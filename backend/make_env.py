"""Creates backend/.env with random secrets. Does nothing if .env already exists."""
import secrets
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent / ".env"

if ENV_FILE.exists():
    print("backend/.env already exists. Leaving it unchanged.")
    raise SystemExit(0)

admin = input("Your email (becomes the admin account, press Enter to skip): ").strip()
text = (
    f"SECRET_KEY={secrets.token_urlsafe(48)}\n"
    f"JWT_SECRET_KEY={secrets.token_urlsafe(48)}\n"
    f"ADMIN_EMAIL={admin}\n"
    "MAIL_USERNAME=\n"
    "MAIL_PASSWORD=\n"
    "GOOGLE_SAFE_BROWSING_API_KEY=\n"
    "DATABASE_URL=\n"
    "MODEL_PATH=\n"
)
ENV_FILE.write_text(text, encoding="utf-8")
print("Created backend/.env with random secrets.")
print("Email codes will print in this terminal unless you fill in MAIL_USERNAME and MAIL_PASSWORD.")
