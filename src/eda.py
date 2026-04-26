"""
eda.py
------
Exploratory Data Analysis helpers.
Generates plots saved to /notebooks/eda_plots/
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

PLOT_DIR = os.path.join(os.path.dirname(__file__), "..", "notebooks", "eda_plots")
os.makedirs(PLOT_DIR, exist_ok=True)


def save(fig: plt.Figure, name: str):
    path = os.path.join(PLOT_DIR, name)
    fig.savefig(path, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  Saved → {path}")


def class_distribution(df: pd.DataFrame, target: str = "CKD"):
    counts = df[target].value_counts()
    fig, ax = plt.subplots(figsize=(6, 4))
    counts.plot(kind="bar", ax=ax, color=["#E74C3C", "#2ECC71"], edgecolor="white")
    ax.set_title("CKD Class Distribution", fontsize=14, fontweight="bold")
    ax.set_xlabel("Class"); ax.set_ylabel("Count")
    for p in ax.patches:
        ax.annotate(str(int(p.get_height())),
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha="center", va="bottom", fontweight="bold")
    save(fig, "01_class_distribution.png")


def numerical_distributions(df: pd.DataFrame, num_cols: list, target: str = "CKD"):
    """KDE plot for each numerical feature, coloured by class."""
    n = len(num_cols)
    cols = 4
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 3))
    axes = axes.flatten()
    for i, col in enumerate(num_cols):
        for cls in df[target].unique():
            subset = df[df[target] == cls][col].dropna()
            axes[i].hist(subset, alpha=0.6, bins=20, label=str(cls), density=True)
        axes[i].set_title(col, fontsize=9)
        axes[i].legend(fontsize=7)
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)
    fig.suptitle("Numerical Feature Distributions by CKD Status", fontsize=13, fontweight="bold")
    plt.tight_layout()
    save(fig, "02_numerical_distributions.png")


def correlation_heatmap(df: pd.DataFrame, num_cols: list):
    corr = df[num_cols].corr()
    fig, ax = plt.subplots(figsize=(12, 9))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
                linewidths=0.5, ax=ax, annot_kws={"size": 7})
    ax.set_title("Feature Correlation Heatmap", fontsize=14, fontweight="bold")
    save(fig, "03_correlation_heatmap.png")


def feature_importance_plot(df: pd.DataFrame, feature_cols: list, target: str = "CKD"):
    """Quick RF feature importance on label-encoded data."""
    X = df[feature_cols].copy()
    y = (df[target].astype(str).str.strip() == "ckd").astype(int)

    for col in X.select_dtypes(include="object").columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].fillna("missing").astype(str))
    X.fillna(X.median(), inplace=True)

    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X, y)

    imp = pd.Series(rf.feature_importances_, index=feature_cols).sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(8, 9))
    imp.plot(kind="barh", ax=ax, color="#3498DB")
    ax.set_title("Random Forest Feature Importances", fontsize=14, fontweight="bold")
    ax.set_xlabel("Importance Score")
    save(fig, "04_feature_importance.png")


def run_all_eda(raw_df: pd.DataFrame):
    from preprocessing import NUMERICAL_COLS, CATEGORICAL_COLS
    print("\n📊 Running EDA ...")
    num_cols  = [c for c in NUMERICAL_COLS  if c in raw_df.columns]
    all_feats = [c for c in raw_df.columns if c not in ("CKD", "PatientID")]

    class_distribution(raw_df)
    numerical_distributions(raw_df, num_cols)
    correlation_heatmap(raw_df, num_cols)
    feature_importance_plot(raw_df, all_feats)
    print("✅ EDA complete.")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from preprocessing import load_data
    DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ckd_dataset_with_id.csv")
    raw = load_data(DATA_PATH)
    run_all_eda(raw)
