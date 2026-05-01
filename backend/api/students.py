"""Student API endpoints — scoped by authenticated user."""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.schemas import Student
from schemas.pydantic_models import StudentCreate, StudentUpdate, StudentResponse
from services.auth_service import validate_token

router = APIRouter(prefix="/api/students", tags=["Students"])


def get_user_id(authorization: str = Header(default="")) -> int:
    """Extract user_id from token header."""
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        return None
    info = validate_token(token)
    return info["user_id"] if info else None


@router.post("", status_code=201)
async def create_student_endpoint(data: StudentCreate,
                                   authorization: str = Header(default=""),
                                   db: AsyncSession = Depends(get_db)):
    """Create a new student profile for the logged-in user."""
    user_id = get_user_id(authorization)
    student = Student(**data.model_dump(), user_id=user_id)
    db.add(student)
    await db.flush()
    await db.refresh(student)
    return _student_dict(student)


@router.get("")
async def list_students(authorization: str = Header(default=""),
                        db: AsyncSession = Depends(get_db)):
    """List students belonging to the logged-in user."""
    user_id = get_user_id(authorization)
    query = select(Student).order_by(Student.id)
    if user_id:
        query = query.where(Student.user_id == user_id)
    result = await db.execute(query)
    return [_student_dict(s) for s in result.scalars().all()]


@router.get("/{student_id}")
async def get_student_endpoint(student_id: int,
                                authorization: str = Header(default=""),
                                db: AsyncSession = Depends(get_db)):
    """Get a student by ID (must belong to logged-in user)."""
    student = await _get_owned_student(db, student_id, authorization)
    return _student_dict(student)


@router.put("/{student_id}")
async def update_student_endpoint(student_id: int, data: StudentUpdate,
                                   authorization: str = Header(default=""),
                                   db: AsyncSession = Depends(get_db)):
    """Update a student's data."""
    student = await _get_owned_student(db, student_id, authorization)
    for key, value in data.model_dump(exclude_unset=True).items():
        if value is not None and hasattr(student, key):
            setattr(student, key, value)
    await db.flush()
    await db.refresh(student)
    return _student_dict(student)


@router.delete("/{student_id}")
async def delete_student_endpoint(student_id: int,
                                   authorization: str = Header(default=""),
                                   db: AsyncSession = Depends(get_db)):
    """Delete a student."""
    student = await _get_owned_student(db, student_id, authorization)
    await db.delete(student)
    return {"message": "Student deleted successfully"}


async def _get_owned_student(db, student_id, authorization) -> Student:
    """Get a student ensuring it belongs to the current user."""
    user_id = get_user_id(authorization)
    query = select(Student).where(Student.id == student_id)
    if user_id:
        query = query.where(Student.user_id == user_id)
    result = await db.execute(query)
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


def _student_dict(s: Student) -> dict:
    return {
        "id": s.id, "user_id": s.user_id, "name": s.name, "email": s.email,
        "gender": s.gender, "ethnicity": s.ethnicity,
        "parent_education": s.parent_education, "lunch": s.lunch,
        "test_prep": s.test_prep, "attendance_pct": s.attendance_pct,
        "study_hours_per_day": s.study_hours_per_day,
        "assignment_completion_pct": s.assignment_completion_pct,
        "sleep_hours": s.sleep_hours, "social_media_hours": s.social_media_hours,
        "stress_level": s.stress_level, "extracurricular_hours": s.extracurricular_hours,
        "math": s.math, "reading": s.reading, "writing": s.writing,
        "science": s.science, "history": s.history, "target_score": s.target_score,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }
