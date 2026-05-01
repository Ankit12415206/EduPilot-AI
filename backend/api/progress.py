"""Progress tracking API endpoints."""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.schemas import StudyLog
from schemas.pydantic_models import StudyLogCreate, StudyLogResponse
from services.adaptive_service import analyze_progress, _calculate_streak

router = APIRouter(prefix="/api/progress", tags=["Progress"])


@router.post("/{student_id}", status_code=201)
async def log_progress(student_id: int, data: StudyLogCreate, db: AsyncSession = Depends(get_db)):
    """Log daily study progress."""
    log = StudyLog(
        student_id=student_id,
        date=data.date or date.today(),
        subject=data.subject,
        hours_studied=data.hours_studied,
        topics_covered=data.topics_covered,
        tasks_completed=data.tasks_completed,
        tasks_total=data.tasks_total,
        self_rating=data.self_rating,
        notes=data.notes,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return {
        "id": log.id,
        "message": f"Progress logged for {data.subject}",
        "date": log.date.isoformat(),
    }


@router.get("/{student_id}")
async def get_progress(student_id: int, days: int = 30, db: AsyncSession = Depends(get_db)):
    """Get progress history."""
    from datetime import timedelta
    cutoff = date.today() - timedelta(days=days)
    result = await db.execute(
        select(StudyLog)
        .where(StudyLog.student_id == student_id, StudyLog.date >= cutoff)
        .order_by(StudyLog.date.desc())
    )
    logs = result.scalars().all()
    return {
        "student_id": student_id,
        "total_logs": len(logs),
        "logs": [
            {
                "id": l.id,
                "date": l.date.isoformat(),
                "subject": l.subject,
                "hours_studied": l.hours_studied,
                "topics_covered": l.topics_covered,
                "tasks_completed": l.tasks_completed,
                "tasks_total": l.tasks_total,
                "self_rating": l.self_rating,
                "notes": l.notes,
            }
            for l in logs
        ],
    }


@router.get("/{student_id}/streak")
async def get_streak(student_id: int, db: AsyncSession = Depends(get_db)):
    """Get current study streak."""
    streak = await _calculate_streak(db, student_id)
    return {"student_id": student_id, "streak": streak}


@router.get("/{student_id}/analysis")
async def get_progress_analysis(student_id: int, db: AsyncSession = Depends(get_db)):
    """Get detailed progress analysis."""
    try:
        return await analyze_progress(db, student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
