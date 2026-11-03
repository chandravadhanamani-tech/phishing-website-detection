"""
train_models.py - ML Model Training Pipeline
"""

import json
import os
import sys
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model  import LogisticRegression
from sklearn.tree          import DecisionTreeClassifier
from sklearn.ensemble      import RandomForestClassifier
from sklearn.svm           import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report,
)
from xgboost import XGBClassifier

from preprocessing import DataPreprocessor

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_PATH   = os.path.join(BASE_DIR, "data", "raw", "phishing_dataset.csv")
MODELS_DIR  = os.path.join(BASE_DIR, "saved_models")
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(os.path.join(MODELS_DIR, "plots"), exist_ok=True)

MODELS = {
    "logistic_regression": LogisticRegression(
        max_iter=1000, C=1.0, solver="lbfgs", random_state=42
    ),
    "decision_tree": DecisionTreeClassifier(
        max_depth=10, min_samples_split=5, random_state=42
    ),
    "random_forest": RandomForestClassifier(
        n_estimators=100, max_depth=15, random_state=42, n_jobs=-1
    ),
    "svm": SVC(
        kernel="rbf", C=1.0, probability=True, random_state=42
    ),
    "xgboost": XGBClassifier(
        n_estimators=100, max_depth=6, learning_rate=0.1,
        use_label_encoder=False, eval_metric="logloss",
        random_state=42, n_jobs=-1,
    ),
}


def evaluate_model(model, X_test, y_test, model_name: str) -> dict:
    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred

    metrics = {
        "model_name":     model_name,
        "accuracy":       round(float(accuracy_score(y_test, y_pred)), 4),
        "precision":      round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall":         round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1_score":       round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "roc_auc":        round(float(roc_auc_score(y_test, y_proba)), 4),
    }
    return metrics


def print_metrics_table(all_metrics: list) -> None:
    print("\n" + "=" * 80)
    print("  MODEL PERFORMANCE COMPARISON")
    print("=" * 80)
    header = f"{'Model':<25} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1':>10} {'ROC-AUC':>10}"
    print(header)
    print("-" * 80)
    for m in sorted(all_metrics, key=lambda x: x["f1_score"], reverse=True):
        row = (
            f"{m['model_name']:<25} "
            f"{m['accuracy']:>10.4f} "
            f"{m['precision']:>10.4f} "
            f"{m['recall']:>10.4f} "
            f"{m['f1_score']:>10.4f} "
            f"{m['roc_auc']:>10.4f}"
        )
        print(row)
    print("=" * 80)


def main():
    print("=" * 60)
    print("  PhishingShield - ML Model Training Pipeline")
    print("=" * 60)

    if not os.path.exists(DATA_PATH):
        print(f"\n[-] Dataset not found at: {DATA_PATH}")
        sys.exit(1)

    prep = DataPreprocessor()
    df   = prep.load_uci_dataset(DATA_PATH)
    df   = prep.clean_data(df)
    X, y = prep.get_feature_target_split(df)

    feature_names = prep.get_feature_names()
    X_train, X_test, y_train, y_test = prep.get_train_test_split(X, y)

    print("\n[+] Applying StandardScaler...")
    scaler  = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    all_metrics = []
    trained_models = {}

    for model_name, model in MODELS.items():
        print(f"\n[+] Training: {model_name}")

        cv_scores = cross_val_score(
            model, X_train_scaled, y_train,
            cv=cv, scoring="f1", n_jobs=-1,
        )
        print(f"   CV F1: {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")

        model.fit(X_train_scaled, y_train)
        trained_models[model_name] = model

        metrics = evaluate_model(model, X_test_scaled, y_test, model_name)
        all_metrics.append(metrics)

        print(f"   Test -> Acc: {metrics['accuracy']:.4f}  F1: {metrics['f1_score']:.4f}  AUC: {metrics['roc_auc']:.4f}")

        model_path = os.path.join(MODELS_DIR, f"{model_name}_model.pkl")
        joblib.dump(model, model_path)
        print(f"   Saved: {model_path}")

        y_pred = model.predict(X_test_scaled)
        print("\n" + classification_report(y_test, y_pred, target_names=["Legitimate", "Phishing"], digits=4))

    print_metrics_table(all_metrics)

    best = max(all_metrics, key=lambda x: x["f1_score"])
    print(f"\n[+] Best Model: {best['model_name']} (F1 = {best['f1_score']:.4f})")

    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))
    joblib.dump(np.array(feature_names), os.path.join(MODELS_DIR, "feature_names.pkl"))

    with open(os.path.join(MODELS_DIR, "metrics.json"), "w") as f:
        json.dump({
            "models":     all_metrics,
            "best_model": best["model_name"],
            "feature_count": len(feature_names),
            "train_size": len(X_train),
            "test_size":  len(X_test),
        }, f, indent=2)

    print(f"\n[+] All models and metrics saved to: {MODELS_DIR}/")


if __name__ == "__main__":
    main()
