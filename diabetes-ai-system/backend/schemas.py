"""
Pydantic schemas used for request validation and response serialization.
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, field_validator


# ---------- Auth ----------

class SignUpRequest(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- Prediction ----------

class PredictionInput(BaseModel):
    pregnancies: int = Field(ge=0, le=20)
    glucose: float = Field(ge=0, le=500)
    bloodpressure: float = Field(ge=0, le=300)
    skinthickness: float = Field(ge=0, le=200)
    insulin: float = Field(ge=0, le=1000)
    bmi: float = Field(ge=0, le=100)
    dpf: float = Field(ge=0, le=5)
    age: int = Field(ge=1, le=120)

    @field_validator("glucose", "bloodpressure", "bmi")
    @classmethod
    def must_be_positive_for_clinical_validity(cls, v):
        if v < 0:
            raise ValueError("Value cannot be negative")
        return v


class PredictionOut(BaseModel):
    id: int
    pregnancies: int
    glucose: float
    bloodpressure: float
    skinthickness: float
    insulin: float
    bmi: float
    dpf: float
    age: int
    prediction: int
    probability: float
    risk_level: str
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionResult(BaseModel):
    prediction_id: int
    prediction_label: str          # "Diabetic" / "Non-Diabetic"
    probability: float             # 0..1
    risk_level: str                # Low / Moderate / High
    recommendations: List[str]
    radar: dict                    # normalized values for radar chart
    created_at: datetime


# ---------- History ----------

class HistoryFilter(BaseModel):
    search: Optional[str] = None
    risk_level: Optional[str] = None
    sort_by: Optional[str] = "created_at"
    sort_dir: Optional[str] = "desc"


# ---------- Dashboard stats ----------

class DashboardStats(BaseModel):
    total_predictions: int
    high_risk_count: int
    moderate_risk_count: int
    low_risk_count: int
    average_probability: float
    last_prediction_at: Optional[datetime] = None


# ---------- Reminders ----------

class ReminderCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    message: Optional[str] = None
    remind_at: datetime


class ReminderOut(BaseModel):
    id: int
    title: str
    message: Optional[str]
    remind_at: datetime
    is_sent: bool
    created_at: datetime

    class Config:
        from_attributes = True
