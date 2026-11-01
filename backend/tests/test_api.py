"""API tests. Scan tests use a tiny throwaway model that only checks plumbing, not accuracy.
Email is captured in memory so tests can read the one-time codes."""
import joblib
import numpy as np
import pytest
from fastapi.testclient import TestClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from app import config, mail, safe_browsing
from app.database import Base, engine
from app.main import app
from app.ml import predictor
from app.ml.features import FEATURE_NAMES


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sent(monkeypatch):
    """Capture every email. The code is the 6 digits at the end of the body line."""
    outbox = {}

    def fake_send(to, subject, body):
        code = body.split(": ")[1].split("\n")[0].strip()
        outbox[to] = code
        return "terminal"

    monkeypatch.setattr(mail, "send_email", fake_send)
    return outbox


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def test_model(tmp_path, monkeypatch):
    rng = np.random.default_rng(0)
    X = rng.random((200, len(FEATURE_NAMES)))
    y = (X[:, 0] > 0.5).astype(int)
    forest = RandomForestClassifier(n_estimators=10, random_state=0).fit(X, y)
    cal = LogisticRegression().fit(forest.predict_proba(X)[:, 1].reshape(-1, 1), y)
    path = tmp_path / "test_model.joblib"
    joblib.dump({"forest": forest, "calibrator": cal, "feature_names": FEATURE_NAMES, "threshold": 0.5}, path)
    monkeypatch.setattr(config, "MODEL_PATH", path)
    predictor.clear_model_cache()
    yield path
    predictor.clear_model_cache()


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def signup(client, sent, email="user@example.com", password="password123"):
    """Register, then verify with the emailed code. Returns the access token."""
    assert client.post("/auth/register", json={"email": email, "password": password}).status_code == 201
    r = client.post("/auth/verify-otp", json={"email": email, "code": sent[email]})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def test_register_requires_verification_before_login(client, sent):
    client.post("/auth/register", json={"email": "user@example.com", "password": "password123"})
    assert "user@example.com" in sent
    blocked = client.post("/auth/login", json={"email": "user@example.com", "password": "password123"})
    assert blocked.status_code == 403


def test_wrong_code_then_correct_code(client, sent):
    client.post("/auth/register", json={"email": "user@example.com", "password": "password123"})
    wrong = "000000" if sent["user@example.com"] != "000000" else "111111"
    bad = client.post("/auth/verify-otp", json={"email": "user@example.com", "code": wrong})
    assert bad.status_code == 400
    ok = client.post("/auth/verify-otp", json={"email": "user@example.com", "code": sent["user@example.com"]})
    assert ok.status_code == 200
    login = client.post("/auth/login", json={"email": "user@example.com", "password": "password123"})
    assert login.status_code == 200


def test_code_locks_after_max_attempts(client, sent):
    client.post("/auth/register", json={"email": "user@example.com", "password": "password123"})
    real = sent["user@example.com"]
    wrong = "000000" if real != "000000" else "111111"
    for _ in range(config.OTP_MAX_ATTEMPTS):
        client.post("/auth/verify-otp", json={"email": "user@example.com", "code": wrong})
    # After the lock, even the right code fails until a new one is requested.
    locked = client.post("/auth/verify-otp", json={"email": "user@example.com", "code": real})
    assert locked.status_code == 400


def test_stored_code_is_hashed_not_plain(client, sent):
    from app.database import SessionLocal
    from app.models import User

    client.post("/auth/register", json={"email": "user@example.com", "password": "password123"})
    db = SessionLocal()
    user = db.query(User).filter(User.email == "user@example.com").one()
    assert user.otp_hash and sent["user@example.com"] not in user.otp_hash
    assert "password123" not in user.password_hash
    db.close()


def test_forgot_and_reset_password(client, sent):
    signup(client, sent)
    generic = client.post("/auth/forgot-password", json={"email": "nobody@example.com"})
    assert generic.status_code == 200 and "nobody@example.com" not in sent

    client.post("/auth/forgot-password", json={"email": "user@example.com"})
    reset = client.post(
        "/auth/reset-password",
        json={"email": "user@example.com", "code": sent["user@example.com"], "new_password": "brandnew123"},
    )
    assert reset.status_code == 200
    assert client.post("/auth/login", json={"email": "user@example.com", "password": "password123"}).status_code == 401
    assert client.post("/auth/login", json={"email": "user@example.com", "password": "brandnew123"}).status_code == 200


def test_verify_code_cannot_be_used_as_reset_code(client, sent):
    client.post("/auth/register", json={"email": "user@example.com", "password": "password123"})
    code = sent["user@example.com"]
    r = client.post("/auth/reset-password", json={"email": "user@example.com", "code": code, "new_password": "brandnew123"})
    assert r.status_code == 400


def test_duplicate_email_rejected(client, sent):
    signup(client, sent)
    assert client.post("/auth/register", json={"email": "user@example.com", "password": "password123"}).status_code == 409


def test_admin_role_granted_by_admin_email(client, sent):
    token = signup(client, sent, email="admin@example.com")
    assert client.get("/auth/me", headers=auth(token)).json()["role"] == "admin"


def test_protected_routes_need_token(client):
    assert client.get("/history").status_code == 401
    assert client.post("/scan", json={"url": "example.com"}).status_code == 401
    assert client.get("/auth/me", headers=auth("not-a-real-token")).status_code == 401


