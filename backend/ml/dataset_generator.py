"""
Dataset Generator for EduPilot AI.
Loads the Kaggle StudentsPerformance dataset (1000 students),
enriches it with synthetic behavioral features, then generates
an additional 1000 synthetic students for a combined ~2000 student dataset.
"""
import os
import sys
import numpy as np
import pandas as pd

# Add parent to path so config can be imported when run as script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_DIR, KAGGLE_DATA_PATH

np.random.seed(42)

# ── Subject list used across the system ──────────────────────────────────
SUBJECTS = ["math", "reading", "writing", "science", "history"]


def _load_kaggle_data() -> pd.DataFrame:
    """Load and clean the Kaggle StudentsPerformance.csv."""
    df = pd.read_csv(KAGGLE_DATA_PATH)
    df.columns = [c.strip().lower().replace(" ", "_").replace("/", "_") for c in df.columns]
    df.rename(columns={
        "math_score": "math",
        "reading_score": "reading",
        "writing_score": "writing",
        "race_ethnicity": "ethnicity",
        "parental_level_of_education": "parent_education",
        "test_preparation_course": "test_prep",
    }, inplace=True)
    return df


def _encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """Convert categorical columns to numeric codes for ML."""
    mappings = {
        "gender": {"female": 0, "male": 1},
        "ethnicity": {"group A": 0, "group B": 1, "group C": 2, "group D": 3, "group E": 4},
        "parent_education": {
            "some high school": 0, "high school": 1, "some college": 2,
            "associate's degree": 3, "bachelor's degree": 4, "master's degree": 5,
        },
        "lunch": {"free/reduced": 0, "standard": 1},
        "test_prep": {"none": 0, "completed": 1},
    }
    for col, mapping in mappings.items():
        if col in df.columns:
            df[f"{col}_encoded"] = df[col].map(mapping).fillna(0).astype(int)
    return df


