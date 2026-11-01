# PhishGuard

PhishGuard is a web application that analyzes URLs and estimates whether they may lead to phishing pages. Users can create an account, verify their email with a one-time code, scan URLs, review scan history, and view dashboard analytics.

Each scan returns a verdict, a 0–100 risk score, separate scoring components, and a plain-language explanation of detected warning signs.

**Author:** Sallavuddin  
**Education:** B.Tech in Computer Science Engineering (Data Science), Rajiv Gandhi Memorial College of Engineering and Technology, Nandyal, Andhra Pradesh, India

---

## Table of Contents

- Features
- How URL Detection Works
- Scoring System
- Verdict Categories
- Accuracy and Evaluation
- Limitations
- Technology Stack
- Quick Start on Windows
- Configuration
- Training the Model
- Testing
- API Reference
- Project Structure
- Security Notes
- Troubleshooting
- License

---

## 1. Features

- **User Accounts:** Registration, email verification, login, forgot password, and password reset.
- **URL Scanning:** Scan one URL at a time.
- **Multiple Detection Methods:** Dataset lookup, trusted-domain checks, Google Safe Browsing, heuristic rules, and Random Forest model.
- **Risk Breakdown:** Separate ML, heuristic, URL feature, calculated-risk, and final-risk scores.
- **Explanations:** Shows triggered rules, notable URL characteristics, and Google Safe Browsing status.
- **Scan History:** Stores scan results and allows users to review previous scans.
- **Dashboard:** Displays scan totals and verdict summaries.
- **Profile:** Allows users to manage account details and change their password.
- **Admin Features:** Provides administrative statistics and user information to authorized administrators.

## 2. How URL Detection Works

The scanner normalizes the submitted URL, checks the dataset and trusted-domain list, obtains the ML probability, extracts URL features, runs heuristic checks, and calculates a risk score.

The final decision follows this priority order:

1. **Google Safe Browsing Flagged:** If Google Safe Browsing reports a threat, the verdict is PHISHING and the risk score is raised to at least 90.

2. **Exact Dataset Match:** If the exact normalized URL is present in the dataset lookup, its recorded label is used. A phishing label produces PHISHING with a score of at least 90. A legitimate label produces SAFE and scales the current score down.

3. **Trusted Domain:** If the host exactly matches a configured trusted domain or is its subdomain, the verdict becomes SAFE and the current score is multiplied by 0.2.

4. **Clean HTTPS URL:** If the URL uses HTTPS, no heuristic rules fire, and Google Safe Browsing status is clear, the verdict becomes SAFE and the current score is multiplied by 0.3.

5. **Risk Score and Additional Rules:** Otherwise, the weighted risk score and verdict bands are used. Additional rules can change a SAFE result to SUSPICIOUS.

Google Safe Browsing being unavailable or not configured is not treated as a clear result.

### Heuristic Checks

The heuristic checks can identify patterns such as:

- Use of HTTP instead of HTTPS.
- Login- and account-related words in the URL.
- IP address used as the host.
- An unusually high number of subdomains.
- Multiple hyphens in the domain.
- Very long URLs or deep URL paths.
- Many query parameters or encoded characters.
- Brand names used in domains that are not the brand's genuine domain, if that check is implemented.

### Notable URL Facts

The feature-fact analysis can report:

- A raw IP address as the host.
- Three or more subdomains.
- Two or more hyphens in the domain.
- URL length of at least 75 characters.
- Path depth of at least four levels.
- Three or more percent-encoded characters.
- Many query parameters.
- A digit ratio of at least 20%.
- Use of HTTP instead of HTTPS.

These facts are explanatory indicators. They are not proof that a URL is malicious.

## 3. Scoring System

The scanner calculates three component scores, each on a 0–100 scale.

| Component | Weight | Calculation |
|---|---:|---|
| ML Score | 60% | ML phishing probability × 100 |
| Heuristic Score | 25% | Triggered checks ÷ Total heuristic checks × 100 |
| URL Feature Score | 15% | Notable facts ÷ 9 × 100 |

### Weighted Risk Formula

```python
calculated_risk = round(
    0.60 * ml_score
    + 0.25 * heuristic_score
    + 0.15 * feature_score
)
```

The result is clamped to the range 0–100.

### Individual Scores

The API returns:

- `ml_score`
- `heuristic_score`
- `feature_score`
- `calculated_risk_score`
- `final_risk_score`
- Component weights
- Number of triggered rules and total rules
- Number of notable facts and total possible facts

**Important:** `calculated_risk_score` is the weighted score before priority overrides. `final_risk_score` is the score after trusted-domain, dataset, clean-HTTPS, or Safe Browsing overrides. The top-level `risk_score` is the final score.

