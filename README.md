# 🛡️ PhishGuard – Phishing URL Detection System

**An Intelligent Web-Based Phishing URL Detection Application Using Machine Learning**

PhishGuard is a web application designed to identify potentially malicious and phishing URLs. It combines Machine Learning, URL feature extraction, heuristic analysis, dataset lookup, trusted-domain verification, and Google Safe Browsing to analyze suspicious links.

The application provides a risk score, detection verdict, individual scoring components, and a detailed explanation to help users understand the potential risks associated with a URL.

---

## 👨‍💻 Project Information

| Detail | Information |
|---|---|
| Project Name | PhishGuard |
| Project Type | Web-Based Machine Learning Application |
| Domain | Cybersecurity and Machine Learning |
| Author | Sallavuddin |
| Degree | B.Tech – Computer Science Engineering (Data Science) |
| College | Rajiv Gandhi Memorial College of Engineering and Technology |
| Location | Nandyal, Andhra Pradesh, India |

---

# 1. Introduction

Phishing is a cyberattack in which attackers create deceptive websites or links to trick users into revealing sensitive information such as usernames, passwords, banking details, and personal information.

These websites often imitate legitimate websites and use misleading domain names, suspicious URL structures, and fake login pages.

Manually identifying phishing URLs can be difficult.

PhishGuard addresses this problem by analyzing URLs using machine-learning techniques and multiple security checks.

Users can submit a URL, and the application analyzes its characteristics to estimate whether it is SAFE, SUSPICIOUS, or PHISHING.

# 2. Objectives

The main objectives of PhishGuard are:

1. Detect potentially malicious and phishing URLs.
2. Use machine learning to estimate phishing probability.
3. Analyze URL characteristics using feature extraction.
4. Identify suspicious patterns through heuristic rules.
5. Integrate Google Safe Browsing for external threat information.
6. Provide understandable explanations for detection results.
7. Calculate separate risk scores for different detection methods.
8. Maintain scan history and provide dashboard information.
9. Provide a simple interface for users to analyze URLs.

# 3. Key Features

### 3.1 User Authentication
- User registration.
- Email verification using OTP.
- User login.
- Forgot password.
- Password reset.
- Protected user access.

### 3.2 URL Detection
- Submit URLs for scanning.
- Analyze URL characteristics.
- Machine-learning prediction.
- Rule-based detection.
- Dataset lookup.
- Trusted-domain verification.
- Google Safe Browsing integration.

### 3.3 Risk Analysis
- ML Probability Score.
- Heuristic Score.
- URL Feature Score.
- Calculated Risk Score.
- Final Risk Score.
- Detection explanations.

### 3.4 Dashboard
- Total scans.
- SAFE results.
- SUSPICIOUS results.
- PHISHING results.
- Scan statistics.

### 3.5 Scan History
- View previous scans.
- Search scanned URLs.
- Filter results by verdict.
- View scan details.
- Delete scan records.

### 3.6 Admin Features
- Total user information.
- Total scan statistics.
- User list.
- Administrative access control.

---

# 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | Backend API development |
| React.js | Frontend development |
| Vite | Frontend development server and build tool |
| Tailwind CSS | UI styling |
| JavaScript | Frontend functionality |
| Random Forest | Machine-learning algorithm |
| Scikit-learn | Machine-learning implementation |
| Pandas | Dataset processing |
| NumPy | Numerical operations |
| SQLite | Database |
| SQLAlchemy | Database management |
| JWT | Authentication |
| Google Safe Browsing API | External threat checking |
| Git and GitHub | Version control and project hosting |

---

# 5. Machine Learning Model

PhishGuard uses a Random Forest classification model to estimate the probability that a URL belongs to the phishing class.

### Why Random Forest?

Random Forest is an ensemble machine-learning algorithm that combines multiple decision trees to make predictions.

It is useful for classification problems because it can learn relationships between different URL characteristics.

### Dataset

The project uses the PhiUSIIL Phishing URL Dataset.

The dataset contains phishing and legitimate URL examples with URL-related features.

The model uses URL characteristics to learn patterns associated with phishing and legitimate websites.

### Machine Learning Workflow

1. Dataset collection.
2. Data preprocessing.
3. Feature preparation.
4. Training and testing split.
5. Random Forest model training.
6. Probability calibration.
7. Model evaluation.
8. Model saving.
9. Model integration with the backend.
10. URL prediction.

### Prediction

