# EduPilot AI — Software Requirements Specification

## 1. Introduction

### 1.1 Purpose
EduPilot AI is an intelligent academic assistant that predicts student performance, identifies weaknesses, generates personalized study plans, and continuously adapts based on progress.

### 1.2 Scope
The system serves as a complete ML-powered academic planner for students, providing data-driven insights and actionable study recommendations.

### 1.3 Definitions
- **Performance Prediction**: ML-based estimation of final academic scores
- **Weakness Detection**: Automated identification of underperforming subjects
- **Adaptive Planning**: Dynamic study schedule adjustment based on progress
- **SHAP**: SHapley Additive exPlanations for model interpretability

## 2. Overall Description

### 2.1 Product Perspective
EduPilot AI is a web-based application with a FastAPI backend, ML engine, and interactive dashboard frontend.

### 2.2 User Classes
- **Students**: Primary users who input data, view predictions, follow study plans
- **Academic Advisors** (future): Can monitor multiple students

### 2.3 Operating Environment
- Python 3.10+ backend
- Modern web browser (Chrome, Firefox, Edge)
- SQLite database (file-based)

## 3. Functional Requirements

### FR-1: Student Profile Management
- FR-1.1: Create student profiles with academic and behavioral data
- FR-1.2: Update student information (scores, habits)
- FR-1.3: Delete student profiles
- FR-1.4: Multi-student support with selector

### FR-2: Performance Prediction
- FR-2.1: Predict final score using ensemble ML (RF + XGBoost)
- FR-2.2: Predict pass/fail probability
- FR-2.3: Provide model confidence score
- FR-2.4: Show SHAP-based explanations for predictions

### FR-3: Weakness Detection
- FR-3.1: Identify weak subjects using threshold-based classification
- FR-3.2: Analyze behavioral factors (attendance, study hours, etc.)
- FR-3.3: Rank weaknesses by severity (critical, moderate, mild)
- FR-3.4: Provide actionable improvement recommendations

### FR-4: Study Plan Generation
- FR-4.1: Generate personalized weekly schedules
- FR-4.2: Create daily task checklists
- FR-4.3: Prioritize subjects based on weakness severity
- FR-4.4: Include spaced repetition intervals
- FR-4.5: Allow marking tasks as complete

### FR-5: Adaptive Learning
- FR-5.1: Track daily study progress (hours, subjects, self-rating)
- FR-5.2: Analyze improvement trends
- FR-5.3: Detect stagnation or decline
- FR-5.4: Automatically trigger plan replanning when needed

### FR-6: Analytics Dashboard
- FR-6.1: Display KPI cards (predicted score, pass probability, streak, weak count)
- FR-6.2: Show subject radar chart
- FR-6.3: Show performance gauge
- FR-6.4: Show weakness heatmap
- FR-6.5: Show study trend charts

### FR-7: Voice Interaction
- FR-7.1: Support voice commands via Web Speech API
- FR-7.2: Navigate to sections by voice
- FR-7.3: Trigger predictions by voice

## 4. Non-Functional Requirements

### NFR-1: Performance
- API response time < 500ms for CRUD operations
- Prediction response time < 2 seconds
- Dashboard load time < 3 seconds

### NFR-2: Usability
- Premium dark-mode glassmorphism UI
- Responsive design (mobile, tablet, desktop)
- Toast notifications for user feedback
- Theme toggle (dark/light)

### NFR-3: Reliability
- ML model accuracy > 95% (classification)
- RMSE < 2.0 for score prediction
- Graceful error handling with user-friendly messages

### NFR-4: Maintainability
- Modular architecture (services, API, ML layers separated)
- Type-safe schemas (Pydantic)
- ORM-based database (SQLAlchemy)

## 5. Data Requirements

### 5.1 Dataset
- 2000 students (1000 Kaggle + 1000 synthetic)
- 17 features including demographics, behavior, and subject scores
- Target variables: final_score (continuous), pass_fail (binary)

### 5.2 Database Schema
- Students, Predictions, StudyLogs, StudyPlans, Goals tables
- Full referential integrity with cascading deletes

## 6. System Architecture

### 6.1 Backend: FastAPI (Python)
### 6.2 ML Engine: scikit-learn, XGBoost, SHAP
### 6.3 Database: SQLite via SQLAlchemy
### 6.4 Frontend: Vanilla HTML/CSS/JS with Chart.js

## 7. Future Enhancements
- Mobile application (React Native)
- AI chatbot tutor integration
- Wearable device integration (sleep/stress tracking)
- Integration with online learning platforms (Coursera, Khan Academy)
- Collaborative study groups
- Real-time notification push via WebSockets
