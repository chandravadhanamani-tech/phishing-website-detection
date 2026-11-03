"""
explain_model.py - SHAP Explainability Module
"""

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
import shap

from preprocessing import DataPreprocessor

BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
DATA_PATH      = os.path.join(BASE_DIR, "data", "raw", "phishing_dataset.csv")
MODELS_DIR     = os.path.join(BASE_DIR, "saved_models")
PLOTS_DIR      = os.path.join(MODELS_DIR, "plots")
EXPLAINER_PATH = os.path.join(MODELS_DIR, "shap_explainer.pkl")
os.makedirs(PLOTS_DIR, exist_ok=True)


def main():
    print("=" * 60)
    print("  PhishingShield - SHAP Explainability")
    print("=" * 60)

    model_path = os.path.join(MODELS_DIR, "xgboost_model.pkl")
    if not os.path.exists(model_path):
        print(f"[-] XGBoost model not found: {model_path}")
        sys.exit(1)

    print("\n[+] Loading XGBoost model...")
    model = joblib.load(model_path)

    print("[+] Loading dataset...")
    prep = DataPreprocessor()
    df   = prep.load_uci_dataset(DATA_PATH)
    df   = prep.clean_data(df)
    X, y = prep.get_feature_target_split(df)
    _, X_test, _, y_test = prep.get_train_test_split(X, y)

    scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
    scaler      = joblib.load(scaler_path)
    X_test_sc   = scaler.transform(X_test)

    feature_names = prep.get_feature_names()

    n_samples = min(500, len(X_test_sc))
    idx = np.random.choice(len(X_test_sc), n_samples, replace=False)
    X_sample = X_test_sc[idx]

    print("\n[+] Computing SHAP values...")
    explainer   = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    print(f"   SHAP values shape: {np.array(shap_values).shape}")

    joblib.dump(explainer, EXPLAINER_PATH)
    print(f"\n[+] SHAP explainer saved: {EXPLAINER_PATH}")

    mean_shap = np.abs(shap_values).mean(axis=0)
    ranked     = sorted(zip(feature_names, mean_shap), key=lambda x: x[1], reverse=True)

    print("\n[+] Top 15 Most Important Features (Global SHAP):")
    print("-" * 50)
    for rank, (name, importance) in enumerate(ranked[:15], 1):
        bar = "X" * int(importance * 50 / (ranked[0][1] + 1e-9))
        print(f"  {rank:2}. {name:<30} {importance:.4f} {bar}")

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor("#0a0e1a")

    shap.summary_plot(
        shap_values,
        X_sample,
        feature_names=feature_names,
        show=False,
        plot_size=None,
    )

    plt.title("SHAP Summary Plot - Feature Impact on Phishing Detection",
              color="white", fontsize=13, pad=15)
    plt.tight_layout()
    summary_path = os.path.join(PLOTS_DIR, "shap_summary.png")
    plt.savefig(summary_path, dpi=150, bbox_inches="tight", facecolor="#0a0e1a")
    plt.close()
    print(f"\n[+] Saved: {summary_path}")

    names_top15      = [r[0] for r in ranked[:15]]
    importance_top15 = [r[1] for r in ranked[:15]]

    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor("#0a0e1a")
    ax.set_facecolor("#111827")

    colors = ["#00d4ff" if i < 5 else "#7c3aed" if i < 10 else "#10b981"
              for i in range(len(names_top15))]

    ax.barh(names_top15[::-1], importance_top15[::-1], color=colors[::-1], alpha=0.9)
    ax.set_xlabel("Mean |SHAP Value|", color="white")
    ax.set_title("Top 15 Features - Global SHAP Importance", color="white", fontsize=13)
    ax.tick_params(colors="white")
    ax.spines["bottom"].set_color("#334155")
    ax.spines["left"].set_color("#334155")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", alpha=0.1, color="white")

    bar_path = os.path.join(PLOTS_DIR, "shap_importance.png")
    plt.tight_layout()
    plt.savefig(bar_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"[+] Saved: {bar_path}")

    print("\n" + "=" * 60)
    print("  SHAP Analysis Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
