"""
Prediction service — orchestrates ML prediction + explanation pipeline.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.schemas import Student, Prediction
from ml.predictor import PerformancePredictor
from ml.explainer import PredictionExplainer
from config import ML_ARTIFACTS_DIR


# Singleton predictor loaded once on import
_predictor = None
_explainer = None


def get_predictor() -> PerformancePredictor:
    global _predictor
    if _predictor is None:
        _predictor = PerformancePredictor(ML_ARTIFACTS_DIR)
        try:
            _predictor.load()
        except FileNotFoundError:
            print("⚠️ Models not found. Run 'python ml/train.py' first.")
    return _predictor


def get_explainer() -> PredictionExplainer:
    global _explainer
    if _explainer is None:
        _explainer = PredictionExplainer(get_predictor())
    return _explainer


def _student_to_features(student: Student) -> dict:
    """Convert student ORM object to feature dict for ML."""
    edu_map = {
        "some high school": 0, "high school": 1, "some college": 2,
        "associate's degree": 3, "bachelor's degree": 4, "master's degree": 5,
    }
    ethnicity_map = {"group A": 0, "group B": 1, "group C": 2, "group D": 3, "group E": 4}
    gender_map = {"female": 0, "male": 1}
    lunch_map = {"free/reduced": 0, "standard": 1}
    prep_map = {"none": 0, "completed": 1}

    return {
        "gender_encoded": gender_map.get(student.gender, 0),
        "ethnicity_encoded": ethnicity_map.get(student.ethnicity, 2),
        "parent_education_encoded": edu_map.get(student.parent_education, 2),
        "lunch_encoded": lunch_map.get(student.lunch, 1),
        "test_prep_encoded": prep_map.get(student.test_prep, 0),
        "attendance_pct": student.attendance_pct or 75,
        "study_hours_per_day": student.study_hours_per_day or 3,
        "assignment_completion_pct": student.assignment_completion_pct or 70,
        "sleep_hours": student.sleep_hours or 7,
        "social_media_hours": student.social_media_hours or 2,
        "stress_level": student.stress_level or 5,
        "extracurricular_hours": student.extracurricular_hours or 2,
        "math": student.math or 50,
        "reading": student.reading or 50,
        "writing": student.writing or 50,
        "science": student.science or 50,
        "history": student.history or 50,
    }


async def run_prediction(db: AsyncSession, student_id: int) -> dict:
    """Run full prediction + explanation for a student."""
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise ValueError(f"Student {student_id} not found")

    features = _student_to_features(student)
    predictor = get_predictor()
    explainer_inst = get_explainer()

    score_pred = predictor.predict_score(features)
    pass_pred = predictor.predict_pass_fail(features)
    explanation = explainer_inst.explain(features)
    importance = predictor.get_feature_importance()

    # Save prediction to DB
    prediction = Prediction(
        student_id=student_id,
        predicted_score=score_pred["predicted_score"],
        pass_probability=pass_pred["pass_probability"],
        prediction_label=pass_pred["prediction"],
        confidence=score_pred["confidence"],
        explanation=explanation,
        feature_importance=importance[:10],  # Top 10
    )
    db.add(prediction)
    await db.flush()
    await db.refresh(prediction)

    return {
        "prediction_id": prediction.id,
        "student_id": student_id,
        "student_name": student.name,
        "score": score_pred,
        "pass_fail": pass_pred,
        "explanation": explanation,
        "feature_importance": importance[:10],
    }
