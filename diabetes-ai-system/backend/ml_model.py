"""
Loads the trained XGBoost model (diabetes_best_model.pkl) once at startup and
exposes a single predict() function used by the API.

Expected feature order (matches the Pima Indians Diabetes dataset and the
SignUp/Dashboard form):
    [Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DPF, Age]

The model is expected to be a scikit-learn-compatible classifier (e.g. an
XGBClassifier saved with joblib.dump) exposing .predict() and .predict_proba().
If the saved file is instead a dict like {"model": ..., "scaler": ...}, both
are unpacked automatically.
"""
import logging
import os

import joblib
import numpy as np

from config import settings

logger = logging.getLogger("diabetes_ai.ml_model")

_model = None
_scaler = None  # optional, only used if the .pkl bundles a fitted scaler

FEATURE_NAMES = [
    "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
    "Insulin", "BMI", "DiabetesPedigreeFunction", "Age",
]

# "Normal" clinical reference ranges, used only to scale the health radar
# chart (0-100) shown on the report page — NOT used by the model itself.
RADAR_REFERENCE_MAX = {
    "Glucose": 200.0,
    "BMI": 50.0,
    "BloodPressure": 120.0,
    "Insulin": 300.0,
    "Age": 90.0,
}


class ModelNotLoadedError(RuntimeError):
    pass


def load_model() -> None:
    """Loads the model file into memory. Called once on FastAPI startup."""
    global _model, _scaler

    if not os.path.exists(settings.MODEL_PATH):
        logger.warning(
            "Model file not found at %s. Predictions will fail until you "
            "place diabetes_best_model.pkl there.",
            settings.MODEL_PATH,
        )
        return

    loaded = joblib.load(settings.MODEL_PATH)

    if isinstance(loaded, dict):
        _model = loaded.get("model")
        _scaler = loaded.get("scaler")
    else:
        _model = loaded
        _scaler = None

    logger.info("Diabetes prediction model loaded from %s", settings.MODEL_PATH)


def is_model_ready() -> bool:
    return _model is not None


def predict(features: dict) -> dict:
    """
    features: dict with keys pregnancies, glucose, bloodpressure, skinthickness,
              insulin, bmi, dpf, age (same shape as schemas.PredictionInput).
    Returns: {"prediction": 0|1, "probability": float}
    """
    if _model is None:
        raise ModelNotLoadedError(
            "The prediction model is not loaded. Make sure "
            "backend/model/diabetes_best_model.pkl exists and restart the server."
        )

    row = np.array([[
        features["pregnancies"],
        features["glucose"],
        features["bloodpressure"],
        features["skinthickness"],
        features["insulin"],
        features["bmi"],
        features["dpf"],
        features["age"],
    ]], dtype=float)

    if _scaler is not None:
        row = _scaler.transform(row)

    pred = int(_model.predict(row)[0])

    if hasattr(_model, "predict_proba"):
        proba = float(_model.predict_proba(row)[0][1])  # P(class == 1 / diabetic)
    else:
        # Fallback for models without predict_proba (shouldn't happen with XGBoost)
        proba = float(pred)

    return {"prediction": pred, "probability": proba}


def risk_level_from_probability(probability: float) -> str:
    if probability >= 0.66:
        return "High"
    if probability >= 0.33:
        return "Moderate"
    return "Low"


def recommendations_for(risk_level: str, features: dict) -> list[str]:
    base_high = [
        "Reduce sugar and refined-carbohydrate intake starting today.",
        "Aim for at least 30 minutes of physical activity, 5 days a week.",
        "Schedule a consultation with a healthcare professional soon.",
        "Monitor your blood glucose levels regularly and keep a log.",
        "Reduce sodium intake to help manage blood pressure.",
    ]
    base_moderate = [
        "Adopt a balanced, lower-sugar diet rich in fiber and vegetables.",
        "Increase weekly physical activity to at least 150 minutes.",
        "Get an annual checkup with an HbA1c/glucose screening.",
        "Maintain a healthy BMI through diet and consistent exercise.",
        "Limit processed foods and sugary beverages.",
    ]
    base_low = [
        "Maintain your current healthy lifestyle and habits.",
        "Continue a balanced diet with whole foods and vegetables.",
        "Keep up regular physical exercise, at least 3-4 times a week.",
        "Get periodic health screenings to catch any changes early.",
    ]

    recs = {"High": base_high, "Moderate": base_moderate, "Low": base_low}[risk_level][:]

    if features.get("bmi", 0) >= 30:
        recs.append("Your BMI indicates obesity — a structured weight-loss plan can significantly lower risk.")
    if features.get("glucose", 0) >= 140:
        recs.append("Your glucose reading is elevated — consider a fasting glucose retest.")
    if features.get("bloodpressure", 0) >= 130:
        recs.append("Your blood pressure is elevated — monitor it regularly and reduce sodium intake.")

    return recs


def radar_data(features: dict) -> dict:
    """Normalizes raw inputs to a 0-100 scale for the health radar chart."""
    def pct(value, max_value):
        return round(min(max(value, 0) / max_value, 1.0) * 100, 1)

    return {
        "Glucose": pct(features["glucose"], RADAR_REFERENCE_MAX["Glucose"]),
        "BMI": pct(features["bmi"], RADAR_REFERENCE_MAX["BMI"]),
        "BloodPressure": pct(features["bloodpressure"], RADAR_REFERENCE_MAX["BloodPressure"]),
        "Insulin": pct(features["insulin"], RADAR_REFERENCE_MAX["Insulin"]),
        "Age": pct(features["age"], RADAR_REFERENCE_MAX["Age"]),
    }
