"""
Model Comparison & Visualization Script for EduPilot AI.
Compares RF, XGBoost, SVM, KNN, Decision Tree, Logistic Regression.
Generates plots: confusion matrix, ROC curve, feature importance, model comparison.
"""
import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, label_binarize
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    confusion_matrix, classification_report, roc_curve, auc,
    mean_squared_error, mean_absolute_error, r2_score,
)
from xgboost import XGBClassifier, XGBRegressor

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ml.dataset_generator import generate_dataset, FEATURE_COLS, SUBJECT_COLS
from config import KAGGLE_DATA_PATH

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docs", "plots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Dark theme for all plots ──
plt.rcParams.update({
    'figure.facecolor': '#0a0e1a',
    'axes.facecolor': '#111827',
    'axes.edgecolor': '#334155',
    'text.color': '#f1f5f9',
    'axes.labelcolor': '#94a3b8',
    'xtick.color': '#64748b',
    'ytick.color': '#64748b',
    'grid.color': '#1e293b',
    'font.family': 'sans-serif',
    'font.size': 10,
})

COLORS = ['#667eea', '#764ba2', '#22d3ee', '#10b981', '#f59e0b', '#ef4444']


def load_data():
    """Load and prepare dataset."""
    df = generate_dataset()
    X = df[FEATURE_COLS]
    y_score = df['final_score']
    y_class = df['pass_fail']
    return X, y_score, y_class, df


def compare_classifiers(X, y):
    """Compare multiple classification models."""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    models = {
        'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42),
        'XGBoost': XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1, eval_metric='logloss', random_state=42),
        'Decision Tree': DecisionTreeClassifier(max_depth=10, random_state=42),
        'SVM': SVC(kernel='rbf', probability=True, random_state=42),
        'KNN': KNeighborsClassifier(n_neighbors=7),
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    }

    results = {}
    trained_models = {}

    for name, model in models.items():
        print(f"  Training {name}...")
        # Use scaled data for SVM, KNN, LR; raw for tree-based
        use_scaled = name in ('SVM', 'KNN', 'Logistic Regression')
        Xtr = X_train_s if use_scaled else X_train
        Xte = X_test_s if use_scaled else X_test

        model.fit(Xtr, y_train)
        y_pred = model.predict(Xte)
        y_prob = model.predict_proba(Xte)[:, 1] if hasattr(model, 'predict_proba') else None

        # Cross-validation
        cv_scores = cross_val_score(model, Xtr, y_train, cv=5, scoring='accuracy')

        results[name] = {
            'accuracy': accuracy_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'y_pred': y_pred,
            'y_prob': y_prob,
        }
        trained_models[name] = model
        print(f"    Accuracy: {results[name]['accuracy']:.4f} | F1: {results[name]['f1']:.4f}")

    return results, trained_models, X_test, X_test_s, y_test


def compare_regressors(X, y):
    """Compare regression models."""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    models = {
        'Random Forest': RandomForestRegressor(n_estimators=200, max_depth=12, random_state=42),
        'XGBoost': XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42),
    }

    reg_results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        reg_results[name] = {
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred),
        }

    return reg_results


def run_hyperparameter_tuning(X, y):
    """Run GridSearchCV on XGBoost."""
    print("\n[Tuning] Running GridSearchCV on XGBoost...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [4, 6, 8],
        'learning_rate': [0.05, 0.1, 0.2],
    }

    grid = GridSearchCV(
        XGBClassifier(eval_metric='logloss', random_state=42),
        param_grid, cv=3, scoring='f1', n_jobs=-1, verbose=0
    )
    grid.fit(X_train, y_train)

    print(f"  Best params: {grid.best_params_}")
    print(f"  Best F1: {grid.best_score_:.4f}")

    return grid.best_params_, grid.best_score_


# ── PLOTTING FUNCTIONS ──

def plot_model_comparison(results):
    """Bar chart comparing all models."""
    fig, ax = plt.subplots(figsize=(12, 6))
    names = list(results.keys())
    metrics = ['accuracy', 'f1', 'precision', 'recall']
    x = np.arange(len(names))
    width = 0.2

    for i, metric in enumerate(metrics):
        values = [results[n][metric] for n in names]
        bars = ax.bar(x + i * width, values, width, label=metric.capitalize(), color=COLORS[i], alpha=0.85)
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=7, color='#94a3b8')

    ax.set_xlabel('Model')
    ax.set_ylabel('Score')
    ax.set_title('Classification Model Comparison', fontsize=14, fontweight='bold', color='#f1f5f9')
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(names, rotation=15)
    ax.set_ylim(0, 1.08)
    ax.legend(loc='lower right', facecolor='#1e293b', edgecolor='#334155')
    ax.grid(axis='y', alpha=0.2)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'model_comparison.png'), dpi=150)
    plt.close()
    print("[Plot] model_comparison.png saved")


