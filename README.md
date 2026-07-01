<div align="center">

# 🩺 Diabetes Prediction AI System

### AI-powered full-stack health risk prediction platform

Predict diabetes risk in real time using **XGBoost**, track your health history, and download personalized AI-generated reports — all wrapped in a secure, full-stack web app.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![XGBoost](https://img.shields.io/badge/XGBoost-ML%20Model-EC6E00?style=flat)](https://xgboost.readthedocs.io/)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📖 Overview

**Diabetes Prediction AI System** is a full-stack web application that uses a trained **XGBoost machine learning model** to assess a user's risk of diabetes based on key clinical indicators. Beyond just a prediction, it offers a complete health-tracking experience — secure accounts, a history of past assessments, visual risk analytics, downloadable PDF reports, and health reminders.

> ⚠️ **Disclaimer:** This tool is for educational and informational purposes only. It is **not** a substitute for professional medical diagnosis. Always consult a licensed healthcare provider.

---

## ✨ Key Features

| | |
|---|---|
| 🔐 **Secure Authentication** | JWT-based login/signup with bcrypt password hashing |
| 🤖 **AI-Powered Prediction** | XGBoost model trained on 8 clinical features |
| 📊 **Visual Health Analytics** | Risk probability pie chart & health radar chart |
| 🧾 **Smart Recommendations** | Personalized, risk-level-based health guidance |
| 🕓 **Prediction History** | Search, filter, and sort past assessments |
| 📄 **Downloadable PDF Reports** | Professional, shareable health risk reports |
| ⏰ **Health Reminders** | Schedule and manage personal reminders |
| 📈 **Live Dashboard Stats** | Personal & platform-wide prediction analytics |

---

## 📸 Screenshots

<div align="center">

| Home Page |
|---|---|
| ![Home Page](diabetes-ai-system/pictures/home%20page.png) |

| Home Page |
|---|---|
| ![Total count](pictures/.png) |

| Prediction Form | Dashboard |
|---|---|
| ![Prediction Form](pictures/predict.png) | ![Dashboard](pictures/dashboard.png) |

| Prediction History | PDF Report |
|---|---|
| ![History](pictures/history.png) | ![Report](pictures/report.png) |

</div>

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology |
|---|---|
| **Backend** | FastAPI (Python) |
| **Database** | MySQL + SQLAlchemy ORM |
| **Machine Learning** | XGBoost, scikit-learn, NumPy, Pandas |
| **Authentication** | JWT (python-jose) + Passlib/Bcrypt |
| **Reports** | ReportLab + Matplotlib |
| **Frontend** | HTML5, CSS3, JavaScript |

</div>

---

## 🧠 How Prediction Works

The model takes in **8 clinical inputs** (based on the Pima Indians Diabetes dataset structure):

`Pregnancies` · `Glucose` · `Blood Pressure` · `Skin Thickness` · `Insulin` · `BMI` · `Diabetes Pedigree Function` · `Age`

It returns:
- **Prediction:** Diabetic / Non-Diabetic
- **Probability score** (0–100%)
- **Risk level:** 🟢 Low (<33%) · 🟡 Moderate (33–66%) · 🔴 High (≥66%)
- **Personalized recommendations** based on individual risk factors

---

## 📁 Project Structure

```
Diabetes-Prediction-with-AI/
├── backend/
│   ├── main.py              # FastAPI app & API routes
│   ├── auth.py               # JWT auth & password hashing
│   ├── config.py             # Environment-based settings
│   ├── database.py           # SQLAlchemy engine/session
│   ├── models.py             # ORM models
│   ├── schemas.py            # Pydantic request/response schemas
│   ├── ml_model.py           # Model loading & prediction logic
│   ├── pdf_report.py         # PDF report generation
│   ├── schema.sql            # MySQL schema
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example          # Environment variable template
│   └── model/
│       └── diabetes_best_model.pkl
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
└── README.md
```

---

## 🚀 Getting Started

### 1️⃣ Clone the repository
```bash
git clone https://github.com/Khyathi-Priya/Diabetes-Prediction-with-AI.git
cd Diabetes-Prediction-with-AI/backend
```

### 2️⃣ Set up a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure environment variables
```bash
cp .env.example .env
```
Then edit `.env`:
```env
DATABASE_URL=mysql+pymysql://root:<password>@localhost:3306/diabetes_ai_db
JWT_SECRET_KEY=<your-secret-key>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
MODEL_PATH=model/diabetes_best_model.pkl
ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

### 5️⃣ Set up the database
```bash
mysql -u root -p < schema.sql
```
*(Tables are also auto-created on server startup if they don't exist.)*

### 6️⃣ Add the trained model
Place your trained model file at:
```
backend/model/diabetes_best_model.pkl
```

### 7️⃣ Run the server
```bash
uvicorn main:app --reload --port 8000
```

Visit **`http://localhost:8000`** to use the app, and **`http://localhost:8000/docs`** for interactive Swagger API docs. 🎉

---

## 🔌 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/signup` | `POST` | Register a new user |
| `/api/auth/signin` | `POST` | Log in and receive a JWT token |
| `/api/auth/me` | `GET` | Get current authenticated user |
| `/api/predict` | `POST` | Get an AI diabetes risk prediction |
| `/api/stats` | `GET` | Personal dashboard statistics |
| `/api/stats/platform` | `GET` | Public platform-wide statistics |
| `/api/history` | `GET` | List prediction history (search/sort/filter) |
| `/api/history/{id}` | `DELETE` | Delete a prediction record |
| `/api/report/{id}/pdf` | `GET` | Download a prediction as a PDF report |
| `/api/reminders` | `GET`/`POST` | List or create health reminders |
| `/api/reminders/{id}` | `DELETE` | Delete a reminder |
| `/api/health` | `GET` | Server health check |

---

## 📄 Sample Report

Every prediction can be exported as a polished PDF report featuring:
- Patient details & prediction summary
- Risk probability pie chart
- Health radar chart across key metrics
- Personalized AI health recommendations

---

## 🗺️ Roadmap

- [ ] Email notifications for reminders
- [ ] Mobile-responsive UI enhancements
- [ ] Multi-language support
- [ ] Model retraining pipeline with new patient data

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**Built with ❤️ by [Khyathi Priya](https://github.com/Khyathi-Priya)**

</div>
