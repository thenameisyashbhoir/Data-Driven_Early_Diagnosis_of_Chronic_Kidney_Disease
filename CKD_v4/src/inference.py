"""
inference.py - Prediction engine for the CKD Early Diagnosis system.
"""
import pickle, os, sys
import numpy as np
import pandas as pd

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
ARTEFACTS_PATH = os.path.join(MODELS_DIR, "ckd_artefacts.pkl")

LOW_THRESHOLD      = 0.30
MODERATE_THRESHOLD = 0.60


def load_artefacts(path=ARTEFACTS_PATH):
    with open(path, "rb") as f:
        return pickle.load(f)


def get_risk_level(prob):
    if prob < LOW_THRESHOLD:      return "Low Risk"
    elif prob < MODERATE_THRESHOLD: return "Moderate Risk"
    return "High Risk"


def get_risk_emoji(prob):
    if prob < LOW_THRESHOLD:      return "🟢"
    elif prob < MODERATE_THRESHOLD: return "🟡"
    return "🔴"


def estimate_ckd_stage(prob, serum_creatinine=1.0, hemoglobin=13.0):
    if prob < 0.30: return "No CKD Detected"
    if prob < 0.45: return "Stage 1 – Kidney damage with normal function (eGFR ≥ 90)"
    if prob < 0.60: return "Stage 2 – Mildly reduced function (eGFR 60–89)"
    if prob < 0.75:
        if serum_creatinine > 3.5 or hemoglobin < 9:
            return "Stage 4 – Severely reduced function (eGFR 15–29)"
        return "Stage 3 – Moderately reduced function (eGFR 30–59)"
    return "Stage 5 – Kidney failure / End-stage (eGFR < 15)"


def get_recommendation(risk_level):
    recs = {
        "Low Risk": (
            "✅ No immediate concern.\n"
            "• Maintain a healthy diet low in sodium and processed foods.\n"
            "• Stay hydrated and exercise regularly.\n"
            "• Annual kidney function check-up recommended."
        ),
        "Moderate Risk": (
            "⚠️ Moderate CKD risk detected.\n"
            "• Consult a nephrologist within the next 1–2 months.\n"
            "• Monitor blood pressure and blood glucose closely.\n"
            "• Reduce protein intake and avoid nephrotoxic medications (NSAIDs).\n"
            "• Repeat blood tests (creatinine, eGFR) every 3–6 months."
        ),
        "High Risk": (
            "🚨 High CKD risk — URGENT medical attention required.\n"
            "• Seek specialist (nephrologist) consultation immediately.\n"
            "• Strict blood pressure control (target < 130/80 mmHg).\n"
            "• Initiate or adjust CKD-specific medications as prescribed.\n"
            "• Follow a renal diet (low potassium, phosphorus, and sodium).\n"
            "• Discuss dialysis or transplant eligibility if Stage 4–5."
        )
    }
    return recs.get(risk_level, "")


def compute_feature_importance(model, X_scaled_input, feature_names):
    """
    SHAP if available, else fall back to RF feature_importances_ or
    logistic regression coefficients.
    """
    model_type = type(model).__name__

    if HAS_SHAP:
        try:
            if model_type in ("RandomForestClassifier", "GradientBoostingClassifier", "XGBClassifier"):
                explainer = shap.TreeExplainer(model)
                shap_vals = explainer.shap_values(X_scaled_input)
                if isinstance(shap_vals, list):
                    shap_vals = shap_vals[1]
            else:
                background = shap.sample(X_scaled_input, min(50, len(X_scaled_input)))
                explainer  = shap.KernelExplainer(model.predict_proba, background)
                shap_vals  = explainer.shap_values(X_scaled_input)
                if isinstance(shap_vals, list):
                    shap_vals = shap_vals[1]

            vals = shap_vals.flatten()
            df = pd.DataFrame({
                "Feature"    : feature_names,
                "SHAP Value" : vals,
                "Impact"     : ["↑ Risk" if v > 0 else "↓ Risk" for v in vals]
            })
            df["|SHAP|"] = df["SHAP Value"].abs()
            return df.sort_values("|SHAP|", ascending=False).head(8).reset_index(drop=True), "shap"
        except Exception:
            pass

    # Fallback: RF importances or LR coefficients
    try:
        if hasattr(model, "feature_importances_"):
            vals = model.feature_importances_
        elif hasattr(model, "coef_"):
            vals = model.coef_[0]
        else:
            return pd.DataFrame(), "none"

        df = pd.DataFrame({
            "Feature"    : feature_names,
            "SHAP Value" : vals,
            "Impact"     : ["↑ Risk" if v > 0 else "↓ Risk" for v in vals]
        })
        df["|SHAP|"] = df["SHAP Value"].abs()
        return df.sort_values("|SHAP|", ascending=False).head(8).reset_index(drop=True), "importance"
    except Exception:
        return pd.DataFrame(), "none"


def build_explanation_text(top_features):
    if top_features.empty:
        return "Feature explanation unavailable."
    risk_up   = top_features[top_features["SHAP Value"] > 0]["Feature"].head(3).tolist()
    risk_down = top_features[top_features["SHAP Value"] < 0]["Feature"].head(2).tolist()
    parts = []
    if risk_up:
        parts.append(f"High {', '.join(risk_up)} significantly increased CKD risk.")
    if risk_down:
        parts.append(f"Low {', '.join(risk_down)} also contributed to the risk profile.")
    return " ".join(parts) or "No dominant contributing factors identified."


def predict(patient_data, artefacts, selected_model=None):
    feature_names = artefacts["feature_names"]
    scaler        = artefacts["scaler"]
    encoders      = artefacts["encoders"]

    if selected_model and selected_model in artefacts["all_models"]:
        model = artefacts["all_models"][selected_model]
    else:
        model = artefacts["best_model"]

    row     = {f: patient_data.get(f, 0) for f in feature_names}
    X_input = pd.DataFrame([row])

    for col, le in encoders.items():
        if col in X_input.columns:
            val = str(X_input.at[0, col]).lower().strip()
            if val not in le.classes_:
                val = le.classes_[0]
            X_input[col] = int(le.transform([val])[0])

    X_scaled = scaler.transform(X_input)
    prob     = float(model.predict_proba(X_scaled)[0, 1])

    risk_level = get_risk_level(prob)
    stage      = estimate_ckd_stage(prob,
                                    float(patient_data.get("SerumCreatinine", 1.0)),
                                    float(patient_data.get("Hemoglobin", 13.0)))
    rec        = get_recommendation(risk_level)

    top_feats, feat_method = compute_feature_importance(model, X_scaled, feature_names)
    explanation            = build_explanation_text(top_feats)

    return {
        "probability"     : prob,
        "risk_percent"    : round(prob * 100, 1),
        "risk_level"      : risk_level,
        "risk_emoji"      : get_risk_emoji(prob),
        "stage"           : stage,
        "recommendation"  : rec,
        "top_features"    : top_feats,
        "explanation_text": explanation,
        "feat_method"     : feat_method,
    }
