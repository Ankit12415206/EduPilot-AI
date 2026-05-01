"""
Study Plan Generator for EduPilot AI.
Creates personalized daily/weekly study schedules based on weaknesses,
goals, and available time with spaced repetition integration.
"""
from datetime import datetime, timedelta, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.schemas import Student, StudyPlan
from services.weakness_service import detect_weaknesses
from ml.dataset_generator import SUBJECT_COLS


# Study session templates
SESSION_TEMPLATES = {
    "focus": {"duration_min": 45, "type": "deep_study", "description": "Deep focus session"},
    "review": {"duration_min": 25, "type": "review", "description": "Quick revision"},
    "practice": {"duration_min": 35, "type": "practice", "description": "Practice problems"},
    "break": {"duration_min": 10, "type": "break", "description": "Short break"},
}

# Spaced repetition intervals (days)
SPACED_REPETITION = [1, 3, 7, 14, 30]

SUBJECT_LABELS = {
    "math": "Mathematics", "reading": "Reading", "writing": "Writing",
    "science": "Science", "history": "History",
}

SUBJECT_TOPICS = {
    "math": ["Algebra", "Geometry", "Calculus", "Statistics", "Trigonometry", "Number Theory"],
    "reading": ["Comprehension", "Vocabulary", "Critical Analysis", "Speed Reading", "Literature"],
    "writing": ["Essay Structure", "Grammar", "Creative Writing", "Research Papers", "Editing"],
    "science": ["Physics Basics", "Chemistry", "Biology", "Lab Methods", "Scientific Reasoning"],
    "history": ["World History", "Modern Era", "Civilizations", "Political Systems", "Timelines"],
}


