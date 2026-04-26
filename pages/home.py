"""
pages/home.py  ──  Home / Landing Page
"""
import streamlit as st
from utils.styles import inject_css, page_header, badge


def render():
    inject_css()

    # ── Hero ───────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding: 40px 20px 30px 20px;">
      <div style="display:inline-block; background:rgba(0,212,255,0.1);
                  border:1px solid rgba(0,212,255,0.3); border-radius:20px;
                  padding:4px 16px; font-size:0.75rem; color:#00D4FF;
                  letter-spacing:0.1em; text-transform:uppercase;
                  font-weight:600; margin-bottom:18px;">
        AI · Machine Learning · Early Detection
      </div>
      <div style="font-family:'Syne',sans-serif; font-size:2.8rem;
                  font-weight:800; line-height:1.15; color:#E8F0FE;
                  margin-bottom:16px;">
        Early Diagnosis of<br>
        <span style="color:#00D4FF;">Chronic Kidney Disease</span>
      </div>
      <div style="font-size:1.0rem; color:#7A9CC0; max-width:600px;
                  margin:0 auto 30px auto; line-height:1.7;">
        A research-grade AI system that detects CKD risk at early stages,
        provides probability-based risk scores, and delivers explainable
        insights — before irreversible damage occurs.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA
    col_l, col_cta, col_r = st.columns([2, 2, 2])
    with col_cta:
        if st.button("🔬 Start CKD Screening", use_container_width=True):
            st.session_state.current_page = "Screening"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Why Early Detection ────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-header">⚡ Why Early Detection Matters</div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    cards = [
        ("🔕", "Silent Progression",
         "CKD shows no symptoms in early stages. By the time symptoms appear, up to 90% of kidney function may already be lost."),
        ("⏱️", "Time-Critical",
         "Early-stage CKD (Stage 1–2) is reversible with lifestyle changes. Late-stage CKD requires dialysis or transplant."),
        ("💊", "Preventable",
         "With AI-powered early screening, high-risk patients can receive timely treatment, slowing or halting progression."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3], cards):
        with col:
            st.markdown(f"""
            <div class="ckd-card">
              <div style="font-size:1.8rem; margin-bottom:10px;">{icon}</div>
              <div style="font-family:'Syne',sans-serif; font-size:1.0rem;
                          font-weight:700; color:#00D4FF; margin-bottom:8px;">{title}</div>
              <div style="font-size:0.86rem; color:#7A9CC0; line-height:1.65;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CKD Statistics ────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Global CKD Burden</div>', unsafe_allow_html=True)

    stats_cols = st.columns(4)
    stats = [
        ("850M+",  "People affected globally",       "#00D4FF"),
        ("10th",   "Leading cause of death worldwide","#FF3B5C"),
        ("90%",    "Cases undiagnosed in early stage","#FF8C42"),
        ("Stage 1–2", "Optimal intervention window", "#00E5A0"),
    ]
    for col, (val, lbl, clr) in zip(stats_cols, stats):
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-val" style="color:{clr};">{val}</div>
              <div class="metric-lbl">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── How It Works ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">⚙️ How This System Works</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="ckd-card">
      <div style="display:flex; gap:0; align-items:stretch; flex-wrap:wrap;">
        <div style="flex:1; min-width:160px; text-align:center; padding:12px 10px;">
          <div style="font-size:1.6rem; margin-bottom:8px;">📋</div>
          <div style="font-family:'Syne',sans-serif; font-size:0.85rem;
                      font-weight:700; color:#00D4FF;">1. Enter Data</div>
          <div style="font-size:0.78rem; color:#7A9CC0; margin-top:4px;">Input patient lab values & clinical flags</div>
        </div>
        <div style="display:flex; align-items:center; color:#1E3A5F; font-size:1.4rem; padding:0 4px;">→</div>
        <div style="flex:1; min-width:160px; text-align:center; padding:12px 10px;">
          <div style="font-size:1.6rem; margin-bottom:8px;">🤖</div>
          <div style="font-family:'Syne',sans-serif; font-size:0.85rem;
                      font-weight:700; color:#00D4FF;">2. ML Analysis</div>
          <div style="font-size:0.78rem; color:#7A9CC0; margin-top:4px;">4 models vote with GridSearchCV tuning</div>
        </div>
        <div style="display:flex; align-items:center; color:#1E3A5F; font-size:1.4rem; padding:0 4px;">→</div>
        <div style="flex:1; min-width:160px; text-align:center; padding:12px 10px;">
          <div style="font-size:1.6rem; margin-bottom:8px;">📊</div>
          <div style="font-family:'Syne',sans-serif; font-size:0.85rem;
                      font-weight:700; color:#00D4FF;">3. Risk Score</div>
          <div style="font-size:0.78rem; color:#7A9CC0; margin-top:4px;">Probability %, Risk Level, CKD Stage 1–5</div>
        </div>
        <div style="display:flex; align-items:center; color:#1E3A5F; font-size:1.4rem; padding:0 4px;">→</div>
        <div style="flex:1; min-width:160px; text-align:center; padding:12px 10px;">
          <div style="font-size:1.6rem; margin-bottom:8px;">🧠</div>
          <div style="font-family:'Syne',sans-serif; font-size:0.85rem;
                      font-weight:700; color:#00D4FF;">4. Explain</div>
          <div style="font-size:0.78rem; color:#7A9CC0; margin-top:4px;">SHAP feature importance & human explanation</div>
        </div>
        <div style="display:flex; align-items:center; color:#1E3A5F; font-size:1.4rem; padding:0 4px;">→</div>
        <div style="flex:1; min-width:160px; text-align:center; padding:12px 10px;">
          <div style="font-size:1.6rem; margin-bottom:8px;">💊</div>
          <div style="font-family:'Syne',sans-serif; font-size:0.85rem;
                      font-weight:700; color:#00D4FF;">5. Recommend</div>
          <div style="font-size:0.78rem; color:#7A9CC0; margin-top:4px;">Clinical advice + nearest hospital</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Disclaimer ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="disclaimer">
      ⚠️ <strong>Disclaimer:</strong> This system is designed for early screening support only
      and does not replace professional medical diagnosis. All patient data is processed
      locally and used solely for risk assessment. Always consult a qualified nephrologist
      for clinical decisions.
    </div>
    """, unsafe_allow_html=True)
