"""
Pydantic schemas for request/response validation.
"""
from datetime import datetime, date
from typing import Optional, List, Any
from pydantic import BaseModel, Field


# ── Student Schemas ──────────────────────────────────────────────────────

class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = None
    gender: str = "female"
    ethnicity: str = "group C"
    parent_education: str = "some college"
    lunch: str = "standard"
    test_prep: str = "none"
    attendance_pct: float = Field(75.0, ge=0, le=100)
    study_hours_per_day: float = Field(3.0, ge=0, le=16)
    assignment_completion_pct: float = Field(70.0, ge=0, le=100)
    sleep_hours: float = Field(7.0, ge=2, le=14)
    social_media_hours: float = Field(2.0, ge=0, le=16)
    stress_level: int = Field(5, ge=1, le=10)
    extracurricular_hours: float = Field(2.0, ge=0, le=16)
    math: int = Field(65, ge=0, le=100)
    reading: int = Field(65, ge=0, le=100)
    writing: int = Field(65, ge=0, le=100)
    science: int = Field(65, ge=0, le=100)
    history: int = Field(65, ge=0, le=100)
    target_score: float = Field(75.0, ge=0, le=100)


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    ethnicity: Optional[str] = None
    parent_education: Optional[str] = None
    lunch: Optional[str] = None
    test_prep: Optional[str] = None
    attendance_pct: Optional[float] = None
    study_hours_per_day: Optional[float] = None
    assignment_completion_pct: Optional[float] = None
    sleep_hours: Optional[float] = None
    social_media_hours: Optional[float] = None
    stress_level: Optional[int] = None
    extracurricular_hours: Optional[float] = None
    math: Optional[int] = None
    reading: Optional[int] = None
    writing: Optional[int] = None
    science: Optional[int] = None
    history: Optional[int] = None
    target_score: Optional[float] = None


class StudentResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    gender: str
    ethnicity: str
    parent_education: str
    lunch: str
    test_prep: str
    attendance_pct: float
    study_hours_per_day: float
    assignment_completion_pct: float
    sleep_hours: float
    social_media_hours: float
    stress_level: int
    extracurricular_hours: float
    math: int
    reading: int
    writing: int
    science: int
    history: int
    target_score: float
    created_at: datetime

    class Config:
        from_attributes = True


# ── Prediction Schemas ────────────────────────────────────────────────────

class PredictionResponse(BaseModel):
    id: int
    student_id: int
    predicted_score: float
    pass_probability: float
    prediction_label: str
    confidence: float
    explanation: Optional[Any] = None
    feature_importance: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Study Log Schemas ─────────────────────────────────────────────────────

class StudyLogCreate(BaseModel):
    subject: str
    hours_studied: float = Field(1.0, ge=0, le=16)
    topics_covered: Optional[str] = None
    tasks_completed: int = Field(0, ge=0)
    tasks_total: int = Field(0, ge=0)
    self_rating: int = Field(3, ge=1, le=5)
    notes: Optional[str] = None
    date: Optional[date] = None


class StudyLogResponse(BaseModel):
    id: int
    student_id: int
    date: date
    subject: str
    hours_studied: float
    topics_covered: Optional[str] = None
    tasks_completed: int
    tasks_total: int
    self_rating: int
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Study Plan Schemas ────────────────────────────────────────────────────

class StudyPlanResponse(BaseModel):
    id: int
    student_id: int
    plan_type: str
    plan_data: Any
    weaknesses: Optional[Any] = None
    recommendations: Optional[Any] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class GoalCreate(BaseModel):
    target_score: float = Field(75.0, ge=0, le=100)
    target_subject: Optional[str] = None
    exam_date: Optional[date] = None
    description: Optional[str] = None


# ── Analytics Schemas ─────────────────────────────────────────────────────

class AnalyticsOverview(BaseModel):
    predicted_score: Optional[float] = None
    pass_probability: Optional[float] = None
    study_streak: int = 0
    total_study_hours: float = 0
    weak_subjects_count: int = 0
    strong_subjects_count: int = 0
    improvement_trend: float = 0
    tasks_completion_rate: float = 0
