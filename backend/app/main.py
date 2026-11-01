import json
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import config, mail, otp, safe_browsing
from app.database import get_db, init_db
from app.ml.normalize import InvalidURLError, normalize_url
from app.ml.predictor import ModelMismatchError, ModelNotFoundError
from app.models import Scan, User
from app.schemas import (
    EmailOnlyIn,
    LoginIn,
    ProfileUpdateIn,
    RegisterIn,
    ResetIn,
    ScanDetailOut,
    ScanIn,
    ScanOut,
    TokenOut,
    UserOut,
    VerifyIn,
)
from app.scanner import features_to_json, scan_url, triggered_to_json
from app.security import (
    create_access_token,
    get_current_user,
    hash_password,
    require_admin,
    verify_password,
)

VERDICTS = ("SAFE", "SUSPICIOUS", "PHISHING")
DETECTION_METHOD = "Random Forest model (calibrated) + rule-based checks + trusted-domain list + Google Safe Browsing (if configured)"
SAFETY_NOTE = "Automated URL detection cannot guarantee that a website is safe. Do not enter passwords on unfamiliar sites."


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()  # creates missing tables only; existing data is kept
    yield


app = FastAPI(title="PhishGuard API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"name": "PhishGuard API", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health():
    return {"status": "ok"}


def _send_code(user: User, purpose: str, db: Session) -> dict:
    code = otp.issue_code(user, purpose)
    db.commit()
    subject = "Your PhishGuard verification code" if purpose == otp.PURPOSE_VERIFY else "Your PhishGuard password reset code"
    try:
        delivery = mail.send_email(user.email, subject, mail.code_email_body(code, purpose))
    except mail.MailError as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e))
    return {"delivery": delivery}


def _token_response(user: User) -> dict:
    return {"access_token": create_access_token(user), "token_type": "bearer", "user": UserOut.model_validate(user)}


# ---------- Auth ----------

@app.post("/auth/register", status_code=201)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    email = body.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists.")
    role = "admin" if config.ADMIN_EMAIL and email == config.ADMIN_EMAIL else "user"
    user = User(email=email, password_hash=hash_password(body.password), role=role, email_verified=False)
    db.add(user)
    db.commit()
    db.refresh(user)
    sent = _send_code(user, otp.PURPOSE_VERIFY, db)
    return {"email": user.email, "verification_required": True, **sent}


@app.post("/auth/resend-otp")
def resend_verification(body: EmailOnlyIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if user and not user.email_verified:
        _send_code(user, otp.PURPOSE_VERIFY, db)
    return {"message": "If this account needs verification, a new code has been sent."}


@app.post("/auth/verify-otp", response_model=TokenOut)
def verify_email(body: VerifyIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if user is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid code.")
    if user.email_verified:
        return _token_response(user)
    problem = otp.check_code(user, otp.PURPOSE_VERIFY, body.code)
    if problem:
        db.commit()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, problem)
    user.email_verified = True
    db.commit()
    db.refresh(user)
    return _token_response(user)


@app.post("/auth/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong email or password.")
    if not user.email_verified:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Please verify your email first. Check your inbox for the code.")
    return _token_response(user)


@app.post("/auth/forgot-password")
def forgot_password(body: EmailOnlyIn, db: Session = Depends(get_db)):
    # Same reply whether or not the account exists, so people cannot discover which emails are registered.
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if user is not None:
        _send_code(user, otp.PURPOSE_RESET, db)
    return {"message": "If an account exists for this email, a reset code has been sent."}


@app.post("/auth/reset-password")
def reset_password(body: ResetIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if user is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired code.")
    problem = otp.check_code(user, otp.PURPOSE_RESET, body.code)
    if problem:
        db.commit()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, problem)
    user.password_hash = hash_password(body.new_password)
    db.commit()
    return {"message": "Password reset. You can log in with your new password."}


@app.get("/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


# ---------- Scanning ----------

@app.post("/scan", response_model=ScanDetailOut, status_code=201)
def create_scan(body: ScanIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        normalized = normalize_url(body.url)
        external = safe_browsing.check_url(normalized)
        result = scan_url(body.url, external=external)
    except InvalidURLError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e))
    except (ModelNotFoundError, ModelMismatchError) as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e))

    scan = Scan(
        user_id=user.id,
        submitted_url=result["submitted_url"],
        normalized_url=result["normalized_url"],
        ml_probability=result["ml_probability"],
        heuristic_score=result["heuristic_score"],
        risk_score=result["risk_score"],
        verdict=result["verdict"],
        external_status=result["external_status"],
        features_json=features_to_json(result["features"]),
        triggered_checks_json=triggered_to_json(result["triggered_checks"]),
        explanation=result["explanation"],
        created_at=datetime.now(timezone.utc),
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return _detail(scan)


def _detail(scan: Scan) -> dict:
    return {
        "id": scan.id,
        "submitted_url": scan.submitted_url,
        "normalized_url": scan.normalized_url,
        "ml_probability": scan.ml_probability,
        "heuristic_score": scan.heuristic_score,
        "risk_score": scan.risk_score,
        "verdict": scan.verdict,
        "external_status": scan.external_status,
        "explanation": scan.explanation,
        "created_at": scan.created_at,
        "features": json.loads(scan.features_json),
        "triggered_checks": json.loads(scan.triggered_checks_json),
        "detection_method": DETECTION_METHOD,
        "safety_note": SAFETY_NOTE,
    }


def _own_scan(db: Session, user: User, scan_id: int) -> Scan:
    # Always filter by user_id so one user can never read another user's scan.
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == user.id).first()
    if scan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Scan not found.")
    return scan


@app.get("/history", response_model=list[ScanOut])
def history(
    q: str | None = Query(default=None, max_length=200),
    verdict: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Scan).filter(Scan.user_id == user.id)
    if verdict:
        if verdict not in VERDICTS:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "verdict must be SAFE, SUSPICIOUS or PHISHING.")
        query = query.filter(Scan.verdict == verdict)
    if q:
        query = query.filter(Scan.submitted_url.contains(q))
    return query.order_by(Scan.created_at.desc()).limit(500).all()


@app.get("/history/{scan_id}", response_model=ScanDetailOut)
def history_detail(scan_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _detail(_own_scan(db, user, scan_id))


@app.delete("/history/{scan_id}", status_code=204)
def history_delete(scan_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    scan = _own_scan(db, user, scan_id)
    db.delete(scan)
    db.commit()
    return Response(status_code=204)


# ---------- Dashboard (current user's own data) ----------

@app.get("/dashboard")
def dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Scan.verdict, func.count(Scan.id)).filter(Scan.user_id == user.id).group_by(Scan.verdict).all()
    counts = {v: 0 for v in VERDICTS}
    for verdict, n in rows:
        counts[verdict] = n
    total = sum(counts.values())
    daily = (
        db.query(func.date(Scan.created_at), func.count(Scan.id))
        .filter(Scan.user_id == user.id)
        .group_by(func.date(Scan.created_at))
        .order_by(func.date(Scan.created_at))
        .all()
    )
    recent = db.query(Scan).filter(Scan.user_id == user.id).order_by(Scan.created_at.desc()).limit(5).all()
    return {
        "user": {"email": user.email, "role": user.role},
        "total_scans": total,
        "counts": counts,
        "detection_percentage": round((counts["PHISHING"] + counts["SUSPICIOUS"]) / total * 100, 1) if total else 0.0,
        "daily": [{"date": str(d), "scans": n} for d, n in daily],
        "recent": [
            {
                "id": s.id,
                "submitted_url": s.submitted_url,
                "verdict": s.verdict,
                "risk_score": s.risk_score,
                "explanation": s.explanation,
                "created_at": s.created_at.isoformat(),
            }
            for s in recent
        ],
        "is_empty": total == 0,
    }


# ---------- Profile ----------

@app.get("/profile", response_model=UserOut)
def get_profile(user: User = Depends(get_current_user)):
    return user


@app.put("/profile", response_model=UserOut)
def update_profile(body: ProfileUpdateIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password is wrong.")
    user.password_hash = hash_password(body.new_password)
    db.commit()
    db.refresh(user)
    return user


# ---------- Admin (role checked on the server) ----------

@app.get("/admin/stats")
def admin_stats(_admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    total_users = db.query(func.count(User.id)).scalar() or 0
    rows = db.query(Scan.verdict, func.count(Scan.id)).group_by(Scan.verdict).all()
    counts = {v: 0 for v in VERDICTS}
    for verdict, n in rows:
        counts[verdict] = n
    return {"total_users": total_users, "total_scans": sum(counts.values()), "counts": counts}


@app.get("/admin/users")
def admin_users(_admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    rows = (
        db.query(User, func.count(Scan.id))
        .outerjoin(Scan, Scan.user_id == User.id)
        .group_by(User.id)
        .order_by(User.created_at.desc())
        .all()
    )
    return [
        {"id": u.id, "email": u.email, "role": u.role, "email_verified": u.email_verified,
         "created_at": u.created_at, "scan_count": n}
        for u, n in rows
    ]