def _add_behavioral_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add realistic synthetic behavioral features correlated with scores."""
    n = len(df)
    avg_score = df[["math", "reading", "writing"]].mean(axis=1)
    normalized = avg_score / 100.0  # 0-1 scale

    # Attendance: correlated with performance (60-100%)
    df["attendance_pct"] = np.clip(
        normalized * 30 + 65 + np.random.normal(0, 5, n), 40, 100
    ).round(1)

    # Study hours per day: correlated with performance (0.5-8)
    df["study_hours_per_day"] = np.clip(
        normalized * 5 + 1 + np.random.normal(0, 0.8, n), 0.5, 8.0
    ).round(1)

    # Assignment completion rate: correlated with performance (30-100%)
    df["assignment_completion_pct"] = np.clip(
        normalized * 50 + 45 + np.random.normal(0, 7, n), 20, 100
    ).round(1)

    # Sleep hours: slight positive correlation (4-10)
    df["sleep_hours"] = np.clip(
        6.5 + normalized * 1.5 + np.random.normal(0, 0.8, n), 4, 10
    ).round(1)

    # Social media hours: negative correlation (0-8)
    df["social_media_hours"] = np.clip(
        4 - normalized * 3 + np.random.normal(0, 1, n), 0, 8
    ).round(1)

    # Stress level: slightly higher for lower performers (1-10)
    df["stress_level"] = np.clip(
        6 - normalized * 3 + np.random.normal(0, 1.5, n), 1, 10
    ).astype(int)

    # Extracurricular hours per week: slight positive (0-10)
    df["extracurricular_hours"] = np.clip(
        normalized * 4 + 1 + np.random.normal(0, 1.5, n), 0, 10
    ).round(1)

    # Science score: correlated with math & reading
    df["science"] = np.clip(
        df["math"] * 0.4 + df["reading"] * 0.3 + np.random.normal(20, 8, n), 0, 100
    ).astype(int)

    # History score: correlated with reading & writing
    df["history"] = np.clip(
        df["reading"] * 0.4 + df["writing"] * 0.35 + np.random.normal(18, 8, n), 0, 100
    ).astype(int)

    return df


def _generate_synthetic_students(n: int = 1000) -> pd.DataFrame:
    """Generate fully synthetic student records."""
    data = {}

    # Demographic features
    data["gender"] = np.random.choice(["female", "male"], n)
    data["ethnicity"] = np.random.choice(
        ["group A", "group B", "group C", "group D", "group E"],
        n, p=[0.1, 0.2, 0.35, 0.25, 0.1]
    )
    data["parent_education"] = np.random.choice(
        ["some high school", "high school", "some college",
         "associate's degree", "bachelor's degree", "master's degree"],
        n, p=[0.12, 0.20, 0.22, 0.22, 0.15, 0.09]
    )
    data["lunch"] = np.random.choice(["free/reduced", "standard"], n, p=[0.35, 0.65])
    data["test_prep"] = np.random.choice(["none", "completed"], n, p=[0.64, 0.36])

    # Behavioral features (base)
    attendance = np.clip(np.random.normal(78, 12, n), 40, 100)
    study_hours = np.clip(np.random.normal(3.5, 1.5, n), 0.5, 8)
    assignment = np.clip(np.random.normal(72, 15, n), 20, 100)
    sleep = np.clip(np.random.normal(7, 1, n), 4, 10)
    social_media = np.clip(np.random.normal(2.5, 1.5, n), 0, 8)
    stress = np.clip(np.random.normal(5, 2, n), 1, 10)
    extracurricular = np.clip(np.random.normal(3, 2, n), 0, 10)

    data["attendance_pct"] = attendance.round(1)
    data["study_hours_per_day"] = study_hours.round(1)
    data["assignment_completion_pct"] = assignment.round(1)
    data["sleep_hours"] = sleep.round(1)
    data["social_media_hours"] = social_media.round(1)
    data["stress_level"] = stress.astype(int)
    data["extracurricular_hours"] = extracurricular.round(1)

    # Education level numeric for score generation
    edu_map = {
        "some high school": 0, "high school": 1, "some college": 2,
        "associate's degree": 3, "bachelor's degree": 4, "master's degree": 5,
    }
    edu_numeric = np.array([edu_map[e] for e in data["parent_education"]])
    lunch_numeric = np.array([1 if l == "standard" else 0 for l in data["lunch"]])
    prep_numeric = np.array([1 if t == "completed" else 0 for t in data["test_prep"]])

    # Generate scores using a realistic model
    base_score = (
        attendance * 0.15 +
        study_hours * 4 +
        assignment * 0.12 +
        sleep * 1.5 -
        social_media * 2.5 -
        stress * 1.2 +
        edu_numeric * 2 +
        lunch_numeric * 4 +
        prep_numeric * 5 +
        extracurricular * 0.5
    )

    for subject in SUBJECTS:
        noise = np.random.normal(0, 6, n)
        if subject == "math":
            scores = base_score * 0.9 + noise
        elif subject == "reading":
            scores = base_score * 0.95 + noise
        elif subject == "writing":
            scores = base_score * 0.92 + noise
        elif subject == "science":
            scores = base_score * 0.88 + noise
        else:  # history
            scores = base_score * 0.91 + noise
        data[subject] = np.clip(scores, 0, 100).astype(int)

    return pd.DataFrame(data)


def _compute_targets(df: pd.DataFrame) -> pd.DataFrame:
    """Compute target variables: final_score and pass_fail."""
    score_cols = [c for c in SUBJECTS if c in df.columns]
    df["final_score"] = df[score_cols].mean(axis=1).round(1)
    df["pass_fail"] = (df["final_score"] >= 40).astype(int)
    return df


def generate_dataset() -> pd.DataFrame:
    """Main entry: load Kaggle data + generate synthetic → combined dataset."""
    print("📚 Loading Kaggle StudentsPerformance dataset...")
    kaggle_df = _load_kaggle_data()
    kaggle_df["source"] = "kaggle"
    print(f"   Loaded {len(kaggle_df)} Kaggle students")

    print("🔧 Adding behavioral features to Kaggle data...")
    kaggle_df = _add_behavioral_features(kaggle_df)

    print("🧪 Generating 1000 synthetic students...")
    synthetic_df = _generate_synthetic_students(1000)
    synthetic_df["source"] = "synthetic"

    # Align columns
    common_cols = [
        "gender", "ethnicity", "parent_education", "lunch", "test_prep",
        "attendance_pct", "study_hours_per_day", "assignment_completion_pct",
        "sleep_hours", "social_media_hours", "stress_level", "extracurricular_hours",
        "math", "reading", "writing", "science", "history", "source"
    ]
    kaggle_aligned = kaggle_df[common_cols].copy()
    synthetic_aligned = synthetic_df[common_cols].copy()

    combined = pd.concat([kaggle_aligned, synthetic_aligned], ignore_index=True)
    combined = _encode_categoricals(combined)
    combined = _compute_targets(combined)

    # Add student IDs
    combined.insert(0, "student_id", range(1, len(combined) + 1))
    combined.insert(1, "name", [f"Student_{i:04d}" for i in range(1, len(combined) + 1)])

    print(f"✅ Combined dataset: {len(combined)} students")
    print(f"   Features: {list(combined.columns)}")
    print(f"   Score range: {combined['final_score'].min():.1f} – {combined['final_score'].max():.1f}")
    print(f"   Pass rate: {combined['pass_fail'].mean()*100:.1f}%")

    return combined


def save_dataset(df: pd.DataFrame, filename: str = "students_combined.csv"):
    """Save to data directory."""
    path = os.path.join(DATA_DIR, filename)
    df.to_csv(path, index=False)
    print(f"💾 Saved to {path}")
    return path


# ── Feature columns for ML ──────────────────────────────────────────────
FEATURE_COLS = [
    "gender_encoded", "ethnicity_encoded", "parent_education_encoded",
    "lunch_encoded", "test_prep_encoded",
    "attendance_pct", "study_hours_per_day", "assignment_completion_pct",
    "sleep_hours", "social_media_hours", "stress_level", "extracurricular_hours",
    "math", "reading", "writing", "science", "history",
]

SUBJECT_COLS = ["math", "reading", "writing", "science", "history"]


if __name__ == "__main__":
    df = generate_dataset()
    save_dataset(df)
    print("\n📊 Sample rows:")
    print(df.head(3).to_string())
    print("\n📈 Statistics:")
    print(df[SUBJECT_COLS + ["final_score"]].describe().round(1).to_string())
