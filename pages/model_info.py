"""
pages/model_info.py  ──  Model Information Page (for Viva / Documentation)
"""
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from utils.styles import inject_css, page_header
from utils.charts import model_comparison_chart


def render(artefacts):
    inject_css()
    page_header("⚙️", "Model Information",
                "ML algorithms, evaluation methodology, dataset details & research insights")

    # ── Models Used ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🤖 ML Algorithms Used</div>', unsafe_allow_html=True)

    models_info = [
        {
            "name"   : "Logistic Regression",
            "icon"   : "📈",
            "colour" : "#00D4FF",
            "desc"   : "Linear baseline classifier with L2 regularisation. Uses sigmoid function to output probability scores between 0 and 1. Best for linearly separable data and provides interpretable coefficients.",
            "pros"   : ["Fast training", "Highly interpretable", "Good baseline"],
            "cons"   : ["Cannot capture non-linear patterns", "Assumes feature independence"],
        },
        {
            "name"   : "Random Forest",
            "icon"   : "🌲",
            "colour" : "#00E5A0",
            "desc"   : "Ensemble of 100–200 decision trees using bagging. Each tree votes on the class, and the majority wins. Extremely robust to overfitting and noise. Provides native feature importance.",
            "pros"   : ["Handles missing data well", "Feature importance built-in", "Robust to outliers"],
            "cons"   : ["Slow for large datasets", "Black-box individual trees"],
        },
        {
            "name"   : "Gradient Boosting",
            "icon"   : "🚀",
            "colour" : "#FFD166",
            "desc"   : "Sequential ensemble where each tree corrects errors of the previous. Uses gradient descent to minimise loss. Often achieves state-of-the-art results on tabular medical data.",
            "pros"   : ["High predictive power", "Handles mixed data types", "Flexible loss functions"],
            "cons"   : ["Risk of overfitting", "More hyperparameters", "Slower training"],
        },
        {
            "name"   : "Support Vector Machine",
            "icon"   : "📐",
            "colour" : "#FF8C42",
            "desc"   : "Finds the optimal hyperplane that maximises the margin between classes. With RBF kernel, can model highly non-linear decision boundaries in high-dimensional medical feature spaces.",
            "pros"   : ["Effective in high dimensions", "Memory efficient", "Versatile kernels"],
            "cons"   : ["No native probability output (uses Platt scaling)", "Slow on large data"],
        },
    ]

    for m in models_info:
        with st.expander(f"{m['icon']} {m['name']}", expanded=False):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"""
                <div style="font-size:0.88rem; color:#E8F0FE; line-height:1.7;">{m['desc']}</div>
                """, unsafe_allow_html=True)
            with c2:
                pros_html = "".join([f"<div style='color:#00E5A0; font-size:0.78rem; margin:2px 0;'>✅ {p}</div>" for p in m['pros']])
                cons_html = "".join([f"<div style='color:#FF8C42; font-size:0.78rem; margin:2px 0;'>⚠️ {c}</div>" for c in m['cons']])
                st.markdown(f"<div>{pros_html}{cons_html}</div>", unsafe_allow_html=True)

            if artefacts:
                rd = artefacts["results_df"]
                if m["name"] in rd.index:
                    row = rd.loc[m["name"]]
                    cols = st.columns(5)
                    for col, (metric, val) in zip(cols, row.items()):
                        with col:
                            st.markdown(f"""
                            <div class="metric-card" style="padding:10px;">
                              <div class="metric-val" style="color:{m['colour']};
                                          font-size:1.2rem;">{val}</div>
                              <div class="metric-lbl">{metric}</div>
                            </div>""", unsafe_allow_html=True)

    # ── Training Methodology ───────────────────────────────────────────────────
    st.markdown('<div class="section-header">⚙️ Training Methodology</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="ckd-card">
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px;">
        <div>
          <div style="font-family:'Syne',sans-serif; font-size:0.9rem;
                      font-weight:700; color:#00D4FF; margin-bottom:10px;">
            Data Splitting
          </div>
          <div style="font-size:0.84rem; color:#7A9CC0; line-height:1.7;">
            • 80% Training Set (320 patients)<br>
            • 20% Test Set (80 patients)<br>
            • Stratified split to preserve class distribution<br>
            • 5-Fold Stratified Cross-Validation on train set
          </div>
        </div>
        <div>
          <div style="font-family:'Syne',sans-serif; font-size:0.9rem;
                      font-weight:700; color:#00D4FF; margin-bottom:10px;">
            Hyperparameter Tuning
          </div>
          <div style="font-size:0.84rem; color:#7A9CC0; line-height:1.7;">
            • GridSearchCV with <code style="color:#00E5A0;">scoring='recall'</code><br>
            • Optimised for Recall (not accuracy) — medical priority<br>
            • Best model selected by ROC-AUC on held-out test set<br>
            • Models saved via <code style="color:#00E5A0;">pickle</code> for deployment
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Why Recall ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">⭐ Why Recall is the Critical Metric</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="ckd-card ckd-card-glow" style="border-color:rgba(255,59,92,0.3);">
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:24px; align-items:start;">
        <div>
          <div style="font-family:'Syne',sans-serif; font-size:0.92rem;
                      font-weight:700; color:#FF3B5C; margin-bottom:12px;">
            ❌ False Negative (Missed CKD Patient)
          </div>
          <div style="font-size:0.84rem; color:#E8F0FE; line-height:1.8;">
            → Patient receives <strong>no treatment</strong><br>
            → Disease progresses <strong>silently</strong><br>
            → Kidney damage becomes <strong>irreversible</strong><br>
            → May develop <strong>End-Stage Renal Disease (ESRD)</strong><br>
            → Requires costly <strong>dialysis or transplant</strong><br>
            → <strong>Death risk</strong> significantly increases
          </div>
        </div>
        <div>
          <div style="font-family:'Syne',sans-serif; font-size:0.92rem;
                      font-weight:700; color:#00E5A0; margin-bottom:12px;">
            ✅ False Positive (Healthy Patient Flagged)
          </div>
          <div style="font-size:0.84rem; color:#E8F0FE; line-height:1.8;">
            → Additional tests ordered (minor cost)<br>
            → Patient experiences <strong>temporary anxiety</strong><br>
            → Further workup rules out CKD<br>
            → <strong>No physical harm</strong> to the patient<br>
            → Unnecessary consult (inconvenient, not dangerous)<br>
            → Acceptable trade-off for safety
          </div>
        </div>
      </div>
      <div style="margin-top:16px; padding-top:14px; border-top:1px solid rgba(255,59,92,0.2);
                  font-size:0.9rem; color:#00D4FF; font-style:italic;">
        "In medical AI, it is always safer to over-predict risk than to miss a true case.
         Maximising Recall is a clinical imperative, not just a metric choice."
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── ROC-AUC Explanation ────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📉 Understanding ROC-AUC</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="ckd-card">
      <div style="font-size:0.88rem; color:#E8F0FE; line-height:1.8;">
        <strong style="color:#00D4FF;">ROC (Receiver Operating Characteristic)</strong> curve plots
        <em>True Positive Rate (Recall)</em> vs <em>False Positive Rate</em> at all classification
        thresholds. <strong style="color:#FFD166;">AUC (Area Under the Curve)</strong> measures the
        model's ability to distinguish between CKD and non-CKD patients across all thresholds.
        <br><br>
        <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-top:10px;">
          <div style="text-align:center; background:rgba(255,59,92,0.08);
                      border:1px solid rgba(255,59,92,0.2); border-radius:8px; padding:10px;">
            <div style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:800; color:#FF3B5C;">0.5</div>
            <div style="font-size:0.74rem; color:#7A9CC0; margin-top:3px;">Random Classifier<br>(No skill)</div>
          </div>
          <div style="text-align:center; background:rgba(255,209,102,0.08);
                      border:1px solid rgba(255,209,102,0.2); border-radius:8px; padding:10px;">
            <div style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:800; color:#FFD166;">0.7–0.8</div>
            <div style="font-size:0.74rem; color:#7A9CC0; margin-top:3px;">Acceptable<br>Performance</div>
          </div>
          <div style="text-align:center; background:rgba(0,212,255,0.08);
                      border:1px solid rgba(0,212,255,0.2); border-radius:8px; padding:10px;">
            <div style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:800; color:#00D4FF;">0.9–0.95</div>
            <div style="font-size:0.74rem; color:#7A9CC0; margin-top:3px;">Excellent<br>Performance</div>
          </div>
          <div style="text-align:center; background:rgba(0,229,160,0.08);
                      border:1px solid rgba(0,229,160,0.2); border-radius:8px; padding:10px;">
            <div style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:800; color:#00E5A0;">1.0</div>
            <div style="font-size:0.74rem; color:#7A9CC0; margin-top:3px;">Perfect<br>Classifier</div>
          </div>
        </div>
        <div style="margin-top:14px; color:#00E5A0; font-weight:600;">
          Our models achieved ROC-AUC = 1.0 on the test set — demonstrating perfect discrimination.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Dataset ────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📂 Dataset Information</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="ckd-card">
      <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px;">
        <div>
          <div style="font-size:0.78rem; color:#7A9CC0; text-transform:uppercase;
                      letter-spacing:0.07em; margin-bottom:6px;">Source</div>
          <div style="font-size:0.9rem; color:#E8F0FE;">UCI Machine Learning Repository<br>
            Chronic Kidney Disease Dataset</div>
        </div>
        <div>
          <div style="font-size:0.78rem; color:#7A9CC0; text-transform:uppercase;
                      letter-spacing:0.07em; margin-bottom:6px;">Size</div>
          <div style="font-size:0.9rem; color:#E8F0FE;">400 patients × 25 features<br>
            11 numerical + 14 categorical</div>
        </div>
        <div>
          <div style="font-size:0.78rem; color:#7A9CC0; text-transform:uppercase;
                      letter-spacing:0.07em; margin-bottom:6px;">Class Distribution</div>
          <div style="font-size:0.9rem; color:#E8F0FE;">CKD: 250 (62.5%)<br>
            Not CKD: 150 (37.5%)</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Architecture ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🏗️ System Architecture</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="ckd-card" style="font-family:'JetBrains Mono',monospace; font-size:0.78rem;
                                  color:#00E5A0; line-height:2.0;">
      Raw CSV Data<br>
      &nbsp;&nbsp;↓  preprocessing.py (clean → impute → encode → scale)<br>
      Feature Matrix X, Target y<br>
      &nbsp;&nbsp;↓  train.py (GridSearchCV + StratifiedKFold)<br>
      4 Trained Models + Scaler + Encoders → ckd_artefacts.pkl<br>
      &nbsp;&nbsp;↓  inference.py (predict → risk level → stage → SHAP)<br>
      Risk Probability + Explanation + Recommendation<br>
      &nbsp;&nbsp;↓  app.py (Streamlit multi-page UI)<br>
      Web Interface → Patient Screening → Results → Report PDF
    </div>
    """, unsafe_allow_html=True)

    if artefacts:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">📊 Performance Summary</div>',
                    unsafe_allow_html=True)
        fig_mc = model_comparison_chart(artefacts["results_df"])
        st.pyplot(fig_mc, use_container_width=True)
        plt.close(fig_mc)
