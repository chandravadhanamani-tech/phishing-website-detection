"""
evaluate_models.py - Model Evaluation & Visualization
"""

import json
import os
import sys
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from sklearn.metrics import (
    confusion_matrix, roc_curve, auc,
    ConfusionMatrixDisplay,
)

from preprocessing import DataPreprocessor

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE_DIR, "data", "raw", "phishing_dataset.csv")
MODELS_DIR = os.path.join(BASE_DIR, "saved_models")
PLOTS_DIR  = os.path.join(MODELS_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

plt.style.use("dark_background")
COLORS = {
    "logistic_regression": "#00d4ff",
    "decision_tree":       "#7c3aed",
    "random_forest":       "#10b981",
    "svm":                 "#f59e0b",
    "xgboost":             "#ef4444",
}

MODEL_NAMES = list(COLORS.keys())
DISPLAY_NAMES = {
    "logistic_regression": "Logistic Reg.",
    "decision_tree":       "Decision Tree",
    "random_forest":       "Random Forest",
    "svm":                 "SVM",
    "xgboost":             "XGBoost",
}


def load_data():
    prep = DataPreprocessor()
    df   = prep.load_uci_dataset(DATA_PATH)
    df   = prep.clean_data(df)
    X, y = prep.get_feature_target_split(df)
    _, X_test, _, y_test = prep.get_train_test_split(X, y)

    scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
    scaler      = joblib.load(scaler_path)
    X_test_sc   = scaler.transform(X_test)

    return X_test_sc, y_test, prep.get_feature_names()


def plot_confusion_matrices(models_dict, X_test, y_test):
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    fig.patch.set_facecolor("#0a0e1a")
    fig.suptitle("Confusion Matrices - All Models", fontsize=16, color="white", y=1.01)

    axes_flat = axes.flatten()

    for idx, (name, model) in enumerate(models_dict.items()):
        ax    = axes_flat[idx]
        y_pred = model.predict(X_test)
        cm     = confusion_matrix(y_test, y_pred)
        disp   = ConfusionMatrixDisplay(cm, display_labels=["Legitimate", "Phishing"])
        disp.plot(ax=ax, cmap="Blues", colorbar=False)
        ax.set_title(DISPLAY_NAMES.get(name, name), color="white", fontsize=12)
        ax.set_facecolor("#111827")
        ax.tick_params(colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")

    if len(models_dict) < 6:
        axes_flat[-1].set_visible(False)

    plt.tight_layout()
    path = os.path.join(PLOTS_DIR, "confusion_matrices.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"[+] Saved: {path}")


def plot_roc_curves(models_dict, X_test, y_test):
    fig, ax = plt.subplots(figsize=(9, 7))
    fig.patch.set_facecolor("#0a0e1a")
    ax.set_facecolor("#111827")

    for name, model in models_dict.items():
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X_test)[:, 1]
        else:
            y_proba = model.decision_function(X_test)

        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_auc_val = auc(fpr, tpr)
        label = f"{DISPLAY_NAMES.get(name, name)} (AUC = {roc_auc_val:.4f})"
        ax.plot(fpr, tpr, label=label, color=COLORS.get(name, "#ffffff"), linewidth=2)

    ax.plot([0, 1], [0, 1], "w--", alpha=0.3, linewidth=1)
    ax.set_xlabel("False Positive Rate", color="white")
    ax.set_ylabel("True Positive Rate", color="white")
    ax.set_title("ROC Curves - All Models", color="white", fontsize=14)
    ax.legend(loc="lower right", facecolor="#111827", labelcolor="white")
    ax.tick_params(colors="white")
    ax.spines["bottom"].set_color("#334155")
    ax.spines["left"].set_color("#334155")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(alpha=0.1, color="white")

    path = os.path.join(PLOTS_DIR, "roc_curves.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"[+] Saved: {path}")


def plot_comparison_bar(metrics_json: dict):
    models_data = metrics_json.get("models", [])
    if not models_data:
        return

    metrics_keys = ["accuracy", "precision", "recall", "f1_score", "roc_auc"]
    metric_labels = ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"]

    x       = np.arange(len(metrics_keys))
    width   = 0.15
    offsets = np.linspace(-(len(models_data) - 1) / 2, (len(models_data) - 1) / 2, len(models_data)) * width

    fig, ax = plt.subplots(figsize=(13, 6))
    fig.patch.set_facecolor("#0a0e1a")
    ax.set_facecolor("#111827")

    for i, model_m in enumerate(models_data):
        name   = model_m["model_name"]
        values = [model_m.get(k, 0) * 100 for k in metrics_keys]
        ax.bar(
            x + offsets[i], values, width,
            label  = DISPLAY_NAMES.get(name, name),
            color  = COLORS.get(name, "#888"),
            alpha  = 0.9,
            zorder = 3,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels, color="white")
    ax.set_ylabel("Score (%)", color="white")
    ax.set_title("Model Performance Comparison", color="white", fontsize=14)
    ax.set_ylim(0, 110)
    ax.legend(facecolor="#111827", labelcolor="white")
    ax.tick_params(colors="white")
    ax.grid(axis="y", alpha=0.1, color="white", zorder=0)
    ax.spines["bottom"].set_color("#334155")
    ax.spines["left"].set_color("#334155")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    path = os.path.join(PLOTS_DIR, "model_comparison.png")
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"[+] Saved: {path}")


def main():
    print("=" * 60)
    print("  PhishingShield - Model Evaluation & Visualization")
    print("=" * 60)

    if not os.path.exists(DATA_PATH):
        print(f"[-] Dataset not found: {DATA_PATH}")
        sys.exit(1)

    print("\n[+] Loading test data...")
    X_test, y_test, feature_names = load_data()

    models_dict = {}
    for name in MODEL_NAMES:
        model_path = os.path.join(MODELS_DIR, f"{name}_model.pkl")
        if os.path.exists(model_path):
            models_dict[name] = joblib.load(model_path)
            print(f"   [+] Loaded: {name}")

    if not models_dict:
        print("[-] No trained models found.")
        sys.exit(1)

    print("\n[+] Generating confusion matrices...")
    plot_confusion_matrices(models_dict, X_test, y_test)

    print("[+] Generating ROC curves...")
    plot_roc_curves(models_dict, X_test, y_test)

    metrics_path = os.path.join(MODELS_DIR, "metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            metrics_data = json.load(f)
        print("[+] Generating comparison bar chart...")
        plot_comparison_bar(metrics_data)

    print(f"\n[+] All plots saved to: {PLOTS_DIR}/")


if __name__ == "__main__":
    main()
