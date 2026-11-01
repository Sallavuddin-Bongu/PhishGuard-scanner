# PhishGuard – AI-Powered Phishing URL Detection

## Run it (Windows)

1. Unzip the folder.
2. Double-click **start-backend.bat**. It creates the Python environment, installs packages, creates `backend\.env` with random secrets, and starts the API on http://localhost:8001. Keep its window open.
3. Double-click **start-frontend.bat**. It installs packages and starts the website on http://localhost:5173. Keep its window open.
4. Open http://localhost:5173 in your browser.

Email verification codes print in the backend window. To send real emails, put your Gmail address and a Gmail App Password in `backend\.env` (`MAIL_USERNAME`, `MAIL_PASSWORD`), then restart the backend.

Useful addresses:
- http://localhost:5173 — the website
- http://localhost:8001/docs — API documentation
- http://localhost:8001/health — should show `{"status":"ok"}`

## ML model

No model is included. Train it once with your dataset (see below). Until then, scans show a "model not found" message and everything else works.

## (Old note)

This package includes a **demo model** trained on **synthetic (generated) URLs** in `backend\model\DEMO_synthetic_urls.csv`, so the website runs out of the box. Its accuracy numbers do not describe real phishing detection.

To replace it with a real model, train on the real PhiUSIIL dataset (this overwrites the demo model):

```
cd backend
.venv\Scripts\activate
python -m app.ml.train --data C:\path\to\PhiUSIIL_Phishing_URL_Dataset.csv
```

This writes `backend\model\phishguard_model.joblib` and `training_report.md`. The report marks the demo model with a warning.

## Features

- Register with email verification, login, forgot and reset password
- Scan URLs with the ML model plus rule checks, and optional Google Safe Browsing (set `GOOGLE_SAFE_BROWSING_API_KEY`)
- Dashboard with statistics, charts, and recent scans
- Scan history with search, filter, view, and delete (own scans only)
- Profile with password change
- Admin page for the email in `ADMIN_EMAIL`

## Scoring

- ML score: calibrated Random Forest probability × 100 (weight 0.8)
- Rule score: triggered checks ÷ total checks × 100 (weight 0.2)
- Google Safe Browsing: if it flags the URL, the verdict is PHISHING
- Bands: 70+ PHISHING, 40–69 SUSPICIOUS, below 40 SAFE

Automated detection cannot guarantee that a site is safe.

## Database

SQLite is used by default (`backend\phishguard.db`). For PostgreSQL, set `DATABASE_URL` to something like `postgresql+psycopg2://user:password@localhost/phishguard`.

If you upgrade from an older version, delete `backend\phishguard.db` first, because the tables changed.
