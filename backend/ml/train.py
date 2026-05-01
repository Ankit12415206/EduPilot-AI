"""
Training pipeline for EduPilot AI.
Run this script to generate data, train models, and save artifacts.
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.dataset_generator import generate_dataset, save_dataset
from ml.predictor import PerformancePredictor
from config import ML_ARTIFACTS_DIR


def main():
    print("=" * 60)
    print("🎓 EduPilot AI — Training Pipeline")
    print("=" * 60)

    # Step 1: Generate dataset
    print("\n📦 Step 1: Generating combined dataset...")
    df = generate_dataset()
    save_dataset(df)

    # Step 2: Train models
    print("\n🤖 Step 2: Training ML models...")
    predictor = PerformancePredictor(ML_ARTIFACTS_DIR)
    metrics = predictor.train(df)

    # Step 3: Save models
    print("\n💾 Step 3: Saving model artifacts...")
    predictor.save()

    # Save metrics
    metrics_path = os.path.join(ML_ARTIFACTS_DIR, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"📊 Metrics saved to {metrics_path}")

    # Step 4: Quick test
    print("\n🧪 Step 4: Running prediction test...")
    test_features = {
        "gender_encoded": 0,
        "ethnicity_encoded": 2,
        "parent_education_encoded": 3,
        "lunch_encoded": 1,
        "test_prep_encoded": 1,
        "attendance_pct": 85.0,
        "study_hours_per_day": 4.5,
        "assignment_completion_pct": 80.0,
        "sleep_hours": 7.5,
        "social_media_hours": 1.5,
        "stress_level": 4,
        "extracurricular_hours": 3.0,
        "math": 75,
        "reading": 80,
        "writing": 78,
        "science": 72,
        "history": 70,
    }

    score_pred = predictor.predict_score(test_features)
    pass_pred = predictor.predict_pass_fail(test_features)
    importance = predictor.get_feature_importance()

    print(f"\n   Test Student Prediction:")
    print(f"   Predicted Score: {score_pred['predicted_score']}")
    print(f"   Pass Probability: {pass_pred['pass_probability']*100:.1f}%")
    print(f"   Prediction: {pass_pred['prediction']}")
    print(f"   Model Confidence: {score_pred['confidence']*100:.1f}%")

    print(f"\n   Top 5 Important Features:")
    for feat in importance[:5]:
        print(f"   - {feat['feature']}: {feat['importance']:.4f}")

    # Step 5: Feature importance
    fi_path = os.path.join(ML_ARTIFACTS_DIR, "feature_importance.json")
    with open(fi_path, "w") as f:
        json.dump(importance, f, indent=2)
    print(f"\n📊 Feature importance saved to {fi_path}")

    print("\n" + "=" * 60)
    print("✅ Training pipeline complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
