"""
Seed demo data on first launch — creates sample students + study logs.
"""
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.schemas import Student, StudyLog, User
from services.auth_service import hash_password


DEMO_STUDENTS = [
    {
        "name": "Priya Sharma", "gender": "female", "ethnicity": "group C",
        "parent_education": "bachelor's degree", "lunch": "standard", "test_prep": "completed",
        "attendance_pct": 92, "study_hours_per_day": 5.5, "assignment_completion_pct": 95,
        "sleep_hours": 7.5, "social_media_hours": 1, "stress_level": 3, "extracurricular_hours": 3,
        "math": 88, "reading": 92, "writing": 90, "science": 85, "history": 78, "target_score": 90,
    },
    {
        "name": "Rahul Verma", "gender": "male", "ethnicity": "group B",
        "parent_education": "high school", "lunch": "free/reduced", "test_prep": "none",
        "attendance_pct": 62, "study_hours_per_day": 1.5, "assignment_completion_pct": 45,
        "sleep_hours": 5.5, "social_media_hours": 5, "stress_level": 8, "extracurricular_hours": 1,
        "math": 42, "reading": 48, "writing": 40, "science": 38, "history": 35, "target_score": 60,
    },
    {
        "name": "Ananya Patel", "gender": "female", "ethnicity": "group D",
        "parent_education": "master's degree", "lunch": "standard", "test_prep": "completed",
        "attendance_pct": 85, "study_hours_per_day": 4, "assignment_completion_pct": 82,
        "sleep_hours": 7, "social_media_hours": 2, "stress_level": 5, "extracurricular_hours": 4,
        "math": 72, "reading": 78, "writing": 80, "science": 70, "history": 65, "target_score": 80,
    },
    {
        "name": "Vikram Singh", "gender": "male", "ethnicity": "group A",
        "parent_education": "some college", "lunch": "standard", "test_prep": "none",
        "attendance_pct": 75, "study_hours_per_day": 3, "assignment_completion_pct": 65,
        "sleep_hours": 6.5, "social_media_hours": 3, "stress_level": 6, "extracurricular_hours": 5,
        "math": 65, "reading": 58, "writing": 55, "science": 60, "history": 52, "target_score": 70,
    },
    {
        "name": "Meera Iyer", "gender": "female", "ethnicity": "group E",
        "parent_education": "associate's degree", "lunch": "standard", "test_prep": "completed",
        "attendance_pct": 88, "study_hours_per_day": 4.5, "assignment_completion_pct": 90,
        "sleep_hours": 8, "social_media_hours": 1.5, "stress_level": 4, "extracurricular_hours": 2,
        "math": 76, "reading": 85, "writing": 82, "science": 74, "history": 80, "target_score": 85,
    },
]

SUBJECTS = ["math", "reading", "writing", "science", "history"]


async def seed_demo_data(db: AsyncSession):
    """Seed demo students and study logs if DB is empty."""
    # Check if data exists
    count = await db.execute(select(func.count(Student.id)))
    if count.scalar() > 0:
        return False  # Already seeded

    print("[Seed] Creating demo students...")

    # Create a demo user account
    demo_user = User(
        username="demo",
        password_hash=hash_password("demo123"),
        full_name="Demo User",
        email="demo@edupilot.ai",
    )
    db.add(demo_user)
    await db.flush()
    await db.refresh(demo_user)

    # Create students linked to demo user
    for s_data in DEMO_STUDENTS:
        student = Student(**s_data, user_id=demo_user.id)
        db.add(student)
    await db.flush()

    # Get created students
    result = await db.execute(select(Student))
    students = result.scalars().all()

    # Add study logs for past 10 days
    print("[Seed] Creating study logs...")
    today = date.today()
    import random
    random.seed(42)

    for student in students:
        for day_offset in range(10):
            d = today - timedelta(days=day_offset)
            # 1-3 subjects per day
            n_subjects = random.randint(1, 3)
            for subj in random.sample(SUBJECTS, n_subjects):
                log = StudyLog(
                    student_id=student.id,
                    date=d,
                    subject=subj,
                    hours_studied=round(random.uniform(0.5, 3), 1),
                    topics_covered=f"{subj.capitalize()} practice",
                    tasks_completed=random.randint(2, 5),
                    tasks_total=5,
                    self_rating=random.randint(2, 5),
                    notes=f"Studied {subj} on {d}",
                )
                db.add(log)

    await db.commit()
    print(f"[Seed] Created {len(DEMO_STUDENTS)} students + study logs")
    print("[Seed] Demo login: username='demo' password='demo123'")
    return True
