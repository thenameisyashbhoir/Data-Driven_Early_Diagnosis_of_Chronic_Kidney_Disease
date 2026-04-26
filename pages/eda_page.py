"""
pages/eda_page.py  ──  Exploratory Data Analysis Page
"""
import streamlit as st
import os
from utils.styles import inject_css, page_header


def render():
    inject_css()
    page_header("🔍", "Data Insights",
                "Exploratory Data Analysis — distributions, correlations, and feature importance")

    PLOT_DIR = os.path.join(os.path.dirname(__file__), "..", "notebooks", "eda_plots")
    plot_map = {
        "01 — Class Distribution"              : "01_class_distribution.png",
        "02 — Numerical Feature Distributions" : "02_numerical_distributions.png",
        "03 — Correlation Heatmap"             : "03_correlation_heatmap.png",
        "04 — Feature Importances (RF)"        : "04_feature_importance.png",
    }

    if not os.path.isdir(PLOT_DIR) or not os.listdir(PLOT_DIR):
        st.markdown("""
        <div class="warn-box">
          ⚠️ EDA plots not yet generated. Click the button below to generate them.
        </div>""", unsafe_allow_html=True)
        if st.button("🚀 Generate EDA Plots"):
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
            from eda import run_all_eda
            from preprocessing import load_data
            DATA = os.path.join(os.path.dirname(__file__), "..", "data",
                                "ckd_dataset_with_id.csv")
            with st.spinner("Running EDA …"):
                run_all_eda(load_data(DATA))
            st.success("✅ EDA plots generated!")
            st.rerun()
        return

    # ── EDA descriptions ───────────────────────────────────────────────────────
    descriptions = {
        "01 — Class Distribution": (
            "Shows the distribution of CKD vs Non-CKD cases. Our dataset has 250 CKD "
            "patients (62.5%) and 150 Non-CKD patients (37.5%), indicating mild class imbalance "
            "which was addressed through stratified splits and recall-optimised training."
        ),
        "02 — Numerical Feature Distributions": (
            "KDE plots comparing the distribution of each numerical feature across CKD and "
            "Non-CKD patients. Key findings: Serum Creatinine and Blood Urea are markedly higher "
            "in CKD patients, while Hemoglobin and Packed Cell Volume are significantly lower."
        ),
        "03 — Correlation Heatmap": (
            "Pearson correlation matrix of all numerical features. Strong positive correlation "
            "between Hemoglobin and Packed Cell Volume (r≈0.96). High Serum Creatinine and Blood "
            "Urea are strongly correlated with each other and with CKD presence."
        ),
        "04 — Feature Importances (RF)": (
            "Random Forest feature importances identify the most discriminative features. "
            "Specific Gravity, Hemoglobin, Serum Creatinine, Albumin, and Packed Cell Volume "
            "are the top predictors — consistent with clinical nephrological knowledge."
        ),
    }

    selected = st.selectbox("📊 Select EDA Plot", list(plot_map.keys()))

    img_path = os.path.join(PLOT_DIR, plot_map[selected])
    if os.path.exists(img_path):
        st.markdown(f"""
        <div class="info-box">
          📖 <strong>Interpretation:</strong> {descriptions.get(selected, "")}
        </div>
        """, unsafe_allow_html=True)
        st.image(img_path, use_container_width=True)
    else:
        st.warning(f"Plot file not found: {plot_map[selected]}")

    # ── Key Dataset Facts ──────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">📋 Key EDA Findings</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="ckd-card">
          <div style="font-family:'Syne',sans-serif; font-size:0.9rem;
                      font-weight:700; color:#00D4FF; margin-bottom:10px;">
            🔑 Top Predictive Features
          </div>
          <div style="font-size:0.83rem; color:#E8F0FE; line-height:1.9;">
            1. <span style="color:#FF3B5C;">Specific Gravity</span> — most important (RF importance)<br>
            2. <span style="color:#FF3B5C;">Hemoglobin</span> — significantly lower in CKD<br>
            3. <span style="color:#FF3B5C;">Serum Creatinine</span> — elevated in CKD<br>
            4. <span style="color:#FF8C42;">Albumin</span> — protein in urine indicates damage<br>
            5. <span style="color:#FF8C42;">Packed Cell Volume</span> — anaemia marker<br>
            6. <span style="color:#FFD166;">Hypertension</span> — co-morbidity indicator
          </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="ckd-card">
          <div style="font-family:'Syne',sans-serif; font-size:0.9rem;
                      font-weight:700; color:#00D4FF; margin-bottom:10px;">
            📊 Missing Value Strategy
          </div>
          <div style="font-size:0.83rem; color:#E8F0FE; line-height:1.9;">
            <span style="color:#00E5A0;">Numerical features</span><br>
            → Median imputation (robust to outliers in medical data)<br><br>
            <span style="color:#00E5A0;">Categorical features</span><br>
            → Mode imputation (most frequent class preserved)<br><br>
            <span style="color:#FFD166;">Rationale:</span> Median is preferred over mean in
            clinical data due to skewed distributions (e.g., creatinine levels).
          </div>
        </div>
        """, unsafe_allow_html=True)
