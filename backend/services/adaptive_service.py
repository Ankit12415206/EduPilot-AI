"""
Adaptive Learning Service for EduPilot AI.
Monitors student progress and dynamically adjusts study plans.
"""
from datetime import datetime, timedelta, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.schemas import Student, StudyLog, StudyPlan
from services.planner_service import generate_study_plan
from ml.dataset_generator import SUBJECT_COLS


SUBJECT_LABELS = {
    "math": "Mathematics", "reading": "Reading", "writing": "Writing",
    "science": "Science", "history": "History",
}


async def analyze_progress(db: AsyncSession, student_id: int) -> dict:
    """Analyze student's recent progress and determine if plan adaptation is needed."""

    # Get last 7 days of study logs
    week_ago = date.today() - timedelta(days=7)
    result = await db.execute(
        select(StudyLog)
        .where(StudyLog.student_id == student_id, StudyLog.date >= week_ago)
        .order_by(StudyLog.date.desc())
    )
    recent_logs = result.scalars().all()

    # Get last 30 days for trend analysis
    month_ago = date.today() - timedelta(days=30)
    result_month = await db.execute(
        select(StudyLog)
        .where(StudyLog.student_id == student_id, StudyLog.date >= month_ago)
        .order_by(StudyLog.date.desc())
    )
    monthly_logs = result_month.scalars().all()

    # Calculate study streak
    streak = await _calculate_streak(db, student_id)

    # Per-subject progress
    subject_progress = {}
    for subject in SUBJECT_COLS:
        subj_logs = [l for l in monthly_logs if l.subject == subject]
        if subj_logs:
            total_hours = sum(l.hours_studied for l in subj_logs)
            avg_rating = sum(l.self_rating for l in subj_logs) / len(subj_logs)
            completion_rate = sum(l.tasks_completed for l in subj_logs) / max(1, sum(l.tasks_total for l in subj_logs))

            # Trend: compare last week vs previous weeks
            recent_subj = [l for l in recent_logs if l.subject == subject]
            older_subj = [l for l in subj_logs if l not in recent_subj]
            recent_avg = sum(l.self_rating for l in recent_subj) / max(1, len(recent_subj))
            older_avg = sum(l.self_rating for l in older_subj) / max(1, len(older_subj))

            trend = "improving" if recent_avg > older_avg + 0.3 else \
                    "declining" if recent_avg < older_avg - 0.3 else "stable"

            subject_progress[subject] = {
                "label": SUBJECT_LABELS.get(subject, subject),
                "total_hours": round(total_hours, 1),
                "sessions_count": len(subj_logs),
                "avg_self_rating": round(avg_rating, 1),
                "task_completion_rate": round(completion_rate * 100, 1),
                "trend": trend,
                "recent_avg_rating": round(recent_avg, 1),
            }

    # Adaptation triggers
    adaptation_needed = False
    adaptation_reasons = []

    for subject, progress in subject_progress.items():
        if progress["trend"] == "declining":
            adaptation_needed = True
            adaptation_reasons.append(
                f"{progress['label']} is declining — increase focus"
            )
        if progress["task_completion_rate"] < 50:
            adaptation_needed = True
            adaptation_reasons.append(
                f"{progress['label']} task completion is low ({progress['task_completion_rate']}%)"
            )

    # Check overall study consistency
    study_days = len(set(l.date for l in recent_logs))
    if study_days < 4:
        adaptation_needed = True
        adaptation_reasons.append(f"Only studied {study_days}/7 days this week — need more consistency")

    total_week_hours = sum(l.hours_studied for l in recent_logs)

    return {
        "student_id": student_id,
        "study_streak": streak,
        "weekly_study_days": study_days,
        "weekly_study_hours": round(total_week_hours, 1),
        "subject_progress": subject_progress,
        "adaptation_needed": adaptation_needed,
        "adaptation_reasons": adaptation_reasons,
        "overall_trend": _overall_trend(subject_progress),
    }


async def adapt_plan(db: AsyncSession, student_id: int) -> dict:
    """Trigger adaptive replanning based on progress analysis."""
    progress = await analyze_progress(db, student_id)

    if not progress["adaptation_needed"]:
        return {
            "adapted": False,
            "message": "Your current plan is on track! No changes needed.",
            "progress": progress,
        }

    # Update student scores based on self-reported improvement
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()

    # Regenerate plan with updated priorities
    available_hours = max(2.0, progress["weekly_study_hours"] / 6)
    new_plan = await generate_study_plan(db, student_id, available_hours)

    return {
        "adapted": True,
        "reasons": progress["adaptation_reasons"],
        "new_plan": new_plan,
        "progress": progress,
        "message": f"Plan adapted based on {len(progress['adaptation_reasons'])} factors.",
    }


async def _calculate_streak(db: AsyncSession, student_id: int) -> int:
    """Calculate consecutive study days streak."""
    result = await db.execute(
        select(StudyLog.date)
        .where(StudyLog.student_id == student_id)
        .distinct()
        .order_by(StudyLog.date.desc())
    )
    dates = [row[0] for row in result.all()]

    if not dates:
        return 0

    streak = 0
    current = date.today()

    for d in dates:
        if d == current or d == current - timedelta(days=1):
            streak += 1
            current = d
        else:
            break

    return streak


def _overall_trend(subject_progress: dict) -> str:
    """Determine overall learning trend."""
    if not subject_progress:
        return "no_data"

    trends = [p["trend"] for p in subject_progress.values()]
    improving = trends.count("improving")
    declining = trends.count("declining")

    if improving > declining and improving >= 2:
        return "improving"
    elif declining > improving and declining >= 2:
        return "declining"
    return "stable"