async def generate_study_plan(db: AsyncSession, student_id: int,
                               available_hours: float = 4.0,
                               exam_date: date = None) -> dict:
    """Generate a personalized weekly study plan."""

    # Get weakness analysis
    weakness_data = await detect_weaknesses(db, student_id)

    # Calculate priority scores
    subject_priorities = _calculate_priorities(
        weakness_data["subject_analysis"],
        weakness_data["target_score"],
        exam_date
    )

    # Generate weekly plan
    weekly_plan = _generate_weekly_schedule(
        subject_priorities, available_hours, exam_date
    )

    # Generate daily tasks
    daily_tasks = _generate_daily_tasks(subject_priorities, available_hours)

    # Generate recommendations
    recommendations = _generate_recommendations(weakness_data)

    plan_data = {
        "weekly_schedule": weekly_plan,
        "daily_tasks": daily_tasks,
        "subject_priorities": subject_priorities,
        "total_hours_per_week": round(available_hours * 6, 1),  # 6 study days
        "revision_day": "Sunday",
        "spaced_repetition_schedule": _generate_spaced_repetition(subject_priorities),
        "generated_at": datetime.utcnow().isoformat(),
    }

    # Deactivate old plans
    old_plans = await db.execute(
        select(StudyPlan).where(
            StudyPlan.student_id == student_id,
            StudyPlan.is_active == True
        )
    )
    for plan in old_plans.scalars():
        plan.is_active = False

    # Save new plan
    study_plan = StudyPlan(
        student_id=student_id,
        plan_type="weekly",
        plan_data=plan_data,
        weaknesses=weakness_data["weak_subjects"],
        recommendations=recommendations,
        is_active=True,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(study_plan)
    await db.flush()
    await db.refresh(study_plan)

    return {
        "plan_id": study_plan.id,
        "student_id": student_id,
        "plan": plan_data,
        "weaknesses": weakness_data["weak_subjects"],
        "recommendations": recommendations,
        "assessment": weakness_data["overall_assessment"],
    }


def _calculate_priorities(subject_analysis: list, target: float,
                          exam_date: date = None) -> list:
    """Calculate study priority for each subject."""
    # Exam proximity factor
    if exam_date:
        days_until = (exam_date - date.today()).days
        proximity_factor = max(0.5, min(2.0, 30 / max(days_until, 1)))
    else:
        proximity_factor = 1.0

    priorities = []
    for subj in subject_analysis:
        gap = max(0, target - subj["score"])
        severity_weight = {"critical": 3.0, "moderate": 2.0, "mild": 1.0, "strong": 0.3}
        weight = severity_weight.get(subj["severity"], 1.0)

        priority_score = (gap / 100) * weight * proximity_factor
        time_allocation_pct = max(5, round(priority_score * 100, 1))

        priorities.append({
            **subj,
            "priority_score": round(priority_score, 3),
            "time_allocation_pct": time_allocation_pct,
            "suggested_topics": SUBJECT_TOPICS.get(subj["subject"], [])[:3],
            "study_approach": _get_study_approach(subj["severity"]),
        })

    # Normalize time allocation to 100%
    total = sum(p["time_allocation_pct"] for p in priorities)
    if total > 0:
        for p in priorities:
            p["time_allocation_pct"] = round(p["time_allocation_pct"] / total * 100, 1)

    priorities.sort(key=lambda x: x["priority_score"], reverse=True)
    return priorities


def _get_study_approach(severity: str) -> str:
    """Suggest study approach based on weakness severity."""
    approaches = {
        "critical": "Start with basics. Focus on understanding core concepts before practice.",
        "moderate": "Mix theory review with practice problems. Aim for consistent daily progress.",
        "mild": "Practice-focused study. Work through challenging problems.",
        "strong": "Maintenance mode. Quick reviews and advanced challenges.",
    }
    return approaches.get(severity, "Balanced study approach.")


def _generate_weekly_schedule(priorities: list, daily_hours: float,
                              exam_date: date = None) -> list:
    """Generate a 7-day weekly schedule."""
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekly = []

    for i, day in enumerate(days):
        if day == "Sunday":
            # Revision day
            sessions = [{
                "time_slot": "10:00 - 12:00",
                "subject": "All Subjects",
                "type": "revision",
                "duration_min": 120,
                "description": "Weekly revision of all subjects",
                "topics": ["Review notes", "Practice weak areas", "Self-assessment"],
            }]
            weekly.append({"day": day, "is_rest_day": False, "is_revision_day": True, "sessions": sessions})
            continue

        sessions = []
        remaining_minutes = int(daily_hours * 60)
        start_hour = 9  # 9 AM start

        # Allocate subjects based on priority
        for j, subj in enumerate(priorities):
            if remaining_minutes <= 0:
                break

            alloc_min = int(remaining_minutes * subj["time_allocation_pct"] / 100)
            alloc_min = max(20, min(alloc_min, 60))  # 20-60 min per subject

            # Vary topics across days
            topic_idx = (i + j) % len(subj.get("suggested_topics", ["General"]))
            topics = subj.get("suggested_topics", ["General"])
            topic = topics[topic_idx] if topics else "General"

            session_type = "focus" if subj["severity"] in ("critical", "moderate") else "review"

            sessions.append({
                "time_slot": f"{start_hour:02d}:00 - {start_hour:02d}:{alloc_min:02d}",
                "subject": subj["label"],
                "subject_key": subj["subject"],
                "type": session_type,
                "duration_min": alloc_min,
                "description": f"{SESSION_TEMPLATES[session_type]['description']} — {topic}",
                "topics": [topic],
                "priority": subj["severity"],
            })

            # Add break
            sessions.append({
                "time_slot": f"{start_hour:02d}:{alloc_min:02d} - {start_hour + 1:02d}:00",
                "subject": "Break",
                "type": "break",
                "duration_min": 10,
                "description": "Short break — stretch, hydrate",
            })

            remaining_minutes -= alloc_min
            start_hour += 1

        weekly.append({
            "day": day,
            "is_rest_day": False,
            "is_revision_day": False,
            "sessions": [s for s in sessions if s["type"] != "break"][:6],
            "total_study_min": sum(s["duration_min"] for s in sessions if s["type"] != "break"),
        })

    return weekly


def _generate_daily_tasks(priorities: list, daily_hours: float) -> list:
    """Generate a checklist of daily tasks."""
    tasks = []
    task_id = 1

    for subj in priorities[:5]:
        n_tasks = 3 if subj["severity"] == "critical" else 2 if subj["severity"] == "moderate" else 1
        topics = subj.get("suggested_topics", ["General Study"])

        for i in range(min(n_tasks, len(topics))):
            tasks.append({
                "id": task_id,
                "subject": subj["label"],
                "subject_key": subj["subject"],
                "task": f"Study {topics[i]}",
                "duration_min": 30 if subj["severity"] in ("critical", "moderate") else 20,
                "priority": subj["severity"],
                "completed": False,
            })
            task_id += 1

    # Add general tasks
    tasks.append({
        "id": task_id, "subject": "General", "subject_key": "general",
        "task": "Review today's notes", "duration_min": 15,
        "priority": "mild", "completed": False,
    })
    task_id += 1
    tasks.append({
        "id": task_id, "subject": "General", "subject_key": "general",
        "task": "Plan tomorrow's study", "duration_min": 10,
        "priority": "mild", "completed": False,
    })

    return tasks


def _generate_spaced_repetition(priorities: list) -> list:
    """Generate spaced repetition schedule for weak subjects."""
    schedule = []
    today = date.today()

    for subj in priorities:
        if subj["severity"] in ("critical", "moderate"):
            for interval in SPACED_REPETITION:
                review_date = today + timedelta(days=interval)
                schedule.append({
                    "subject": subj["label"],
                    "subject_key": subj["subject"],
                    "review_date": review_date.isoformat(),
                    "interval_days": interval,
                    "topics": subj.get("suggested_topics", [])[:2],
                })

    schedule.sort(key=lambda x: x["review_date"])
    return schedule


def _generate_recommendations(weakness_data: dict) -> list:
    """Generate actionable study recommendations."""
    recs = []

    # Subject-specific
    for weak in weakness_data["weak_subjects"][:3]:
        recs.append({
            "type": "subject",
            "priority": "high",
            "title": f"Improve {weak['label']}",
            "description": f"Your {weak['label']} score ({weak['score']}) is {abs(weak['gap_from_target']):.0f} points below target. "
                           f"Dedicate extra focus sessions to this subject.",
            "action_items": [
                f"Spend at least 45 minutes daily on {weak['label']}",
                "Complete all assigned practice problems",
                "Seek help from teacher or tutoring for difficult topics",
            ],
        })

    # Behavioral
    for behavior in weakness_data["poor_behaviors"][:2]:
        recs.append({
            "type": "behavioral",
            "priority": "medium",
            "title": f"Improve {behavior['label']}",
            "description": behavior["recommendation"],
            "action_items": [behavior["recommendation"]],
        })

    # General
    recs.append({
        "type": "general",
        "priority": "low",
        "title": "Maintain Consistency",
        "description": "Consistency is more important than intensity. Study daily, even if briefly.",
        "action_items": [
            "Set a fixed study schedule",
            "Track your progress daily",
            "Reward yourself for streaks",
        ],
    })

    return recs
