"""
Student service — CRUD operations for student management.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.schemas import Student


async def create_student(db: AsyncSession, data: dict) -> Student:
    """Create a new student."""
    student = Student(**data)
    db.add(student)
    await db.flush()
    await db.refresh(student)
    return student


async def get_student(db: AsyncSession, student_id: int) -> Student:
    """Get a student by ID."""
    result = await db.execute(select(Student).where(Student.id == student_id))
    return result.scalar_one_or_none()


async def get_all_students(db: AsyncSession) -> list:
    """Get all students."""
    result = await db.execute(select(Student).order_by(Student.id))
    return result.scalars().all()


async def update_student(db: AsyncSession, student_id: int, data: dict) -> Student:
    """Update a student's data."""
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        return None
    for key, value in data.items():
        if value is not None and hasattr(student, key):
            setattr(student, key, value)
    await db.flush()
    await db.refresh(student)
    return student


async def delete_student(db: AsyncSession, student_id: int) -> bool:
    """Delete a student."""
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        return False
    await db.delete(student)
    return True
