"""Application settings, read from environment variables (and an optional backend/.env file)."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent  # the backend/ folder
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or SECRET_KEY

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "").strip().lower()
DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{BASE_DIR / 'phishguard.db'}"

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_MINUTES", "60"))

# Email (Gmail: use an App Password, not your normal password).
# If MAIL_USERNAME or MAIL_PASSWORD is empty, codes are printed in the backend terminal instead.
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "").strip()
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "").strip()
MAIL_FROM = os.getenv("MAIL_FROM", "").strip() or MAIL_USERNAME
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

OTP_TTL_MINUTES = int(os.getenv("OTP_TTL_MINUTES", "10"))
OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))

GOOGLE_SAFE_BROWSING_API_KEY = os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "").strip()

MODEL_PATH = Path(os.getenv("MODEL_PATH") or (BASE_DIR / "model" / "phishguard_model.joblib"))

# Optional: path to the PhiUSIIL CSV. If set, a pasted URL that is in this file gets its real label.
DATASET_PATH = os.getenv("DATASET_PATH", "").strip()

# Calibrated ML probability at or above this value counts as phishing for the ML-only label.
DECISION_THRESHOLD = 0.5

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")