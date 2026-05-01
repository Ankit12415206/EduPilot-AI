# 🎓 EduPilot AI — Adaptive Study Planner & Academic Performance Predictor

> An AI-powered academic assistant that predicts student performance, identifies weaknesses, generates personalized study plans, and continuously adapts based on progress.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Ankit12415206/EduPilot-AI.git
cd EduPilot-AI

# 2. Install Python dependencies
pip install -r backend/requirements.txt

# 3. Train ML models (generates dataset + trains models)
cd backend
python ml/train.py

# 4. Start the server
python -m uvicorn main:app --reload --port 8000

# 5. Open in browser
# http://localhost:8000
```

**Demo Account:** `demo` / `demo123`

## 🔐 Authentication & Security
- **Secure Login/Register**: SHA-256 password hashing with unique salts.
- **Token Sessions**: Secure session management for multi-user support.
- **User Scoping**: Data isolation ensuring users only access their own profiles.
- **Auth Guard**: Protected dashboard routes.

## 🧠 Core Features

### 1. Performance Prediction
- Ensemble of **Random Forest + XGBoost** for high accuracy (98.5%).
- Predicts final score (regression) and pass/fail probability (classification).
- **Explainability Engine**: Provides human-readable reasons for every prediction.

### 2. Universal Profile System
- **Customizable Fields**: Toggle default academic fields or add your own custom metrics.
- **Flexible Data**: Adapts to school students, college students, or professionals.
- **Persistent Settings**: Your field configuration is saved across sessions.

### 3. Personalized Study Plans
- **AI Generation**: Weekly schedules prioritized by subject weakness severity.
- **Adaptive Engine**: Monitors daily progress and automatically regenerates plans.
- **Actionable Tasks**: Daily checklists with completion status tracking.

### 4. Advanced Analytics Dashboard
- **6-Chart Interface**: Includes Radar, Gauge, Bar, Pie, Line, and Heatmap visualizations.
- **KPI Grid**: Track Predicted Score, Pass Probability, Streak, Weaknesses, and Completion Rate.
- **Natural Design**: Warm-cool palette with glassmorphism and Lucide icons.

### 5. Reminders & Notifications
- **Study Reminders**: Set specific times for subject-wise study sessions.
- **Browser Notifications**: Native alerts ensuring you never miss a study window.

### 6. Professional Data Export
- **Multi-Format Export**: Download your data as **PDF, CSV, Excel (XLS), or JSON**.
- **Formatted PDF Reports**: Print-ready performance summaries with charts and metrics.
- **Data Preview**: Table-based overview before exporting.

### 7. Integrated Help Chatbot
- **Rule-based Assistant**: Guided help for platform features.
- **Quick Actions**: One-click answers for common queries.

## 📊 ML Model Performance

| Metric | Value |
|--------|-------|
| Best Model | Logistic Regression (98.5%) |
| XGBoost RMSE | 0.84 |
| F1 Score | 0.989 |
| Dataset Size | 2000 students |
| Features | 17 (Demographic + Behavioral) |

## 📁 Project Structure

```
EduPilot-AI/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── database.py           # SQLAlchemy setup
│   ├── config.py             # Configuration
│   ├── api/                  # REST API endpoints (Auth, Students, Plans, etc.)
│   ├── models/               # ORM schemas
│   ├── services/             # Business logic (Auth, Planner, Recommendation)
│   └── ml/                   # ML engine
│       ├── dataset_generator.py  # Data pipeline
│       ├── predictor.py          # Prediction logic
│       ├── explainer.py          # Explainability engine
│       ├── train.py              # Training pipeline
│       └── artifacts/            # Trained model weights & metrics
├── frontend/
│   ├── login.html            # Auth portal
│   ├── index.html            # Dashboard SPA
│   ├── css/styles.css        # Professional Design System
│   └── js/                   # Modular JS (Dashboard, Export, Reminders, etc.)
├── data/                     # SQLite DB & raw datasets
└── docs/                     # Documentation & Model Plots
```

## 👨‍💻 Author

**Ankit**
Registration No: 12415206
Course: B.Tech CSE AI/ML (CSE274)

---

*Powered by Machine Learning & ❤️*
