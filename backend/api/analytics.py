"""Analytics API endpoints for the dashboard."""
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models.schemas import Student, Prediction, StudyLog
from services.weakness_service import detect_weaknesses
from services.adaptive_service import analyze_progress
from ml.dataset_generator import SUBJECT_COLS

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/{student_id}/overview")
async def get_overview(student_id: int, db: AsyncSession = Depends(get_db)):
    """Dashboard overview statistics."""
    # Get student
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Latest prediction
    pred_result = await db.execute(
        select(Prediction)
        .where(Prediction.student_id == student_id)
        .order_by(Prediction.created_at.desc())
        .limit(1)
    )
    latest_pred = pred_result.scalar_one_or_none()

    # Study stats
    week_ago = date.today() - timedelta(days=7)
    log_result = await db.execute(
        select(StudyLog)
        .where(StudyLog.student_id == student_id, StudyLog.date >= week_ago)
    )
    recent_logs = log_result.scalars().all()

    total_hours = sum(l.hours_studied for l in recent_logs)
    study_days = len(set(l.date for l in recent_logs))

    # Weakness count
    try:
        weakness_data = await detect_weaknesses(db, student_id)
        weak_count = len(weakness_data["weak_subjects"])
        strong_count = len(weakness_data["strong_subjects"])
    except Exception:
        weak_count = 0
        strong_count = 0

    # Streak
    try:
        progress = await analyze_progress(db, student_id)
        streak = progress["study_streak"]
    except Exception:
        streak = 0

    # Subject scores
    scores = {s: getattr(student, s, 0) or 0 for s in SUBJECT_COLS}

    return {
        "student_id": student_id,
        "student_name": student.name,
        "predicted_score": latest_pred.predicted_score if latest_pred else None,
        "pass_probability": latest_pred.pass_probability if latest_pred else None,
        "prediction_label": latest_pred.prediction_label if latest_pred else None,
        "study_streak": streak,
        "weekly_study_hours": round(total_hours, 1),
        "weekly_study_days": study_days,
        "weak_subjects_count": weak_count,
        "strong_subjects_count": strong_count,
        "current_scores": scores,
        "target_score": student.target_score,
        "average_score": round(sum(scores.values()) / max(1, len(scores)), 1),
    }


@router.get("/{student_id}/trends")
async def get_trends(student_id: int, days: int = 30, db: AsyncSession = Depends(get_db)):
    """Performance trend data for charts."""
    cutoff = date.today() - timedelta(days=days)

    # Get predictions over time
    pred_result = await db.execute(
        select(Prediction)
        .where(Prediction.student_id == student_id, Prediction.created_at >= cutoff)
        .order_by(Prediction.created_at)
    )
    predictions = pred_result.scalars().all()

    # Get study logs per day
    log_result = await db.execute(
        select(StudyLog)
        .where(StudyLog.student_id == student_id, StudyLog.date >= cutoff)
        .order_by(StudyLog.date)
    )
    logs = log_result.scalars().all()

    # Aggregate by date
    daily_study = {}
    for log in logs:
        day_str = log.date.isoformat()
        if day_str not in daily_study:
            daily_study[day_str] = {"hours": 0, "subjects": set(), "rating": []}
        daily_study[day_str]["hours"] += log.hours_studied
        daily_study[day_str]["subjects"].add(log.subject)
        daily_study[day_str]["rating"].append(log.self_rating)

    study_trend = [
        {
            "date": d,
            "hours": round(v["hours"], 1),
            "subjects_count": len(v["subjects"]),
            "avg_rating": round(sum(v["rating"]) / len(v["rating"]), 1) if v["rating"] else 0,
        }
        for d, v in sorted(daily_study.items())
    ]

    prediction_trend = [
        {
            "date": p.created_at.isoformat(),
            "predicted_score": p.predicted_score,
            "pass_probability": p.pass_probability,
        }
        for p in predictions
    ]

    return {
        "student_id": student_id,
        "study_trend": study_trend,
        "prediction_trend": prediction_trend,
    }


@router.get("/{student_id}/heatmap")
async def get_heatmap(student_id: int, db: AsyncSession = Depends(get_db)):
    """Subject weakness heatmap data."""
    try:
        weakness_data = await detect_weaknesses(db, student_id)
        heatmap = []
        for subj in weakness_data["subject_analysis"]:
            heatmap.append({
                "subject": subj["label"],
                "subject_key": subj["subject"],
                "score": subj["score"],
                "severity": subj["severity"],
                "gap": subj["gap_from_target"],
            })
        return {
            "student_id": student_id,
            "heatmap": heatmap,
            "average_score": weakness_data["average_score"],
            "target_score": weakness_data["target_score"],
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
