"""
preprocessing.py
----------------
Data loading, cleaning, imputation, encoding, and feature engineering
for the CKD Early Diagnosis system.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings("ignore")


# ── Column metadata ────────────────────────────────────────────────────────────
CATEGORICAL_COLS = [
    "RedBloodCells", "PusCells", "PusCellClumps", "Bacteria",
    "Hypertension", "DiabetesMellitus", "CoronaryArteryDisease",
    "Appetite", "PedalEdema", "Anemia"
]

NUMERICAL_COLS = [
    "Age", "BloodPressure", "SpecificGravity", "Albumin", "Sugar",
    "BloodGlucose", "BloodUrea", "SerumCreatinine", "Sodium",
    "Potassium", "Hemoglobin", "PackedCellVolume", "WBCCount", "RBCCount"
]

DROP_COLS = ["PatientID"]
TARGET_COL = "CKD"


def load_data(path: str) -> pd.DataFrame:
    """Load raw CSV dataset."""
    df = pd.read_csv(path)
    # Standardise string columns (remove stray whitespace / tabs)
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip().str.lower()
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fixes known formatting issues in the UCI CKD dataset:
    - Replace '?' and 'nan' strings with np.nan
    - Drop irrelevant identifier columns
    """
    df = df.copy()
    df.drop(columns=[c for c in DROP_COLS if c in df.columns], inplace=True)

    # Replace textual missing markers
    df.replace({"?": np.nan, "nan": np.nan, "": np.nan}, inplace=True)

    # Coerce numerical columns
    for col in NUMERICAL_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def impute_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Imputation strategy:
    - Numerical  → median (robust to outliers in medical data)
    - Categorical → most-frequent (mode)
    """
    df = df.copy()

    num_cols  = [c for c in NUMERICAL_COLS  if c in df.columns]
    cat_cols  = [c for c in CATEGORICAL_COLS if c in df.columns]

    # Numerical imputation
    num_imp = SimpleImputer(strategy="median")
    df[num_cols] = num_imp.fit_transform(df[num_cols])

    # Categorical imputation
    cat_imp = SimpleImputer(strategy="most_frequent")
    df[cat_cols] = cat_imp.fit_transform(df[cat_cols])

    return df


def encode_categoricals(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Label-encode binary / ordinal categorical columns.
    Returns the encoded DataFrame and a dict of fitted LabelEncoders.
    """
    df = df.copy()
    encoders = {}
    cat_cols = [c for c in CATEGORICAL_COLS if c in df.columns]

    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le

    # Encode target
    df[TARGET_COL] = (df[TARGET_COL].astype(str).str.strip() == "ckd").astype(int)

    return df, encoders


def scale_features(X_train: pd.DataFrame, X_test: pd.DataFrame) -> tuple:
    """
    StandardScaler fit on train, applied to both train and test.
    Returns scaled arrays and the fitted scaler.
    """
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)
    return X_train_sc, X_test_sc, scaler


def full_pipeline(path: str) -> tuple:
    """
    End-to-end preprocessing pipeline.
    Returns: X (DataFrame), y (Series), feature_names (list)
    """
    df = load_data(path)
    df = clean_data(df)
    df = impute_data(df)
    df, encoders = encode_categoricals(df)

    feature_cols = [c for c in df.columns if c != TARGET_COL]
    X = df[feature_cols]
    y = df[TARGET_COL]

    return X, y, feature_cols, encoders