The trained model produces a phishing probability.

For example:

- 0.90 = 90% estimated phishing probability.
- 0.50 = 50% estimated phishing probability.
- 0.10 = 10% estimated phishing probability.

These probabilities are model estimates, not guarantees of actual website behavior.

---

# 6. URL Detection Methodology

PhishGuard combines five major detection components.

### 6.1 Dataset Lookup

The application checks whether the exact normalized URL exists in the configured dataset lookup.

Possible results:

- `phishing`
- `legitimate`
- `None`

If the URL is recorded as phishing, the result becomes PHISHING with a risk score of at least 90.

If it is recorded as legitimate, the result becomes SAFE and the current risk score is reduced.

### 6.2 Trusted Domain Verification

PhishGuard maintains a list of trusted domains.

Examples:

- google.com
- github.com
- microsoft.com
- amazon.com
- wikipedia.org
- python.org
- youtube.com
- linkedin.com

The system checks whether the hostname exactly matches a trusted domain or is a subdomain of it.

A trusted-domain match changes the result to SAFE and reduces the current risk score.

### 6.3 Google Safe Browsing

Google Safe Browsing checks URLs against Google's available threat information.

Possible statuses:

- `flagged`
- `clear`
- `unavailable`
- `not_configured`

If a URL is flagged, PhishGuard returns PHISHING with a risk score of at least 90.

An unavailable check is never interpreted as a safe result.

### 6.4 Heuristic Detection

Heuristic detection identifies suspicious patterns in URLs.

Examples:

- HTTP instead of HTTPS.
- Multiple hyphens in the domain.
- Suspicious login-related words.
- Excessive subdomains.
- IP address as the hostname.
- Long URLs.
- Deep URL paths.
- Unusual query parameters.

The exact checks are defined in the backend heuristic module.

### 6.5 Machine Learning Prediction

The Random Forest model analyzes URL features and produces a phishing probability.

This probability is combined with the heuristic and URL feature scores to calculate the initial risk score.

---

# 7. Risk Scoring System

PhishGuard calculates three individual scores and combines them into one weighted risk score.

### 7.1 ML Score – 60%

Represents the phishing probability estimated by the Random Forest model.

Formula:

```python
ml_score = ml_probability * 100
```

### 7.2 Heuristic Score – 25%

Represents the percentage of heuristic checks triggered by the submitted URL.

Formula:

```python
heuristic_score = (
    triggered_checks / total_heuristic_checks
) * 100
```

### 7.3 URL Feature Score – 15%

Represents the number of notable URL characteristics identified.

There are nine possible facts in the current feature-facts implementation.

Formula:

```python
feature_score = (
    notable_facts / 9
) * 100
```

### 7.4 Final Weighted Risk Calculation

```python
calculated_risk = round(
    0.60 * ml_score
    + 0.25 * heuristic_score
    + 0.15 * feature_score
)
```

The score is limited to the range 0–100.

### Example

The following values are illustrative:

| Component | Score | Weight |
|---|---:|---:|
| ML Score | 70 | 60% |
| Heuristic Score | 40 | 25% |
| URL Feature Score | 50 | 15% |

Calculation:

```text
ML contribution = 70 × 0.60 = 42

Heuristic contribution = 40 × 0.25 = 10

Feature contribution = 50 × 0.15 = 7.5

Total = 59.5

Calculated Risk Score = 60
```

The application also returns a final risk score after priority overrides.

---

# 8. Verdict Classification

PhishGuard initially classifies URLs according to these risk-score ranges.

| Risk Score | Verdict | Meaning |
|---|---|---|
| 0–29 | SAFE | No strong warning signs from the initial score. |
| 30–59 | SUSPICIOUS | Some warning signs have been detected. |
| 60–100 | PHISHING | High calculated phishing risk. |

### Additional Suspicious Rules

Two additional conditions can change an initial SAFE verdict to SUSPICIOUS:

1. ML phishing probability is greater than or equal to the configured decision threshold.
2. Two or more heuristic checks are triggered.

After these initial verdict checks, priority overrides are applied.

### Detection Priority

1. Google Safe Browsing flagged.
2. Exact dataset match.
3. Trusted-domain match.
4. Clean HTTPS condition.
5. Weighted score and additional suspicious rules.

**Note:** The priority rules can change both the initial verdict and the final risk score.

Every SAFE result includes this safety message:

