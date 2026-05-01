"""Application configuration."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(PROJECT_DIR, 'data', 'edupilot.db')}"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
ML_ARTIFACTS_DIR = os.path.join(BASE_DIR, "ml", "artifacts")
KAGGLE_DATA_PATH = r"C:\Users\ankit\Downloads\Datasets\StudentsPerformance.csv"

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ML_ARTIFACTS_DIR, exist_ok=True)
