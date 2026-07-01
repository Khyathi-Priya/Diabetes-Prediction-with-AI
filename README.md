# 🩺 Diabetes Prediction AI System

An AI-powered web application that predicts diabetes risk using a trained XGBoost machine learning model. Built with **FastAPI** (backend) and a **MySQL** database, it provides user authentication, risk prediction, health history tracking, downloadable PDF reports, and reminders.

## ✨ Features

- 🔐 **User Authentication** — Sign up / sign in with JWT-based auth and bcrypt password hashing
- 🤖 **AI Risk Prediction** — Predicts diabetic risk from 8 clinical inputs (Pregnancies, Glucose, Blood Pressure, Skin Thickness, Insulin, BMI, Diabetes Pedigree Function, Age)
- 📊 **Health Radar & Risk Charts** — Visual breakdown of risk factors
- 📄 **PDF Report Generation** — Downloadable, detailed health risk reports per prediction
- 🕓 **Prediction History** — Search, filter, and sort past predictions
- 📈 **Dashboard Stats** — Personal and platform-wide prediction analytics
- ⏰ **Reminders** — Schedule personal health reminders
- 🧾 **Activity Logging** — Tracks user actions (signup, signin, predictions, downloads)

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Database | MySQL (SQLAlchemy ORM) |
| ML Model | XGBoost (scikit-learn compatible) |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| PDF Reports | ReportLab + Matplotlib |
| Frontend | HTML / CSS / JS (served as static files) |

## 📁 Project Structure

```
diabetes-prediction-ai/
├── backend/
│   ├── main.py            # FastAPI app & API routes
│   ├── auth.py             # JWT auth & password hashing
│   ├── config.py           # App settings (.env driven)
│   ├── database.py         # SQLAlchemy engine/session setup
│   ├── models.py           # ORM models (User, Prediction, Reminder, ActivityLog)
│   ├── schemas.py          # Pydantic request/response schemas
│   ├── ml_model.py         # Model loading & prediction logic
│   ├── pdf_report.py       # PDF report generation
│   ├── schema.sql          # MySQL schema (manual setup option)
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variable template
│   └── model/
│       └── diabetes_best_model.pkl   # Trained model file
├── frontend/
│   └── style.css
└── README.md
```

## ⚙️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/diabetes-prediction-ai.git
cd diabetes-prediction-ai/backend
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

Key variables:
```
DATABASE_URL=mysql+pymysql://root:<password>@localhost:3306/diabetes_ai_db
JWT_SECRET_KEY=<your-secret-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
MODEL_PATH=model/diabetes_best_model.pkl
ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

### 5. Set up the database
Option A — let FastAPI auto-create tables on startup (default), or  
Option B — run the schema manually:
```bash
mysql -u root -p < schema.sql
```

### 6. Add the trained model
Place your trained model at:
```
backend/model/diabetes_best_model.pkl
```
It can be a raw scikit-learn-compatible classifier, or a dict of `{"model": ..., "scaler": ...}`.

### 7. Run the server
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`, and the frontend (if present in `../frontend`) is served automatically at the same address.

## 🔌 API Overview

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/signup` | POST | Register a new user |
| `/api/auth/signin` | POST | Log in and receive a JWT |
| `/api/auth/me` | GET | Get current user info |
| `/api/predict` | POST | Get a diabetes risk prediction |
| `/api/stats` | GET | Personal dashboard stats |
| `/api/stats/platform` | GET | Public platform-wide stats |
| `/api/history` | GET | List past predictions (search/sort/filter) |
| `/api/history/{id}` | DELETE | Delete a prediction record |
| `/api/report/{id}/pdf` | GET | Download a prediction as PDF |
| `/api/reminders` | GET / POST | List / create reminders |
| `/api/reminders/{id}` | DELETE | Delete a reminder |
| `/api/health` | GET | Health check |

Interactive API docs are available at `/docs` (Swagger UI) once the server is running.

## 🧠 Model Details

- **Input features:** Pregnancies, Glucose, Blood Pressure, Skin Thickness, Insulin, BMI, Diabetes Pedigree Function, Age
- **Output:** Binary prediction (Diabetic / Non-Diabetic) with probability score
- **Risk levels:** Low (< 33%), Moderate (33–66%), High (≥ 66%)
- Model trained on data structured like the Pima Indians Diabetes dataset

## 📄 Sample Report

The system generates a downloadable PDF report per prediction, including patient info, input values, risk probability pie chart, health radar chart, and personalized AI recommendations.

## ⚠️ Disclaimer

This application is for **informational and educational purposes only**. It is **not a medical diagnostic tool**. Always consult a licensed healthcare professional for medical advice.

## 📝 License

This project is open source and available under the [MIT License](LICENSE).