def test_scan_without_model_gives_clear_error(client, sent, monkeypatch, tmp_path):
    token = signup(client, sent)
    monkeypatch.setattr(config, "MODEL_PATH", tmp_path / "missing.joblib")
    predictor.clear_model_cache()
    r = client.post("/scan", json={"url": "example.com"}, headers=auth(token))
    assert r.status_code == 503
    assert "not found" in r.json()["detail"]


def test_scan_saves_and_returns_result(client, sent, test_model):
    token = signup(client, sent)
    r = client.post("/scan", json={"url": "https://example.com/login"}, headers=auth(token))
    assert r.status_code == 201
    body = r.json()
    assert body["verdict"] in ("SAFE", "SUSPICIOUS", "PHISHING")
    assert 0 <= body["risk_score"] <= 100
    assert body["normalized_url"] == "https://example.com/login"
    assert set(body["features"]) == set(FEATURE_NAMES)
    assert body["external_status"] == "not_configured"
    assert len(client.get("/history", headers=auth(token)).json()) == 1


def test_safe_browsing_flag_forces_phishing(client, sent, test_model, monkeypatch):
    token = signup(client, sent)
    monkeypatch.setattr(safe_browsing, "check_url", lambda url: {"status": "flagged", "threats": ["SOCIAL_ENGINEERING"]})
    body = client.post("/scan", json={"url": "example.com"}, headers=auth(token)).json()
    assert body["verdict"] == "PHISHING" and body["risk_score"] >= 90
    assert body["external_status"] == "flagged"


def test_safe_browsing_unavailable_is_not_called_safe(client, sent, test_model, monkeypatch):
    token = signup(client, sent)
    monkeypatch.setattr(safe_browsing, "check_url", lambda url: {"status": "unavailable", "threats": []})
    body = client.post("/scan", json={"url": "example.com"}, headers=auth(token)).json()
    assert body["external_status"] == "unavailable"
    assert "unavailable" in body["explanation"]


def test_invalid_url_rejected(client, sent, test_model):
    token = signup(client, sent)
    assert client.post("/scan", json={"url": "ftp://example.com"}, headers=auth(token)).status_code == 422


def test_users_cannot_see_or_delete_each_others_scans(client, sent, test_model):
    a = signup(client, sent, email="a@example.com")
    b = signup(client, sent, email="b@example.com")
    scan_id = client.post("/scan", json={"url": "example.com"}, headers=auth(a)).json()["id"]
    assert client.get(f"/history/{scan_id}", headers=auth(b)).status_code == 404
    assert client.delete(f"/history/{scan_id}", headers=auth(b)).status_code == 404
    assert client.get("/history", headers=auth(b)).json() == []
    assert client.get(f"/history/{scan_id}", headers=auth(a)).status_code == 200
    assert client.delete(f"/history/{scan_id}", headers=auth(a)).status_code == 204
    assert client.get(f"/history/{scan_id}", headers=auth(a)).status_code == 404


def test_history_filter_and_search(client, sent, test_model):
    token = signup(client, sent)
    client.post("/scan", json={"url": "example.com/alpha"}, headers=auth(token))
    client.post("/scan", json={"url": "example.org/beta"}, headers=auth(token))
    assert len(client.get("/history?q=alpha", headers=auth(token)).json()) == 1
    assert client.get("/history?verdict=BOGUS", headers=auth(token)).status_code == 422


def test_analytics_empty_then_counts(client, sent, test_model):
    token = signup(client, sent)
    empty = client.get("/dashboard", headers=auth(token)).json()
    assert empty["is_empty"] is True and empty["total_scans"] == 0
    client.post("/scan", json={"url": "example.com"}, headers=auth(token))
    stats = client.get("/dashboard", headers=auth(token)).json()
    assert stats["total_scans"] == 1 and sum(stats["counts"].values()) == 1


def test_profile_password_change(client, sent):
    token = signup(client, sent)
    bad = client.put("/profile", json={"current_password": "wrongpass1", "new_password": "newpassword1"}, headers=auth(token))
    assert bad.status_code == 400
    ok = client.put("/profile", json={"current_password": "password123", "new_password": "newpassword1"}, headers=auth(token))
    assert ok.status_code == 200
    assert client.post("/auth/login", json={"email": "user@example.com", "password": "newpassword1"}).status_code == 200


def test_admin_endpoints_blocked_for_normal_users(client, sent):
    token = signup(client, sent)
    assert client.get("/admin/stats", headers=auth(token)).status_code == 403
    assert client.get("/admin/users", headers=auth(token)).status_code == 403
    assert client.get("/admin/stats").status_code == 401


def test_admin_sees_totals(client, sent, test_model):
    admin = signup(client, sent, email="admin@example.com")
    user = signup(client, sent, email="u@example.com")
    client.post("/scan", json={"url": "example.com"}, headers=auth(user))
    stats = client.get("/admin/stats", headers=auth(admin)).json()
    assert stats["total_users"] == 2 and stats["total_scans"] == 1
    users = client.get("/admin/users", headers=auth(admin)).json()
    assert {u["email"] for u in users} == {"admin@example.com", "u@example.com"}


def test_root_and_health(client):
    assert client.get("/").json()["docs"] == "/docs"
    assert client.get("/health").json() == {"status": "ok"}
