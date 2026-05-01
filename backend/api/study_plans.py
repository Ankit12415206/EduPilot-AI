"""Study Plan API endpoints."""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.schemas import StudyPlan
from services.planner_service import generate_study_plan
from services.adaptive_service import adapt_plan, analyze_progress
from services.recommendation_service import get_study_recommendations
from services.weakness_service import detect_weaknesses

router = APIRouter(prefix="/api/plans", tags=["Study Plans"])


@router.post("/{student_id}")
async def create_plan(
    student_id: int,
    available_hours: float = Query(4.0, ge=1.0, le=12.0),
    exam_date: date = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Generate a new personalized study plan."""
    try:
        result = await generate_study_plan(db, student_id, available_hours, exam_date)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{student_id}")
async def get_plan(student_id: int, db: AsyncSession = Depends(get_db)):
    """Get the current active study plan."""
    result = await db.execute(
        select(StudyPlan)
        .where(StudyPlan.student_id == student_id, StudyPlan.is_active == True)
        .order_by(StudyPlan.created_at.desc())
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="No active plan found. Generate one first.")
    return {
        "plan_id": plan.id,
        "student_id": plan.student_id,
        "plan": plan.plan_data,
        "weaknesses": plan.weaknesses,
        "recommendations": plan.recommendations,
        "is_active": plan.is_active,
        "created_at": plan.created_at.isoformat(),
    }


@router.post("/{student_id}/adapt")
async def adapt_study_plan(student_id: int, db: AsyncSession = Depends(get_db)):
    """Trigger adaptive replanning based on progress."""
    try:
        return await adapt_plan(db, student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{student_id}/recommendations")
async def get_recommendations(student_id: int, db: AsyncSession = Depends(get_db)):
    """Get study recommendations."""
    try:
        weakness_data = await detect_weaknesses(db, student_id)
        progress_data = await analyze_progress(db, student_id)
        return get_study_recommendations(weakness_data, progress_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
