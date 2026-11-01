"""Sends emails through Gmail SMTP. Falls back to the backend terminal when mail is not configured.

Credentials are never printed or put in error messages.
"""
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr

from app import config

SENDER_NAME = "PhishGuard"


class MailError(RuntimeError):
    """Safe-to-show message. Never includes credentials."""


def send_email(to_address: str, subject: str, body: str) -> str:
    """Return "email" if sent by SMTP, or "terminal" if printed locally for development."""
    if not config.MAIL_USERNAME or not config.MAIL_PASSWORD:
        print(
            "\n[PhishGuard DEV] Mail is not configured, so the message is shown here.\n"
            f"To: {to_address}\nSubject: {subject}\n{body}\n",
            flush=True,
        )
        return "terminal"

    msg = EmailMessage()
    msg["From"] = formataddr((SENDER_NAME, config.MAIL_FROM))
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=15) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
            server.send_message(msg)
    except (smtplib.SMTPException, OSError):
        raise MailError(
            "The email could not be sent. Check MAIL_USERNAME and MAIL_PASSWORD in backend/.env "
            "(for Gmail, use an App Password)."
        ) from None
    return "email"


def code_email_body(code: str, purpose: str) -> str:
    action = "verify your PhishGuard account" if purpose == "verify" else "reset your PhishGuard password"
    return (
        f"Use this code to {action}: {code}\n\n"
        f"It expires in {config.OTP_TTL_MINUTES} minutes. If you did not request it, ignore this email."
    )