## 4. Verdict Categories

The initial verdict bands are:

| Risk Score | Verdict |
|---|---|
| 0–29 | SAFE |
| 30–59 | SUSPICIOUS |
| 60–100 | PHISHING |

### Additional Suspicious Rules

- If the initial verdict is SAFE but the ML phishing probability is at or above `DECISION_THRESHOLD`, the verdict becomes SUSPICIOUS.
- If the initial verdict is SAFE but two or more heuristic checks fire, the verdict becomes SUSPICIOUS.

Priority overrides are then applied according to the detection order described above.

Every SAFE result includes a safety note:

> Automated URL detection cannot guarantee that a website is safe. Do not enter passwords on unfamiliar sites.

## 5. Accuracy and Evaluation

Do not describe a training-set score as real-world accuracy.

A fair evaluation should use labeled URLs that were not used to train or tune the model. Where possible, split evaluation data by domain so that the same domain does not appear in both training and test sets.

Use the evaluation command to measure performance on the dataset. Review the generated metrics and report the test split, sample size, and evaluation method when presenting results.

## 6. Limitations

- The scanner analyzes URL text and extracted URL features. Unless a separate page-inspection component is implemented, it does not inspect webpage HTML, forms, scripts, or visual content.
- A long or unusual legitimate URL can receive a higher model probability or heuristic score.
- New phishing URLs may not yet appear in Google Safe Browsing or the training dataset.
- HTTPS encrypts the connection but does not prove that a website is legitimate.
- A trusted-domain list can become outdated and should be maintained carefully.
- A dataset match is only as reliable as the dataset label and URL matching process.
- A SAFE verdict is not a guarantee. Users should verify unfamiliar websites through official channels.

## 7. Technology Stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite or PostgreSQL, PyJWT, scikit-learn, pandas.
- **Frontend:** React, Vite, Tailwind CSS, React Router, Axios, Recharts.
- **Machine Learning:** Random Forest with probability calibration.
- **Security:** Password hashing, one-time verification codes, and JWT access tokens.

Check the actual dependency files for the exact installed versions.

## 8. Quick Start on Windows

### Requirements

- Windows 10 or 11.
- Python 3.11 or later.
- Node.js 18 or later.
- Project source code.
- PhiUSIIL dataset if you want to train the model or enable dataset lookup.

### Start the Application

1. Open a terminal in the project folder.
2. Train the model if the required model file is not already present.
3. Start the backend using `start-backend.bat`, if provided.
4. Open a second terminal and start the frontend using `start-frontend.bat`, if provided.
5. Open the frontend address printed by the development server.
6. Register an account and complete email verification.

Default project addresses:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8001`
- API documentation: `http://localhost:8001/docs`

Confirm the actual ports in your configuration.

## 9. Configuration

Backend settings are read from `backend/.env` when the application is configured to load that file.

| Setting | Purpose |
|---|---|
| `SECRET_KEY` | Secret used to sign tokens and protect authentication-related data. |
| `ADMIN_EMAIL` | Email address assigned administrative access. |
| `DATABASE_URL` | Optional database connection string. |
| `MAIL_USERNAME` | Email account used to send verification messages. |
| `MAIL_PASSWORD` | Email provider app password. |
| `GOOGLE_SAFE_BROWSING_API_KEY` | Enables Google Safe Browsing integration. |
| `DATASET_PATH` | Optional path to the phishing URL dataset. |
| `CORS_ORIGINS` | Allowed frontend origins. |
| `ACCESS_TOKEN_MINUTES` | Access-token lifetime. |
| `DECISION_THRESHOLD` | ML probability threshold used by the suspicious-verdict rule. |

Never commit `.env` files, API keys, passwords, or secret tokens to GitHub.

## 10. Training the Model

The project uses a Random Forest phishing URL model with probability calibration.

From the backend folder, run:

```powershell
cd backend

python -m app.ml.train --data "C:\path\to\PhiUSIIL_Phishing_URL_Dataset.csv"
```

After training:

1. Check that the model file exists.
2. Confirm the predictor loads that exact file.
3. Review training and test metrics.
4. Run scanner tests.
5. Test URLs that were not used during training.

Do not assume that high training accuracy means the model will achieve the same accuracy on new URLs.

## 11. Testing

Run automated backend tests:

```powershell
cd backend

python -m pytest -q
```

If the project includes the scanner evaluation module:

```powershell
python -m app.eval_scanner --data "C:\path\to\PhiUSIIL_Phishing_URL_Dataset.csv" --n 300
```

