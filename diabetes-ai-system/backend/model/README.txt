Place your trained model file here as:

    diabetes_best_model.pkl

It can be either:
  (a) a raw scikit-learn-compatible classifier (e.g. an XGBClassifier) saved
      with `joblib.dump(model, "diabetes_best_model.pkl")`, or
  (b) a dict saved as `joblib.dump({"model": model, "scaler": scaler}, ...)`
      if you also fit a StandardScaler during training (recommended — this
      is what ml_training/train_model.py produces).

The backend (backend/ml_model.py) automatically detects which format you used.
Until this file exists, the server will start normally but /api/predict will
return a 503 error explaining the model isn't loaded yet.
