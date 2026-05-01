"""
SQLAlchemy ORM models for EduPilot AI.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    gender = Column(String(10))
    ethnicity = Column(String(20))
    parent_education = Column(String(50))
    lunch = Column(String(20))
    test_prep = Column(String(20))

    # Behavioral features
    attendance_pct = Column(Float, default=0)
    study_hours_per_day = Column(Float, default=0)
    assignment_completion_pct = Column(Float, default=0)
    sleep_hours = Column(Float, default=7)
    social_media_hours = Column(Float, default=0)
    stress_level = Column(Integer, default=5)
    extracurricular_hours = Column(Float, default=0)

    # Subject scores
    math = Column(Integer, default=0)
    reading = Column(Integer, default=0)
    writing = Column(Integer, default=0)
    science = Column(Integer, default=0)
    history = Column(Integer, default=0)

    # Targets
    target_score = Column(Float, default=75)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    predictions = relationship("Prediction", back_populates="student", cascade="all, delete-orphan")
    study_logs = relationship("StudyLog", back_populates="student", cascade="all, delete-orphan")
    study_plans = relationship("StudyPlan", back_populates="student", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="student", cascade="all, delete-orphan")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    predicted_score = Column(Float)
    pass_probability = Column(Float)
    prediction_label = Column(String(10))  # Pass/Fail
    confidence = Column(Float)
    explanation = Column(JSON)  # SHAP explanation data
    feature_importance = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="predictions")


class StudyLog(Base):
    __tablename__ = "study_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    date = Column(Date, default=date.today)
    subject = Column(String(50))
    hours_studied = Column(Float, default=0)
    topics_covered = Column(Text)
    tasks_completed = Column(Integer, default=0)
    tasks_total = Column(Integer, default=0)
    self_rating = Column(Integer, default=3)  # 1-5
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="study_logs")


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    plan_type = Column(String(20), default="weekly")  # daily/weekly
    plan_data = Column(JSON)  # Full plan structure
    weaknesses = Column(JSON)  # Detected weaknesses
    recommendations = Column(JSON)  # Study recommendations
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)

    student = relationship("Student", back_populates="study_plans")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    target_score = Column(Float, default=75)
    target_subject = Column(String(50))  # None = overall
    exam_date = Column(Date)
    description = Column(Text)
    is_achieved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="goals")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
