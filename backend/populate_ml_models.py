"""
populate_ml_models.py - Inserts trained ML model metrics into the MySQL database.
"""

import json
import os
import sys

sys.path.insert(0, ".")

from app.database import SessionLocal, init_db
from app.models.ml_model import MLModel
from app.core.config import get_settings

settings = get_settings()

def main():
    metrics_path = os.path.join("..", "ml", "saved_models", "metrics.json")
    if not os.path.exists(metrics_path):
        print(f"[-] Metrics file not found at: {metrics_path}")
        return

    with open(metrics_path, "r") as f:
        data = json.load(f)

    models_data = data.get("models", [])
    best_model_name = data.get("best_model", "xgboost")

    print("[+] Initializing database tables...")
    try:
        init_db()
    except Exception as e:
        print(f"[-] DB init warning: {e}")

    db = SessionLocal()
    try:
        for m in models_data:
            model_name = m["model_name"]
            is_active = (model_name == best_model_name)

            existing = db.query(MLModel).filter(MLModel.model_name == model_name).first()
            if existing:
                existing.accuracy = m.get("accuracy")
                existing.precision_score = m.get("precision")
                existing.recall_score = m.get("recall")
                existing.f1_score = m.get("f1_score")
                existing.roc_auc = m.get("roc_auc")
                existing.is_active = is_active
                print(f"[+] Updated model record in DB: {model_name} (active={is_active})")
            else:
                db_model = MLModel(
                    model_name=model_name,
                    version="1.0.0",
                    accuracy=m.get("accuracy"),
                    precision_score=m.get("precision"),
                    recall_score=m.get("recall"),
                    f1_score=m.get("f1_score"),
                    roc_auc=m.get("roc_auc"),
                    is_active=is_active,
                )
                db.add(db_model)
                print(f"[+] Inserted new model record to DB: {model_name} (active={is_active})")

        db.commit()
        print("[+] All model metrics successfully populated into MySQL database!")

    except Exception as e:
        db.rollback()
        print(f"[-] Error populating DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
