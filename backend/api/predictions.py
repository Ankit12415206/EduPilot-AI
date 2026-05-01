"""Prediction API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from services.prediction_service import run_prediction
from services.weakness_service import detect_weaknesses

router = APIRouter(prefix="/api", tags=["Predictions"])


@router.post("/predict/{student_id}")
async def predict(student_id: int, db: AsyncSession = Depends(get_db)):
    """Run performance prediction for a student."""
    try:
        result = await run_prediction(db, student_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/weaknesses/{student_id}")
async def get_weaknesses(student_id: int, db: AsyncSession = Depends(get_db)):
    """Get weakness analysis for a student."""
    try:
        return await detect_weaknesses(db, student_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
