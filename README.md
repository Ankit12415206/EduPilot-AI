# 🎓 EduPilot AI — Adaptive Study Planner & Academic Performance Predictor

> An AI-powered academic assistant that predicts student performance, identifies weaknesses, generates personalized study plans, and continuously adapts based on progress.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Navigate to the project
cd StudyAI-Project

# 2. Install Python dependencies
pip install -r backend/requirements.txt

# 3. Train ML models (generates dataset + trains models)
cd backend
set PYTHONIOENCODING=utf-8
python ml/train.py

# 4. Start the server
python -m uvicorn main:app --reload --port 8000

# 5. Open in browser
# http://localhost:8000
```

## 📊 ML Model Performance

| Metric | Value |
|--------|-------|
| XGBoost RMSE | 0.82 |
| Random Forest RMSE | 1.21 |
| Classification Accuracy | 97.25% |
| F1 Score | 0.98 |
| Dataset Size | 2000 students |
| Features | 17 |

## 🧠 Core Features

### 1. Performance Prediction
- Ensemble of Random Forest + XGBoost
- Predicts final score (regression) and pass/fail (classification)
- SHAP-based explainability — shows WHY predictions were made

### 2. Weakness Detection
- Identifies weak subjects using statistical thresholds
- Analyzes behavioral factors (attendance, study hours, sleep, etc.)
- Color-coded severity: 🔴 Critical → 🟡 Moderate → 🔵 Mild → 🟢 Strong

### 3. Personalized Study Plans
- AI-generated weekly schedules prioritized by weakness severity
- Daily task checklists with completion tracking
- Spaced repetition intervals (1, 3, 7, 14, 30 days)
- Exam proximity weighting

### 4. Adaptive Learning Engine
- Monitors daily progress and self-ratings
- Detects improvement trends and stagnation
- Automatically regenerates plans when needed

### 5. Interactive Dashboard
- Performance gauge (predicted score)
- Subject radar chart
- Weakness heatmap
- Study trend charts
- Study streak counter

### 6. Additional Features
- 🎤 Voice commands (Web Speech API)
- 🌙 Dark/Light theme toggle
- 🔔 Toast notifications
- 📱 Responsive design (mobile-friendly)

## 📁 Project Structure

```
StudyAI-Project/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── database.py           # SQLAlchemy setup
│   ├── config.py             # Configuration
│   ├── api/                  # REST API endpoints
│   ├── models/               # ORM models
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic
│   └── ml/                   # ML engine
│       ├── dataset_generator.py  # Data pipeline
│       ├── predictor.py          # Prediction models
│       ├── explainer.py          # SHAP explainability
│       ├── train.py              # Training pipeline
│       └── artifacts/            # Saved models
├── frontend/
│   ├── index.html            # Dashboard SPA
│   ├── css/styles.css        # Design system
│   └── js/                   # JavaScript modules
├── data/                     # Generated datasets
├── docs/                     # Documentation
│   └── SRS.md               # Software Requirements Spec
└── README.md
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/students` | GET/POST | List/Create students |
| `/api/students/{id}` | GET/PUT/DELETE | Student CRUD |
| `/api/predict/{id}` | POST | Run prediction |
| `/api/weaknesses/{id}` | GET | Weakness analysis |
| `/api/plans/{id}` | GET/POST | Study plan |
| `/api/plans/{id}/adapt` | POST | Adaptive replan |
| `/api/progress/{id}` | GET/POST | Progress tracking |
| `/api/analytics/{id}/overview` | GET | Dashboard data |

## 🛠️ Technology Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **ML**: scikit-learn, XGBoost, SHAP, NumPy, Pandas
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **Dataset**: 1000 Kaggle + 1000 Synthetic students

## 📈 Future Scope

- Mobile app (React Native/Flutter)
- AI chatbot tutor
- Wearable device integration
- Online learning platform integration
- Collaborative study groups

## 👨‍💻 Author

Built as a CA ML Project for academic assessment.

---

*Powered by Machine Learning & ❤️*
