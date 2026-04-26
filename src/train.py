"""
train.py - Model training pipeline for CKD Early Diagnosis System
"""
import os, sys, pickle
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report
import warnings; warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(__file__))
from preprocessing import full_pipeline, scale_features

DATA_PATH  = os.path.join(os.path.dirname(__file__), "..", "data", "ckd_dataset_with_id.csv")
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(MODELS_DIR, exist_ok=True)


def get_model_configs():
    configs = {
        "Logistic Regression": {
            "model": LogisticRegression(max_iter=1000, random_state=42),
            "params": {"C": [0.01, 0.1, 1, 10], "solver": ["lbfgs", "liblinear"]}
        },
        "Random Forest": {
            "model": RandomForestClassifier(random_state=42),
            "params": {"n_estimators": [100, 200], "max_depth": [None, 5, 10], "min_samples_split": [2, 5]}
        },
        "Gradient Boosting": {
            "model": GradientBoostingClassifier(random_state=42),
            "params": {"n_estimators": [100, 200], "max_depth": [3, 5], "learning_rate": [0.05, 0.1, 0.2]}
        },
        "SVM": {
            "model": SVC(probability=True, random_state=42),
            "params": {"C": [0.1, 1, 10], "kernel": ["rbf", "linear"], "gamma": ["scale", "auto"]}
        }
    }
    if HAS_XGB:
        configs["XGBoost"] = {
            "model": XGBClassifier(eval_metric="logloss", random_state=42),
            "params": {"n_estimators": [100, 200], "max_depth": [3, 5], "learning_rate": [0.05, 0.1]}
        }
    return configs


def evaluate_model(model, X_test, y_test, model_name):
    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    metrics = {
        "Model"    : model_name,
        "Accuracy" : round(accuracy_score(y_test, y_pred),  4),
        "Precision": round(precision_score(y_test, y_pred), 4),
        "Recall"   : round(recall_score(y_test, y_pred),    4),
        "F1 Score" : round(f1_score(y_test, y_pred),        4),
        "ROC-AUC"  : round(roc_auc_score(y_test, y_proba),  4),
    }
    print(f"\n{'='*52}\n  {model_name}\n{'='*52}")
    for k, v in metrics.items():
        if k != "Model": print(f"  {k:12s}: {v}")
    print("\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["No CKD", "CKD"]))
    print("  Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
    return metrics


def train_all_models():
    print("\n🔬 Loading and preprocessing data ...")
    X, y, feature_names, encoders = full_pipeline(DATA_PATH)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    X_train_sc, X_test_sc, scaler = scale_features(X_train, X_test)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    all_metrics, trained_models = [], {}

    for name, cfg in get_model_configs().items():
        print(f"\n🤖 Training {name} ...")
        gs = GridSearchCV(cfg["model"], cfg["params"], scoring="recall", cv=cv, n_jobs=-1, verbose=0)
        gs.fit(X_train_sc, y_train)
        best = gs.best_estimator_
        cv_scores = cross_val_score(best, X_train_sc, y_train, cv=cv, scoring="recall")
        print(f"  Best params : {gs.best_params_}")
        print(f"  CV Recall   : {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")
        metrics = evaluate_model(best, X_test_sc, y_test, name)
        all_metrics.append(metrics)
        trained_models[name] = best

    results_df = pd.DataFrame(all_metrics).set_index("Model")
    print("\n\n📊 Model Comparison Summary:\n", results_df.to_string())
    best_name  = results_df["ROC-AUC"].idxmax()
    best_model = trained_models[best_name]
    print(f"\n🏆 Best model: {best_name}  (ROC-AUC = {results_df.loc[best_name,'ROC-AUC']})")

    artefacts = {
        "best_model": best_model, "best_name": best_name,
        "all_models": trained_models, "scaler": scaler,
        "encoders": encoders, "feature_names": feature_names,
        "results_df": results_df, "X_train": X_train_sc,
    }
    save_path = os.path.join(MODELS_DIR, "ckd_artefacts.pkl")
    with open(save_path, "wb") as f:
        pickle.dump(artefacts, f)
    print(f"\n✅ Artefacts saved → {save_path}")
    return artefacts


if __name__ == "__main__":
    train_all_models()
