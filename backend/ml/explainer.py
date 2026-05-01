"""
SHAP-based Explainable AI module for EduPilot AI.
Provides human-readable explanations for predictions.
"""
import numpy as np
import shap
from .dataset_generator import FEATURE_COLS


# Human-readable feature names
FEATURE_LABELS = {
    "gender_encoded": "Gender",
    "ethnicity_encoded": "Ethnicity Group",
    "parent_education_encoded": "Parental Education Level",
    "lunch_encoded": "Lunch Type (Economic Status)",
    "test_prep_encoded": "Test Preparation Course",
    "attendance_pct": "Attendance Percentage",
    "study_hours_per_day": "Daily Study Hours",
    "assignment_completion_pct": "Assignment Completion Rate",
    "sleep_hours": "Sleep Hours",
    "social_media_hours": "Social Media Usage",
    "stress_level": "Stress Level",
    "extracurricular_hours": "Extracurricular Activities",
    "math": "Math Score",
    "reading": "Reading Score",
    "writing": "Writing Score",
    "science": "Science Score",
    "history": "History Score",
}


class PredictionExplainer:
    """Generate SHAP-based explanations for predictions."""

    def __init__(self, predictor):
        self.predictor = predictor
        self._explainer = None

    def _get_explainer(self):
        """Lazily create SHAP explainer."""
        if self._explainer is None:
            self._explainer = shap.TreeExplainer(self.predictor.xgb_regressor)
        return self._explainer

    def explain(self, features: dict) -> dict:
        """Generate explanation for a single prediction."""
        X = self.predictor._prepare_input(features)
        explainer = self._get_explainer()
        shap_values = explainer.shap_values(X)

        # Build feature impact list
        impacts = []
        for i, col in enumerate(FEATURE_COLS):
            impact = float(shap_values[0][i])
            impacts.append({
                "feature": col,
                "label": FEATURE_LABELS.get(col, col),
                "value": features.get(col, 0),
                "impact": round(impact, 2),
                "direction": "positive" if impact > 0 else "negative",
                "magnitude": abs(round(impact, 2)),
            })

        # Sort by absolute impact
        impacts.sort(key=lambda x: x["magnitude"], reverse=True)

        # Generate human-readable summary
        top_positive = [i for i in impacts if i["direction"] == "positive"][:3]
        top_negative = [i for i in impacts if i["direction"] == "negative"][:3]

        explanations = []
        for item in top_positive:
            explanations.append(
                f"✅ {item['label']} is boosting your score by +{item['magnitude']:.1f} points"
            )
        for item in top_negative:
            explanations.append(
                f"⚠️ {item['label']} is reducing your score by -{item['magnitude']:.1f} points"
            )

        # Key insight
        if top_negative:
            worst = top_negative[0]
            key_insight = f"Your biggest area for improvement is {worst['label'].lower()}. " \
                          f"Improving this could boost your predicted score significantly."
        else:
            key_insight = "You're performing well across all factors. Keep it up!"

        return {
            "feature_impacts": impacts,
            "top_boosters": top_positive,
            "top_drags": top_negative,
            "explanations": explanations,
            "key_insight": key_insight,
            "base_value": round(float(explainer.expected_value), 1),
        }