"Automated URL detection cannot guarantee that a website is safe. Do not enter passwords on unfamiliar sites."

---

# 9. Application Architecture

PhishGuard contains two main application components.

### Frontend

React.js provides the user interface.

It communicates with the backend through HTTP API requests.

Main responsibilities:

- User registration and login.
- URL submission.
- Displaying detection results.
- Showing risk scores.
- Displaying scan history.
- Dashboard information.
- User and admin interfaces.

### Backend

FastAPI handles application logic and API requests.

Main responsibilities:

- User authentication.
- URL normalization.
- Dataset lookup.
- Random Forest prediction.
- Feature extraction.
- Heuristic detection.
- Google Safe Browsing.
- Risk calculation.
- Verdict classification.
- Database operations.

### System Workflow

```text
             USER
               |
               v
        REACT FRONTEND
               |
               v
         FASTAPI BACKEND
               |
       +-------+--------+
       |       |        |
       v       v        v
    DATASET   TRUSTED   GOOGLE
    LOOKUP    DOMAINS   SAFE BROWSING
       |       |        |
       +-------+--------+
               |
               v
       RANDOM FOREST MODEL
               |
               v
       URL FEATURE EXTRACTION
               |
               v
        HEURISTIC CHECKS
               |
               v
        RISK CALCULATION
               |
               v
       VERDICT CLASSIFICATION
               |
               v
        RESULT EXPLANATION
               |
               v
        REACT DASHBOARD
```

---

# 10. Project Folder Structure

```text
PhishGuard/
|
|-- README.md
|-- .gitignore
|-- start-backend.bat
|-- start-frontend.bat
|
|-- backend/
|   |
|   |-- app/
|   |   |-- main.py
|   |   |-- scanner.py
|   |   |-- dataset_lookup.py
|   |   |-- safe_browsing.py
|   |   |-- mail.py
|   |   |-- otp.py
|   |   |-- security.py
|   |   |-- models.py
|   |   |-- database.py
|   |   |-- config.py
|   |   |
|   |   |-- ml/
|   |       |-- train.py
|   |       |-- predictor.py
|   |       |-- features.py
|   |       |-- heuristics.py
|   |       |-- normalize.py
|   |
|   |-- tests/
|   |-- requirements.txt
|
|-- frontend/
    |
    |-- src/
    |   |-- pages/
    |   |-- components/
    |   |-- api.js
    |   |-- App.jsx
    |
    |-- package.json
```

### Important Files

| File | Purpose |
|---|---|
| main.py | FastAPI application and routes |
| scanner.py | Main URL detection and scoring |
| dataset_lookup.py | Dataset matching |
| safe_browsing.py | Google Safe Browsing integration |
| predictor.py | Machine-learning prediction |
| train.py | Model training |
| features.py | URL feature extraction |
| heuristics.py | Rule-based detection |
| normalize.py | URL normalization |
| config.py | Configuration |
| database.py | Database connection |
| models.py | Database models |
| api.js | Frontend API requests |
| App.jsx | React application |

---

# 11. Installation on Another Computer

Follow these instructions to download, install, configure, and run PhishGuard on a new computer.

### System Requirements

Install:

1. Python 3.11 or later.
2. Node.js 18 or later.
3. Git.
4. Required dataset if model training or dataset lookup is needed.
5. Trained ML model, or the ability to train it.

Official downloads:

- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/
- Git: https://git-scm.com/downloads/

Verify installations:

```bash
python --version
node --version
npm --version
git --version
```

### Step 1: Clone the GitHub Repository

Open PowerShell or Command Prompt:

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git

cd YOUR-REPOSITORY
```

Replace the example URL with your actual GitHub repository URL.

You can alternatively download the repository ZIP from GitHub and extract it.

### Step 2: Create the Backend Virtual Environment

```powershell
cd backend

py -3.11 -m venv .venv

.\.venv\Scripts\Activate.ps1
```

If activation is blocked:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\.venv\Scripts\Activate.ps1
```

For Command Prompt:

```bat
cd backend

py -3.11 -m venv .venv

.venv\Scripts\activate.bat
```

### Step 3: Install Backend Dependencies

```bash
python -m pip install --upgrade pip

pip install -r requirements.txt
```

### Step 4: Configure the Environment

Copy `.env.example` to `.env`, if the example file exists.

```powershell
Copy-Item .env.example .env
```

Configure the required environment variables.

Example:

```env
SECRET_KEY=your_random_secret_key

ADMIN_EMAIL=your-admin-email@example.com

GOOGLE_SAFE_BROWSING_API_KEY=

DATASET_PATH=

CORS_ORIGINS=http://localhost:5173
```

Use all additional variables required by your actual configuration.

Never upload `.env` to GitHub.

### Step 5: Obtain the Dataset and Model

The trained model may not be included in the repository.

If the model file is missing:

1. Obtain the PhiUSIIL dataset.
2. Save the CSV file on your computer.
3. Configure the dataset path.
4. Train the model.
5. Confirm the predictor can load the generated model.

### Step 6: Train the Model

From the backend directory:

```powershell
python -m app.ml.train --data "C:\Datasets\PhiUSIIL_Phishing_URL_Dataset.csv"
```

Replace the example path with the actual dataset path.

Check the training output to find the generated model file. It must be stored at the location expected by the predictor.

### Step 7: Install Frontend Dependencies

Open another terminal:

```bash
cd frontend

npm install
```

### Step 8: Start the Backend

In the backend terminal:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

This command assumes the application entry point is `app.main:app`.

### Step 9: Start the Frontend

In the second terminal:

```bash
cd frontend

npm run dev
```

Open the application:

```text
http://localhost:5173
```

Backend API documentation:

```text
http://localhost:8001/docs
```

Keep both terminal windows running.

---

# 12. Running PhishGuard After Installation

You do not need to install dependencies every time.

### Backend – Windows PowerShell

```powershell
cd backend

.\.venv\Scripts\Activate.ps1

python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

### Frontend

Open a second terminal:

```bash
cd frontend

npm run dev
```

Visit:

```text
http://localhost:5173
```

### Linux / macOS Backend

```bash
cd backend

source .venv/bin/activate

python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

The frontend command remains:

```bash
cd frontend

npm run dev
```

---

# 13. Configuration

The backend configuration is stored in `backend/.env`, when the application is configured to load that file.

| Variable | Purpose |
|---|---|
| SECRET_KEY | Authentication and token security |
| ADMIN_EMAIL | Administrator account |
| DATABASE_URL | Database connection |
| MAIL_USERNAME | Email account |
| MAIL_PASSWORD | Email app password |
| GOOGLE_SAFE_BROWSING_API_KEY | External threat checking |
| DATASET_PATH | Dataset location |
| CORS_ORIGINS | Allowed frontend origins |
| ACCESS_TOKEN_MINUTES | Access token lifetime |
| DECISION_THRESHOLD | ML suspicious-verdict threshold |

Use the actual variable names and defaults defined in the current configuration file.

---

# 14. Machine-Learning Model and Dataset

### Dataset

PhishGuard uses the PhiUSIIL Phishing URL Dataset.

The dataset is used to train the model and may also support exact URL lookup, depending on configuration.

### Model Training

Training is performed using:

```bash
python -m app.ml.train --data "PATH_TO_DATASET.csv"
```

The model output location is determined by the training script.

### Model Integration

The prediction module loads the saved model and returns a phishing probability for the normalized URL.

The feature extraction and prediction pipelines must remain compatible with the trained model.

If the model is retrained, evaluate it and verify that the current application can load it.

---

# 15. Using the Application

1. Open PhishGuard in the browser.
2. Register a new account.
3. Verify the email address.
4. Log in.
5. Navigate to the URL scanner.
6. Enter the URL to analyze.
7. Submit the URL.
8. Review the verdict and risk score.
9. Review individual score components.
10. Read the detection explanation.
11. Open scan history to review previous results.
12. View the dashboard for scan statistics.

### Understanding a Scan Result

A scan result can include:

- Submitted URL.
- Normalized URL.
- Detection verdict.
- ML probability.
- Heuristic score.
- Risk score.
- Individual score breakdown.
- External threat status.
- Triggered checks.
- URL features.
- Explanation.
- Safety note.

---

# 16. API Reference

Interactive API documentation is available while the backend is running:

```text
http://localhost:8001/docs
```

The project documentation describes these API routes. Confirm the exact route definitions in the current backend source code.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | /auth/register | Register user |
| POST | /auth/resend-otp | Resend verification code |
| POST | /auth/verify-otp | Verify email |
| POST | /auth/login | User login |
| POST | /auth/forgot-password | Request password reset |
| POST | /auth/reset-password | Reset password |
| GET | /auth/me | Current user |
| POST | /scan | Scan URL |
| GET | /history | Scan history |
| GET | /history/{id} | Scan details |
| DELETE | /history/{id} | Delete scan |
| GET | /dashboard | Dashboard statistics |
| GET | /profile | User profile |
| PUT | /profile | Update profile |
| GET | /admin/stats | Admin statistics |
| GET | /admin/users | Admin users |
| GET | /health | Backend health |

