"""One-time codes for email verification and password reset.

- Codes are 6 digits, random, and expire after OTP_TTL_MINUTES.
- Only an HMAC hash of the code is stored, keyed with the server secret.
- A code is bound to its purpose and email, so a reset code cannot verify an account.
- After OTP_MAX_ATTEMPTS wrong guesses, the code is cleared and a new one must be requested.
"""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from app import config
from app.models import User

PURPOSE_VERIFY = "verify"
PURPOSE_RESET = "reset"


def _key() -> bytes:
    if not config.JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY is not set. Put it in backend/.env.")
    return config.JWT_SECRET_KEY.encode("utf-8")


def _hash(code: str, purpose: str, email: str) -> str:
    message = f"{purpose}:{email}:{code}".encode("utf-8")
    return hmac.new(_key(), message, hashlib.sha256).hexdigest()


def issue_code(user: User, purpose: str) -> str:
    """Create a new code, store its hash on the user, and return the plain code for sending."""
    code = f"{secrets.randbelow(1_000_000):06d}"
    user.otp_hash = _hash(code, purpose, user.email)
    user.otp_purpose = purpose
    user.otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=config.OTP_TTL_MINUTES)
    user.otp_attempts = 0
    return code


def _clear(user: User) -> None:
    user.otp_hash = None
    user.otp_purpose = None
    user.otp_expires_at = None
    user.otp_attempts = 0


def check_code(user: User, purpose: str, code: str) -> str | None:
    """Return None if the code is valid. Otherwise return a short reason shown to the user."""
    if not user.otp_hash or user.otp_purpose != purpose:
        return "No active code. Please request a new one."
    expires = user.otp_expires_at
    if expires is not None and expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires is None or datetime.now(timezone.utc) > expires:
        _clear(user)
        return "This code has expired. Please request a new one."
    if user.otp_attempts >= config.OTP_MAX_ATTEMPTS:
        _clear(user)
        return "Too many wrong attempts. Please request a new code."
    if not hmac.compare_digest(_hash(code.strip(), purpose, user.email), user.otp_hash):
        user.otp_attempts += 1
        if user.otp_attempts >= config.OTP_MAX_ATTEMPTS:
            _clear(user)
            return "Too many wrong attempts. Please request a new code."
        return "Wrong code."
    _clear(user)
    return None
