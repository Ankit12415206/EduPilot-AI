"""
Weakness Detection Service for EduPilot AI.
Identifies weak subjects and behavioral factors affecting performance.
"""
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.schemas import Student
from ml.dataset_generator import SUBJECT_COLS
from services.prediction_service import get_predictor, _student_to_features


SUBJECT_LABELS = {
    "math": "Mathematics",
    "reading": "Reading",
    "writing": "Writing",
    "science": "Science",
    "history": "History",
}

# Behavioral feature thresholds
BEHAVIORAL_THRESHOLDS = {
    "attendance_pct": {"good": 80, "bad": 60, "label": "Attendance", "unit": "%"},
    "study_hours_per_day": {"good": 4, "bad": 2, "label": "Daily Study Hours", "unit": "hrs"},
    "assignment_completion_pct": {"good": 80, "bad": 50, "label": "Assignment Completion", "unit": "%"},
    "sleep_hours": {"good": 7, "bad": 5, "label": "Sleep", "unit": "hrs"},
    "social_media_hours": {"good": 2, "bad": 4, "label": "Social Media", "unit": "hrs", "inverse": True},
    "stress_level": {"good": 4, "bad": 7, "label": "Stress Level", "unit": "/10", "inverse": True},
}


async def detect_weaknesses(db: AsyncSession, student_id: int) -> dict:
    """Analyze student weaknesses across subjects and behaviors."""
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise ValueError(f"Student {student_id} not found")

    # ── Subject Analysis ──
    scores = {s: getattr(student, s, 0) or 0 for s in SUBJECT_COLS}
    avg_score = np.mean(list(scores.values()))
    std_score = np.std(list(scores.values()))
    target = student.target_score or 75

    subject_analysis = []
    for subject, score in scores.items():
        gap_from_avg = score - avg_score
        gap_from_target = target - score

        if score < avg_score - std_score:
            severity = "critical"
        elif score < avg_score - std_score * 0.5:
            severity = "moderate"
        elif score < avg_score:
            severity = "mild"
        else:
            severity = "strong"

        subject_analysis.append({
            "subject": subject,
            "label": SUBJECT_LABELS.get(subject, subject),
            "score": score,
            "gap_from_average": round(gap_from_avg, 1),
            "gap_from_target": round(gap_from_target, 1),
            "severity": severity,
            "needs_improvement": score < target,
            "percentile_in_class": _estimate_percentile(score),
        })

    # Sort by severity (critical first)
    severity_order = {"critical": 0, "moderate": 1, "mild": 2, "strong": 3}
    subject_analysis.sort(key=lambda x: severity_order[x["severity"]])

    # ── Behavioral Analysis ──
    behavioral_analysis = []
    features = _student_to_features(student)

    for feat, thresholds in BEHAVIORAL_THRESHOLDS.items():
        value = getattr(student, feat, 0) or 0
        is_inverse = thresholds.get("inverse", False)

        if is_inverse:
            if value <= thresholds["good"]:
                status = "good"
            elif value >= thresholds["bad"]:
                status = "poor"
            else:
                status = "moderate"
        else:
            if value >= thresholds["good"]:
                status = "good"
            elif value <= thresholds["bad"]:
                status = "poor"
            else:
                status = "moderate"

        behavioral_analysis.append({
            "feature": feat,
            "label": thresholds["label"],
            "value": value,
            "unit": thresholds["unit"],
            "status": status,
            "recommendation": _get_behavioral_recommendation(feat, value, status),
        })

    # ── Feature Importance from ML ──
    predictor = get_predictor()
    importance = predictor.get_feature_importance()

    weak_subjects = [s for s in subject_analysis if s["severity"] in ("critical", "moderate")]
    strong_subjects = [s for s in subject_analysis if s["severity"] == "strong"]
    poor_behaviors = [b for b in behavioral_analysis if b["status"] == "poor"]

    return {
        "student_id": student_id,
        "student_name": student.name,
        "average_score": round(avg_score, 1),
        "target_score": target,
        "gap_from_target": round(target - avg_score, 1),
        "subject_analysis": subject_analysis,
        "behavioral_analysis": behavioral_analysis,
        "weak_subjects": weak_subjects,
        "strong_subjects": strong_subjects,
        "poor_behaviors": poor_behaviors,
        "feature_importance": importance[:8],
        "overall_assessment": _generate_assessment(avg_score, target, weak_subjects, poor_behaviors),
    }


def _estimate_percentile(score: int) -> int:
    """Rough percentile estimate based on typical distributions."""
    if score >= 90: return 95
    if score >= 80: return 80
    if score >= 70: return 65
    if score >= 60: return 45
    if score >= 50: return 30
    if score >= 40: return 15
    return 5


def _get_behavioral_recommendation(feature: str, value: float, status: str) -> str:
    """Generate actionable recommendation for behavioral factors."""
    if status == "good":
        return "Keep up the excellent work!"

    recommendations = {
        "attendance_pct": "Try to attend at least 80% of classes. Each class missed impacts retention.",
        "study_hours_per_day": "Gradually increase to 4+ hours daily. Use Pomodoro technique (25 min focus + 5 min break).",
        "assignment_completion_pct": "Prioritize completing all assignments. They reinforce classroom learning significantly.",
        "sleep_hours": "Aim for 7-8 hours of sleep. Sleep is critical for memory consolidation.",
        "social_media_hours": f"Reduce from {value:.1f}hrs to under 2hrs. Use app timers to limit scrolling.",
        "stress_level": "Practice relaxation techniques. Consider talking to a counselor if stress persists.",
    }
    return recommendations.get(feature, "Focus on improvement in this area.")


def _generate_assessment(avg: float, target: float, weak: list, poor_behaviors: list) -> str:
    """Generate an overall assessment paragraph."""
    gap = target - avg

    if gap <= 0:
        base = f"Great news! Your current average ({avg:.1f}) already meets your target ({target:.1f})."
    elif gap <= 10:
        base = f"You're close to your target! Just {gap:.1f} points away."
    elif gap <= 20:
        base = f"With focused effort, you can bridge the {gap:.1f}-point gap to your target."
    else:
        base = f"You need significant improvement ({gap:.1f} points) to reach your target."

    if weak:
        subjects = ", ".join(w["label"] for w in weak[:3])
        base += f" Focus areas: {subjects}."

    if poor_behaviors:
        habits = ", ".join(b["label"].lower() for b in poor_behaviors[:2])
        base += f" Also improve: {habits}."

    return base