def plot_confusion_matrices(results, y_test):
    """Confusion matrices for all models."""
    n = len(results)
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for idx, (name, res) in enumerate(results.items()):
        cm = confusion_matrix(y_test, res['y_pred'])
        ax = axes[idx]
        im = ax.imshow(cm, cmap='Blues', alpha=0.8)
        ax.set_title(name, fontsize=11, fontweight='bold', color='#f1f5f9')
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(cm[i, j]), ha='center', va='center', fontsize=14, fontweight='bold', color='#f1f5f9')
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(['Fail', 'Pass'])
        ax.set_yticklabels(['Fail', 'Pass'])

    plt.suptitle('Confusion Matrices — All Models', fontsize=14, fontweight='bold', color='#f1f5f9')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'confusion_matrices.png'), dpi=150)
    plt.close()
    print("[Plot] confusion_matrices.png saved")


def plot_roc_curves(results, y_test):
    """ROC curves for models that support probability."""
    fig, ax = plt.subplots(figsize=(8, 6))

    for idx, (name, res) in enumerate(results.items()):
        if res['y_prob'] is not None:
            fpr, tpr, _ = roc_curve(y_test, res['y_prob'])
            roc_auc = auc(fpr, tpr)
            ax.plot(fpr, tpr, color=COLORS[idx % len(COLORS)], linewidth=2,
                    label=f'{name} (AUC = {roc_auc:.3f})')

    ax.plot([0, 1], [0, 1], 'w--', alpha=0.3, linewidth=1)
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curves — Model Comparison', fontsize=14, fontweight='bold', color='#f1f5f9')
    ax.legend(loc='lower right', facecolor='#1e293b', edgecolor='#334155')
    ax.grid(alpha=0.15)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'roc_curves.png'), dpi=150)
    plt.close()
    print("[Plot] roc_curves.png saved")


def plot_feature_importance(X, y):
    """Feature importance from Random Forest."""
    model = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42)
    model.fit(X, y)
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(range(len(indices)), importances[indices], color=COLORS[0], alpha=0.85)
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels([FEATURE_COLS[i] for i in indices])
    ax.set_xlabel('Importance')
    ax.set_title('Feature Importance (Random Forest)', fontsize=14, fontweight='bold', color='#f1f5f9')
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.15)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'feature_importance.png'), dpi=150)
    plt.close()
    print("[Plot] feature_importance.png saved")


def plot_cv_comparison(results):
    """Cross-validation scores comparison."""
    fig, ax = plt.subplots(figsize=(10, 5))
    names = list(results.keys())
    means = [results[n]['cv_mean'] for n in names]
    stds = [results[n]['cv_std'] for n in names]

    bars = ax.bar(names, means, yerr=stds, capsize=5, color=COLORS[:len(names)], alpha=0.85,
                  error_kw={'ecolor': '#94a3b8', 'linewidth': 1.5})
    for bar, m, s in zip(bars, means, stds):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + s + 0.005,
                f'{m:.4f}', ha='center', va='bottom', fontsize=9, color='#f1f5f9')

    ax.set_ylabel('Accuracy')
    ax.set_title('5-Fold Cross-Validation Comparison', fontsize=14, fontweight='bold', color='#f1f5f9')
    ax.set_ylim(0.85, 1.02)
    ax.grid(axis='y', alpha=0.15)
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'cv_comparison.png'), dpi=150)
    plt.close()
    print("[Plot] cv_comparison.png saved")