Protected endpoints require:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Example Scan Response

Illustrative response only:

```json
{
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

Actual predictions and response values depend on the configured model, rules, dataset, and external services.

---

# 17. Testing and Evaluation

Run backend tests:

```bash
cd backend

python -m pytest -q
```

If the evaluation module is available:

```bash
python -m app.eval_scanner --data "PATH_TO_DATASET.csv" --n 300
```

Recommended evaluation metrics:

- Accuracy.
- Precision.
- Recall.
- F1-score.
- Confusion matrix.
- False-positive rate.
- False-negative rate.

Evaluate using data that was not used for model training or tuning.

A high training score does not guarantee equivalent performance on new URLs.

### Manual URL Testing

Test a variety of URLs:

- Known legitimate websites.
- Unusual but legitimate URLs.
- URLs with suspicious patterns.
- Labeled phishing URLs from an appropriate test dataset.

Record the actual verdict and all individual scores. Expected test labels are not guaranteed predictions.

---

# 18. Security and Privacy

- Store secrets in environment variables.
- Never commit `.env` files.
- Use HTTPS in production.
- Protect user-specific history and profile endpoints.
- Do not expose passwords, OTPs, or tokens in logs or frontend responses.
- Use secure password-reset and authentication flows.
- Restrict Google API keys to the required service.
- Apply rate limiting to authentication and OTP endpoints.
- Treat submitted URLs as untrusted input.
- Do not automatically open untrusted URLs on the backend without isolation and safeguards.

---

# 19. Limitations and Responsible Use

PhishGuard is a URL-analysis tool and should be treated as a security aid, not a complete security solution.

1. URL text analysis cannot identify every malicious webpage.
2. The scanner may not inspect webpage HTML, forms, scripts, or visual content.
3. Legitimate URLs can contain suspicious-looking patterns.
4. New phishing URLs may not be listed by external threat services.
5. HTTPS does not prove that a website is legitimate.
6. Trusted-domain lists require regular maintenance.
7. Dataset labels may contain errors or outdated information.
8. Model predictions are estimates and can be incorrect.

Always verify unfamiliar websites using their official website or trusted communication channel.

---

# 20. Troubleshooting

| Problem | Solution |
|---|---|
| Python not recognized | Install Python and configure PATH. |
| Node.js not recognized | Install Node.js and restart the terminal. |
| npm not recognized | Verify Node.js installation. |
| ModuleNotFoundError | Activate the backend virtual environment and install requirements. |
| package.json not found | Run npm commands inside the frontend directory. |
| Model file not found | Train the model and verify its configured path. |
| Dataset not found | Correct DATASET_PATH. |
| Backend connection failed | Confirm the backend is running. |
| Port already in use | Stop the other process or change the configured port. |
| Email verification failed | Check email settings and development logs. |
| Safe Browsing unavailable | Check API configuration, quota, and connectivity. |
| Same score for every URL | Verify the prediction pipeline and model input. |

---

# 21. Future Improvements

Potential future improvements include:

- Browser extension integration.
- Real-time threat intelligence updates.
- Improved model evaluation on unseen domains.
- Additional phishing detection algorithms.
- Improved bulk URL scanning.
- More detailed analytics.
- Improved detection explanations.
- Production deployment and monitoring.
- More comprehensive automated security tests.

These are potential enhancements and should not be interpreted as already implemented features.

---

# 22. Contributing

Contributions and suggestions are welcome.

To contribute:

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Test your changes.
5. Submit a pull request with a clear description.

Please do not commit API keys, passwords, model secrets, or private user data.

---

# 23. License

No license has currently been specified.

A license should be added before allowing external reuse or contributions under defined terms.

---

# 24. Author

**Sallavuddin**

B.Tech – Computer Science Engineering (Data Science)

Rajiv Gandhi Memorial College of Engineering and Technology

Nandyal, Andhra Pradesh, India

---

**PhishGuard – Analyze URLs. Understand Risk. Stay Alert.**

*Automated detection helps identify warning signs, but users should always verify unfamiliar websites independently.*
