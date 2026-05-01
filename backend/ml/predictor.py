"""
ML Predictor for EduPilot AI.
Trains and serves predictions using an ensemble of Random Forest + XGBoost.
"""
import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor, XGBClassifier

from .dataset_generator import FEATURE_COLS


class PerformancePredictor:
    """Ensemble predictor for student academic performance."""

    def __init__(self, artifacts_dir: str = None):
        if artifacts_dir is None:
            artifacts_dir = os.path.join(os.path.dirname(__file__), "artifacts")
        self.artifacts_dir = artifacts_dir
        os.makedirs(artifacts_dir, exist_ok=True)

        # Models
        self.rf_regressor = RandomForestRegressor(
            n_estimators=200, max_depth=12, min_samples_split=5,
            random_state=42, n_jobs=-1
        )
        self.xgb_regressor = XGBRegressor(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8, random_state=42
        )
        self.rf_classifier = RandomForestClassifier(
            n_estimators=200, max_depth=12, min_samples_split=5,
            random_state=42, n_jobs=-1
        )
        self.xgb_classifier = XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8, random_state=42,
            eval_metric="logloss"
        )
        self.scaler = StandardScaler()
        self._is_trained = False

    def train(self, df: pd.DataFrame) -> dict:
        """Train all models. Returns evaluation metrics."""
        X = df[FEATURE_COLS].values
        y_score = df["final_score"].values
        y_pass = df["pass_fail"].values

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # ── Train regressors ──
        print("🏋️ Training Random Forest Regressor...")
        self.rf_regressor.fit(X_scaled, y_score)
        rf_cv = cross_val_score(self.rf_regressor, X_scaled, y_score,
                                cv=5, scoring="neg_root_mean_squared_error")

        print("🏋️ Training XGBoost Regressor...")
        self.xgb_regressor.fit(X_scaled, y_score)
        xgb_cv = cross_val_score(self.xgb_regressor, X_scaled, y_score,
                                 cv=5, scoring="neg_root_mean_squared_error")

        # ── Train classifiers ──
        print("🏋️ Training Random Forest Classifier...")
        self.rf_classifier.fit(X_scaled, y_pass)
        rf_acc = cross_val_score(self.rf_classifier, X_scaled, y_pass,
                                 cv=5, scoring="accuracy")

        print("🏋️ Training XGBoost Classifier...")
        self.xgb_classifier.fit(X_scaled, y_pass)
        xgb_acc = cross_val_score(self.xgb_classifier, X_scaled, y_pass,
                                  cv=5, scoring="accuracy")
        xgb_f1 = cross_val_score(self.xgb_classifier, X_scaled, y_pass,
                                 cv=5, scoring="f1")

        self._is_trained = True
        metrics = {
            "rf_rmse": -rf_cv.mean(),
            "xgb_rmse": -xgb_cv.mean(),
            "ensemble_rmse": (-rf_cv.mean() + -xgb_cv.mean()) / 2,
            "rf_accuracy": rf_acc.mean(),
            "xgb_accuracy": xgb_acc.mean(),
            "xgb_f1": xgb_f1.mean(),
            "n_samples": len(df),
            "n_features": len(FEATURE_COLS),
        }

        print("\n📊 Evaluation Metrics:")
        for k, v in metrics.items():
            print(f"   {k}: {v:.4f}")

        return metrics

    def predict_score(self, features: dict) -> dict:
        """Predict final score (ensemble average of RF + XGB)."""
        X = self._prepare_input(features)
        rf_pred = self.rf_regressor.predict(X)[0]
        xgb_pred = self.xgb_regressor.predict(X)[0]
        ensemble_pred = (rf_pred * 0.4 + xgb_pred * 0.6)  # XGB weighted higher

        return {
            "predicted_score": round(float(np.clip(ensemble_pred, 0, 100)), 1),
            "rf_prediction": round(float(rf_pred), 1),
            "xgb_prediction": round(float(xgb_pred), 1),
            "confidence": round(float(1 - abs(rf_pred - xgb_pred) / 100), 3),
        }

    def predict_pass_fail(self, features: dict) -> dict:
        """Predict pass/fail probability."""
        X = self._prepare_input(features)
        rf_proba = self.rf_classifier.predict_proba(X)[0]
        xgb_proba = self.xgb_classifier.predict_proba(X)[0]
        ensemble_proba = rf_proba * 0.4 + xgb_proba * 0.6

        return {
            "pass_probability": round(float(ensemble_proba[1]), 3),
            "fail_probability": round(float(ensemble_proba[0]), 3),
            "prediction": "Pass" if ensemble_proba[1] >= 0.5 else "Fail",
        }

    def get_feature_importance(self) -> list:
        """Get ranked feature importance from the ensemble."""
        rf_imp = self.rf_regressor.feature_importances_
        xgb_imp = self.xgb_regressor.feature_importances_
        ensemble_imp = rf_imp * 0.4 + xgb_imp * 0.6

        importance = []
        for i, col in enumerate(FEATURE_COLS):
            importance.append({
                "feature": col,
                "importance": round(float(ensemble_imp[i]), 4),
                "rf_importance": round(float(rf_imp[i]), 4),
                "xgb_importance": round(float(xgb_imp[i]), 4),
            })

        importance.sort(key=lambda x: x["importance"], reverse=True)
        return importance

    def save(self):
        """Save trained models to disk."""
        joblib.dump(self.rf_regressor, os.path.join(self.artifacts_dir, "rf_regressor.pkl"))
        joblib.dump(self.xgb_regressor, os.path.join(self.artifacts_dir, "xgb_regressor.pkl"))
        joblib.dump(self.rf_classifier, os.path.join(self.artifacts_dir, "rf_classifier.pkl"))
        joblib.dump(self.xgb_classifier, os.path.join(self.artifacts_dir, "xgb_classifier.pkl"))
        joblib.dump(self.scaler, os.path.join(self.artifacts_dir, "scaler.pkl"))
        print(f"💾 Models saved to {self.artifacts_dir}")

    def load(self):
        """Load trained models from disk."""
        self.rf_regressor = joblib.load(os.path.join(self.artifacts_dir, "rf_regressor.pkl"))
        self.xgb_regressor = joblib.load(os.path.join(self.artifacts_dir, "xgb_regressor.pkl"))
        self.rf_classifier = joblib.load(os.path.join(self.artifacts_dir, "rf_classifier.pkl"))
        self.xgb_classifier = joblib.load(os.path.join(self.artifacts_dir, "xgb_classifier.pkl"))
        self.scaler = joblib.load(os.path.join(self.artifacts_dir, "scaler.pkl"))
        self._is_trained = True
        print("✅ Models loaded successfully")

    def _prepare_input(self, features: dict) -> np.ndarray:
        """Prepare a single input for prediction."""
        if not self._is_trained:
            raise RuntimeError("Model not trained. Call train() or load() first.")
        X = np.array([[features.get(col, 0) for col in FEATURE_COLS]])
        return self.scaler.transform(X)