def plot_score_distribution(df):
    """Distribution of final scores."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Score histogram
    axes[0].hist(df['final_score'], bins=30, color=COLORS[0], alpha=0.7, edgecolor='#334155')
    axes[0].axvline(df['final_score'].mean(), color=COLORS[2], linestyle='--', linewidth=2, label=f"Mean: {df['final_score'].mean():.1f}")
    axes[0].set_xlabel('Final Score')
    axes[0].set_ylabel('Count')
    axes[0].set_title('Score Distribution', fontsize=12, fontweight='bold', color='#f1f5f9')
    axes[0].legend(facecolor='#1e293b', edgecolor='#334155')

    # Pass/Fail pie
    pass_counts = df['pass_fail'].value_counts()
    axes[1].pie(pass_counts, labels=['Pass', 'Fail'], colors=[COLORS[3], COLORS[5]],
                autopct='%1.1f%%', startangle=90, textprops={'color': '#f1f5f9', 'fontsize': 12})
    axes[1].set_title('Pass/Fail Distribution', fontsize=12, fontweight='bold', color='#f1f5f9')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'score_distribution.png'), dpi=150)
    plt.close()
    print("[Plot] score_distribution.png saved")


def plot_correlation_heatmap(df):
    """Feature correlation heatmap."""
    corr_cols = FEATURE_COLS + ['final_score']
    corr = df[corr_cols].corr()

    fig, ax = plt.subplots(figsize=(14, 10))
    im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
    ax.set_xticks(range(len(corr_cols)))
    ax.set_yticks(range(len(corr_cols)))
    ax.set_xticklabels(corr_cols, rotation=45, ha='right', fontsize=8)
    ax.set_yticklabels(corr_cols, fontsize=8)
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title('Feature Correlation Heatmap', fontsize=14, fontweight='bold', color='#f1f5f9')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'correlation_heatmap.png'), dpi=150)
    plt.close()
    print("[Plot] correlation_heatmap.png saved")


def plot_subject_boxplots(df):
    """Box plots for subject scores."""
    fig, ax = plt.subplots(figsize=(10, 5))
    data = [df[s].values for s in SUBJECT_COLS]
    bp = ax.boxplot(data, patch_artist=True, labels=[s.capitalize() for s in SUBJECT_COLS])
    for i, patch in enumerate(bp['boxes']):
        patch.set_facecolor(COLORS[i % len(COLORS)])
        patch.set_alpha(0.7)
    for median in bp['medians']:
        median.set_color('#f1f5f9')
    ax.set_ylabel('Score')
    ax.set_title('Subject Score Distributions', fontsize=14, fontweight='bold', color='#f1f5f9')
    ax.grid(axis='y', alpha=0.15)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'subject_boxplots.png'), dpi=150)
    plt.close()
    print("[Plot] subject_boxplots.png saved")


def main():
    print("=" * 60)
    print("EduPilot AI -- Model Comparison & Visualization")
    print("=" * 60)

    print("\n[1/7] Loading data...")
    X, y_score, y_class, df = load_data()
    print(f"  Dataset: {len(df)} students, {len(FEATURE_COLS)} features")

    print("\n[2/7] Comparing classification models...")
    clf_results, models, X_test, X_test_s, y_test = compare_classifiers(X, y_class)

    print("\n[3/7] Comparing regression models...")
    reg_results = compare_regressors(X, y_score)
    for name, res in reg_results.items():
        print(f"  {name}: RMSE={res['rmse']:.4f}, MAE={res['mae']:.4f}, R2={res['r2']:.4f}")

    print("\n[4/7] Hyperparameter tuning...")
    best_params, best_f1 = run_hyperparameter_tuning(X, y_class)

    print(f"\n[5/7] Generating plots to {OUTPUT_DIR}...")
    plot_model_comparison(clf_results)
    plot_confusion_matrices(clf_results, y_test)
    plot_roc_curves(clf_results, y_test)
    plot_feature_importance(X, y_class)
    plot_cv_comparison(clf_results)
    plot_score_distribution(df)
    plot_correlation_heatmap(df)
    plot_subject_boxplots(df)

    # Save summary JSON
    print("\n[6/7] Saving comparison results...")
    summary = {
        "classification": {name: {k: v for k, v in res.items() if k not in ('y_pred', 'y_prob')}
                          for name, res in clf_results.items()},
        "regression": reg_results,
        "best_hyperparameters": best_params,
        "best_tuned_f1": best_f1,
        "dataset_size": len(df),
        "n_features": len(FEATURE_COLS),
    }
    with open(os.path.join(OUTPUT_DIR, 'comparison_results.json'), 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    print("\n[7/7] Summary:")
    print(f"  {'Model':<22} {'Accuracy':>10} {'F1':>8} {'CV Mean':>10}")
    print(f"  {'-'*52}")
    for name, res in clf_results.items():
        print(f"  {name:<22} {res['accuracy']:>10.4f} {res['f1']:>8.4f} {res['cv_mean']:>10.4f}")

    print(f"\n  Best Hyperparams: {best_params}")
    print(f"  Tuned F1: {best_f1:.4f}")
    print(f"\n  Plots saved to: {OUTPUT_DIR}")
    print("=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