Track at least:

- Accuracy.
- Precision.
- Recall.
- F1-score.
- Confusion matrix.
- False-positive rate.
- False-negative rate.

Test the individual scoring components as well as the final verdict.

A test URL's expected category is not a guaranteed prediction. Record the actual output from the model and scanner.

## 12. API Reference

When the backend is running, interactive API documentation may be available at:

`http://localhost:8001/docs`

| Method | Path | Purpose |
|---|---|---|
| POST | `/auth/register` | Register a user. |
| POST | `/auth/resend-otp` | Resend verification code. |
| POST | `/auth/verify-otp` | Verify an email address. |
| POST | `/auth/login` | Log in. |
| POST | `/auth/forgot-password` | Request a password reset code. |
| POST | `/auth/reset-password` | Reset a password. |
| GET | `/auth/me` | Get the current user. |
| POST | `/scan` | Scan a URL. |
| GET | `/history` | Retrieve scan history. |
| GET | `/history/{id}` | Retrieve one scan. |
| DELETE | `/history/{id}` | Delete a scan. |
| GET | `/dashboard` | Retrieve dashboard statistics. |
| GET | `/profile` | Retrieve profile information. |
| PUT | `/profile` | Update profile or password, according to implementation. |
| GET | `/admin/stats` | Retrieve admin statistics. |
| GET | `/admin/users` | Retrieve admin user list. |
| GET | `/health` | Check backend health. |

Protected endpoints require an authorization header:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Example Scan Response

The following is an illustrative response shape, not a live prediction:

```json
{
  "submitted_url": "http://example.test/login",
  "normalized_url": "http://example.test/login",
  "verdict": "SUSPICIOUS",
  "ml_probability": 0.42,
  "heuristic_score": 25.0,
  "risk_score": 38,
  "scores": {
    "ml_score": 42.0,
    "heuristic_score": 25.0,
    "feature_score": 55.56,
    "calculated_risk_score": 38,
    "final_risk_score": 38
  },
  "external_status": "unavailable",
  "external_threats": [],
  "triggered_checks": [],
  "features": {},
  "explanation": "Example explanation.",
  "safety_note": null
}
```

Actual values depend on the model, rules, features, dataset, and external check result.

## 13. Project Structure

The following is the structure described by the project documentation. Your actual repository may contain additional files or slightly different names.

```text
PhishGuard/
├── README.md
├── .gitignore
├── start-backend.bat
├── start-frontend.bat
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── scanner.py
│   │   ├── dataset_lookup.py
│   │   ├── safe_browsing.py
│   │   ├── mail.py
│   │   ├── otp.py
│   │   ├── security.py
│   │   ├── models.py
│   │   ├── database.py
│   │   ├── config.py
│   │   └── ml/
│   │       ├── train.py
│   │       ├── predictor.py
│   │       ├── features.py
│   │       ├── heuristics.py
│   │       └── normalize.py
│   ├── tests/
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── pages/
    │   ├── components/
    │   ├── api.js
    │   └── App.jsx
    └── package.json
```

## 14. Security Notes

- Use strong, unique secrets and keep them outside source control.
- Use an email provider app password where required.
- Restrict API keys to the required service and rotate exposed keys.
- Use HTTPS in production.
- Apply authorization checks to every user-specific history and profile operation.
- Do not expose OTPs, passwords, tokens, or secret configuration in frontend responses or logs.
- Apply rate limiting to login, OTP, and password-reset endpoints before production deployment.
- Treat external URL data as untrusted input. Do not automatically open submitted URLs on the server without appropriate isolation and safeguards.

## 15. Troubleshooting

| Problem | What to Check |
|---|---|
| Address already in use | Stop the other process using the backend or frontend port. |
| Browser cannot reach backend | Start the backend and confirm its URL and port. |
| Model file not found | Train the model and verify the predictor's configured model path. |
| Model loading or feature mismatch | Confirm the model and current feature extraction pipeline match. |
| Verification email not received | Check mail configuration, spam, and development logs. |
| Every URL returns the same score | Check whether different normalized URLs produce different model probabilities. Restart the backend after code changes. |
| Google Safe Browsing unavailable | Check API key, API enablement, network access, quota, and service response. |
| Dataset lookup always returns no match | Check `DATASET_PATH`, URL normalization, dataset columns, and label mapping. |

## 16. License

No license has been specified. Add a license before accepting external contributions.

---

## Author

**Sallavuddin**  
B.Tech in Computer Science Engineering (Data Science)  
Rajiv Gandhi Memorial College of Engineering and Technology  
Nandyal, Andhra Pradesh, India
