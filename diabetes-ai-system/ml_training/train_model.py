
import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import (
    RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier,
    ExtraTreesClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

DATA_PATH = os.path.join(os.path.dirname(__file__), "diabetes.csv")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "model", "diabetes_best_model.pkl")

FEATURE_COLUMNS = [
    "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
    "Insulin", "BMI", "DiabetesPedigreeFunction", "Age",
]
TARGET_COLUMN = "Outcome"


df = pd.read_csv("C:/Users/K KHYATHIPRIYA/OneDrive/Documents/Desktop/diabetes-ai-system/ml_training/diabetes.csv")
    

def main():

    X = df[FEATURE_COLUMNS].values
    y = df[TARGET_COLUMN].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42),
        "KNN": KNeighborsClassifier(n_neighbors=9),
        "SVM": SVC(probability=True, random_state=42),
        "Naive Bayes": GaussianNB(),
        "AdaBoost": AdaBoostClassifier(n_estimators=150, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(random_state=42),
        "Extra Trees": ExtraTreesClassifier(n_estimators=200, random_state=42),
        "XGBoost": XGBClassifier(
            n_estimators=250, max_depth=4, learning_rate=0.05,
            use_label_encoder=False, eval_metric="logloss", random_state=42,
        ),
    }

    print(f"{'Model':<22}{'Test Acc':>10}{'CV Acc (5-fold)':>18}")
    print("-" * 52)

    results = {}
    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        preds = model.predict(X_test_scaled)
        acc = accuracy_score(y_test, preds)
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
        results[name] = {"model": model, "test_acc": acc, "cv_acc": cv_scores.mean()}
        print(f"{name:<22}{acc*100:>9.2f}%{cv_scores.mean()*100:>17.2f}%")

    best_name = max(results, key=lambda n: results[n]["test_acc"])
    print(f"\nBest performing model on held-out test set: {best_name} "
          f"({results[best_name]['test_acc']*100:.2f}% accuracy)")

    # Per project requirement: always ship the XGBoost model to production,
    # regardless of which algorithm scored marginally higher in this run.
    xgb_model = results["XGBoost"]["model"]
    print(f"\nSaving XGBoost model (accuracy {results['XGBoost']['test_acc']*100:.2f}%) "
          f"to {os.path.abspath(OUTPUT_PATH)}")

    print("\nXGBoost classification report:")
    print(classification_report(y_test, xgb_model.predict(X_test_scaled)))

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    joblib.dump({"model": xgb_model, "scaler": scaler}, OUTPUT_PATH)


if __name__ == "__main__":
    main()
