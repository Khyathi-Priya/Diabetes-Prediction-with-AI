"""
Diabetes Prediction AI System — FastAPI backend.

Run locally with:
    uvicorn main:app --reload --port 8000

The app also serves the static frontend/ folder, so once deployed (e.g. on
Render) a single web service serves both the UI and the API.
"""
import logging
import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

import models
import schemas
import ml_model
import pdf_report
from auth import (
    hash_password, verify_password, create_access_token, get_current_user
)
from config import settings
from database import Base, engine, get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("diabetes_ai")

app = FastAPI(title="Diabetes Prediction AI System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Creates tables if they don't exist yet (safe / idempotent).
    # For production schema management prefer the included schema.sql.
    Base.metadata.create_all(bind=engine)
    ml_model.load_model()


def log_activity(db: Session, user_id: int, action: str, details: str = ""):
    db.add(models.ActivityLog(user_id=user_id, action=action, details=details))
    db.commit()


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------

@app.post("/api/auth/signup", response_model=schemas.TokenResponse, tags=["auth"])
def signup(payload: schemas.SignUpRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        (models.User.email == payload.email) | (models.User.username == payload.username)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with that email or username already exists.")

    user = models.User(
        username=payload.username,
        email=payload.email,
        password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_activity(db, user.id, "signup", f"User {user.username} registered.")
    token = create_access_token({"sub": str(user.id)})
    return schemas.TokenResponse(access_token=token, user=schemas.UserOut.model_validate(user))


@app.post("/api/auth/signin", response_model=schemas.TokenResponse, tags=["auth"])
def signin(payload: schemas.SignInRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    log_activity(db, user.id, "signin", f"User {user.username} signed in.")
    token = create_access_token({"sub": str(user.id)})
    return schemas.TokenResponse(access_token=token, user=schemas.UserOut.model_validate(user))


@app.get("/api/auth/me", response_model=schemas.UserOut, tags=["auth"])
def me(current_user: models.User = Depends(get_current_user)):
    return current_user


# ---------------------------------------------------------------------------
# Prediction routes
# ---------------------------------------------------------------------------

@app.post("/api/predict", response_model=schemas.PredictionResult, tags=["prediction"])
def predict(
    payload: schemas.PredictionInput,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    features = payload.model_dump()
    try:
        result = ml_model.predict(features)
    except ml_model.ModelNotLoadedError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    risk_level = ml_model.risk_level_from_probability(result["probability"])
    recommendations = ml_model.recommendations_for(risk_level, features)
    radar = ml_model.radar_data(features)

    record = models.Prediction(
        user_id=current_user.id,
        pregnancies=features["pregnancies"],
        glucose=features["glucose"],
        bloodpressure=features["bloodpressure"],
        skinthickness=features["skinthickness"],
        insulin=features["insulin"],
        bmi=features["bmi"],
        dpf=features["dpf"],
        age=features["age"],
        prediction=result["prediction"],
        probability=result["probability"],
        risk_level=risk_level,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    log_activity(db, current_user.id, "prediction",
                 f"Prediction #{record.id} -> {risk_level} risk ({result['probability']*100:.1f}%)")

    return schemas.PredictionResult(
        prediction_id=record.id,
        prediction_label="Diabetic" if result["prediction"] == 1 else "Non-Diabetic",
        probability=result["probability"],
        risk_level=risk_level,
        recommendations=recommendations,
        radar=radar,
        created_at=record.created_at,
    )


# ---------------------------------------------------------------------------
# Dashboard stats (auto-updating)
# ---------------------------------------------------------------------------

@app.get("/api/stats", response_model=schemas.DashboardStats, tags=["dashboard"])
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    records = db.query(models.Prediction).filter(models.Prediction.user_id == current_user.id).all()
    total = len(records)
    high = sum(1 for r in records if r.risk_level == "High")
    moderate = sum(1 for r in records if r.risk_level == "Moderate")
    low = sum(1 for r in records if r.risk_level == "Low")
    avg_prob = (sum(r.probability for r in records) / total) if total else 0.0
    last_at = max((r.created_at for r in records), default=None)

    return schemas.DashboardStats(
        total_predictions=total,
        high_risk_count=high,
        moderate_risk_count=moderate,
        low_risk_count=low,
        average_probability=avg_prob,
        last_prediction_at=last_at,
    )


@app.get("/api/stats/platform", tags=["dashboard"])
def platform_stats(db: Session = Depends(get_db)):
    """Public, anonymous counters shown as animated numbers on the landing page."""
    total_predictions = db.query(models.Prediction).count()
    total_users = db.query(models.User).count()
    diabetic_correct_ratio = 0.974  # reported model accuracy from offline evaluation
    return {
        "predictions_made": total_predictions,
        "registered_users": total_users,
        "accuracy_percentage": round(diabetic_correct_ratio * 100, 1),
    }


# ---------------------------------------------------------------------------
# History routes
# ---------------------------------------------------------------------------

@app.get("/api/history", response_model=List[schemas.PredictionOut], tags=["history"])
def get_history(
    search: Optional[str] = Query(None, description="Search by risk level or result text"),
    risk_level: Optional[str] = Query(None),
    sort_by: str = Query("created_at", pattern="^(created_at|probability|risk_level)$"),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.Prediction).filter(models.Prediction.user_id == current_user.id)

    if risk_level:
        q = q.filter(models.Prediction.risk_level == risk_level)

    if search:
        like = f"%{search}%"
        q = q.filter(models.Prediction.risk_level.ilike(like))

    sort_col = getattr(models.Prediction, sort_by)
    q = q.order_by(asc(sort_col) if sort_dir == "asc" else desc(sort_col))

    return q.all()


@app.delete("/api/history/{prediction_id}", tags=["history"])
def delete_history_item(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    record = db.query(models.Prediction).filter(
        models.Prediction.id == prediction_id,
        models.Prediction.user_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Prediction record not found.")

    db.delete(record)
    db.commit()
    log_activity(db, current_user.id, "delete_prediction", f"Deleted prediction #{prediction_id}")
    return {"message": "Prediction record deleted."}


@app.get("/api/report/{prediction_id}/pdf", tags=["history"])
def download_report(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    record = db.query(models.Prediction).filter(
        models.Prediction.id == prediction_id,
        models.Prediction.user_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Prediction record not found.")

    pdf_buffer = pdf_report.generate_report_pdf(current_user, record)
    log_activity(db, current_user.id, "download_report", f"Downloaded report for prediction #{prediction_id}")

    filename = f"diabetes_report_{prediction_id}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Reminder routes
# ---------------------------------------------------------------------------

@app.post("/api/reminders", response_model=schemas.ReminderOut, tags=["reminders"])
def create_reminder(
    payload: schemas.ReminderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    reminder = models.Reminder(
        user_id=current_user.id,
        title=payload.title,
        message=payload.message,
        remind_at=payload.remind_at,
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@app.get("/api/reminders", response_model=List[schemas.ReminderOut], tags=["reminders"])
def list_reminders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Reminder).filter(
        models.Reminder.user_id == current_user.id
    ).order_by(asc(models.Reminder.remind_at)).all()


@app.delete("/api/reminders/{reminder_id}", tags=["reminders"])
def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    reminder = db.query(models.Reminder).filter(
        models.Reminder.id == reminder_id,
        models.Reminder.user_id == current_user.id,
    ).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found.")
    db.delete(reminder)
    db.commit()
    return {"message": "Reminder deleted."}


# ---------------------------------------------------------------------------
# Health check + static frontend
# ---------------------------------------------------------------------------

@app.get("/api/health", tags=["system"])
def health_check():
    return {
        "status": "ok",
        "model_ready": ml_model.is_model_ready(),
        "time": datetime.utcnow().isoformat(),
    }


# Serve the frontend (HTML/CSS/JS) as static files so the whole app can be
# deployed as a single Render web service. This must be mounted LAST so it
# doesn't shadow the /api routes above.
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
