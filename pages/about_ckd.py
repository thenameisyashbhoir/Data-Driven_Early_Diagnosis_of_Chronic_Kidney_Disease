"""
pages/about_ckd.py  ──  Educational CKD Info Page
"""
import streamlit as st
from utils.styles import inject_css, page_header


def render():
    inject_css()
    page_header("📚", "About CKD",
                "Understanding Chronic Kidney Disease — symptoms, risks, and prevention")

    # ── What is CKD ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="ckd-card ckd-card-glow">
      <div style="font-family:'Syne',sans-serif; font-size:1.1rem;
                  font-weight:700; color:#00D4FF; margin-bottom:12px;">
        🫘 What is Chronic Kidney Disease (CKD)?
      </div>
      <div style="font-size:0.92rem; color:#E8F0FE; line-height:1.8;">
        Chronic Kidney Disease (CKD) is a long-term condition in which the kidneys
        gradually lose their ability to filter waste products and excess fluids from
        the blood. The kidneys are vital organs — they regulate blood pressure, produce
        red blood cells, and maintain electrolyte balance. When they fail, toxins
        accumulate in the body, leading to life-threatening complications.
        <br><br>
        CKD affects approximately <strong style="color:#FF3B5C;">850 million people</strong>
        worldwide and is responsible for 1.2 million deaths annually. It is classified
        into 5 stages based on GFR (Glomerular Filtration Rate), with Stage 5 representing
        kidney failure requiring dialysis or transplant.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── CKD Stages ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 CKD Stages & GFR</div>', unsafe_allow_html=True)

    stages = [
        ("Stage 1", "≥ 90",  "Normal or high GFR. Kidney damage present. Usually no symptoms.",      "#00D4FF", "🔵"),
        ("Stage 2", "60–89", "Mildly reduced GFR. Slight decline in kidney function.",                "#00E5A0", "🟢"),
        ("Stage 3", "30–59", "Moderately reduced. Fatigue, swelling, blood pressure changes.",        "#FFD166", "🟡"),
        ("Stage 4", "15–29", "Severely reduced. Nausea, anaemia, prepare for renal therapy.",         "#FF8C42", "🟠"),
        ("Stage 5", "< 15",  "Kidney failure. Dialysis or kidney transplant required urgently.",      "#FF3B5C", "🔴"),
    ]
    for stage, gfr, desc, clr, icon in stages:
        st.markdown(f"""
        <div class="ckd-card" style="padding:12px 18px; margin-bottom:8px;
                                      border-left:3px solid {clr};">
          <div style="display:flex; align-items:flex-start; gap:12px;">
            <div style="font-size:1.4rem;">{icon}</div>
            <div>
              <div style="font-family:'Syne',sans-serif; font-size:0.92rem;
                          font-weight:700; color:{clr};">
                {stage} &nbsp;|&nbsp;
                <span style="font-family:'JetBrains Mono',monospace;
                             font-size:0.82rem; color:#7A9CC0;">GFR {gfr} mL/min/1.73m²</span>
              </div>
              <div style="font-size:0.84rem; color:#7A9CC0; margin-top:3px;">{desc}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Symptoms ──────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🩺 Symptoms & Warning Signs</div>',
                unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    early_symptoms = [
        "Frequent urination, especially at night (nocturia)",
        "Foamy or bubbly urine (protein leakage)",
        "Blood in urine (haematuria)",
        "Mild swelling in ankles or feet",
        "Persistent fatigue and weakness",
        "Mild increase in blood pressure",
    ]
    late_symptoms = [
        "Severe swelling of legs, ankles, feet, face",
        "Shortness of breath (fluid in lungs)",
        "Nausea, vomiting, loss of appetite",
        "Severe itching (uraemia)",
        "Muscle cramps and restless legs",
        "Mental confusion or difficulty concentrating",
    ]

    with col1:
        st.markdown("""
        <div class="ckd-card">
          <div style="font-family:'Syne',sans-serif; font-size:0.9rem;
                      font-weight:700; color:#00E5A0; margin-bottom:10px;">
            🔵 Early Stage Symptoms (1–2)
          </div>""", unsafe_allow_html=True)
        for s in early_symptoms:
            st.markdown(f"""
            <div style="font-size:0.84rem; color:#E8F0FE; padding:4px 0;
                        border-bottom:1px solid rgba(0,212,255,0.07);">
              <span style="color:#00E5A0; margin-right:6px;">•</span>{s}
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="ckd-card">
          <div style="font-family:'Syne',sans-serif; font-size:0.9rem;
                      font-weight:700; color:#FF3B5C; margin-bottom:10px;">
            🔴 Advanced Stage Symptoms (3–5)
          </div>""", unsafe_allow_html=True)
        for s in late_symptoms:
            st.markdown(f"""
            <div style="font-size:0.84rem; color:#E8F0FE; padding:4px 0;
                        border-bottom:1px solid rgba(0,212,255,0.07);">
              <span style="color:#FF3B5C; margin-right:6px;">•</span>{s}
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Risk Factors ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">⚠️ Major Risk Factors</div>',
                unsafe_allow_html=True)
    risk_factors = [
        ("🩸", "Diabetes Mellitus",   "Type 1 and Type 2 diabetes are the #1 cause of CKD worldwide."),
        ("💢", "Hypertension",        "High blood pressure damages glomeruli, reducing filtration."),
        ("👴", "Age > 60",            "Kidney function declines naturally with age."),
        ("🧬", "Family History",      "Genetic predisposition significantly increases risk."),
        ("🫀", "Cardiovascular Disease","Heart disease and CKD share overlapping risk pathways."),
        ("💊", "NSAIDs / Painkillers","Long-term use of ibuprofen, naproxen damages kidney tissue."),
        ("🧂", "High Sodium Diet",    "Excess sodium raises blood pressure, accelerating kidney damage."),
        ("🚬", "Smoking",             "Reduces blood flow to kidneys and slows filtration."),
    ]
    rf_cols = st.columns(4)
    for i, (icon, title, desc) in enumerate(risk_factors):
        with rf_cols[i % 4]:
            st.markdown(f"""
            <div class="ckd-card" style="padding:14px 16px; text-align:center;">
              <div style="font-size:1.5rem; margin-bottom:6px;">{icon}</div>
              <div style="font-family:'Syne',sans-serif; font-size:0.82rem;
                          font-weight:700; color:#00D4FF; margin-bottom:4px;">{title}</div>
              <div style="font-size:0.76rem; color:#7A9CC0; line-height:1.55;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Prevention ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">✅ Prevention Tips</div>', unsafe_allow_html=True)
    prevention = [
        ("💧", "Stay Hydrated",        "Drink 2–3 litres of water daily. Avoid dehydration."),
        ("🥗", "Kidney-Friendly Diet", "Reduce sodium, potassium, phosphorus. Eat fresh vegetables."),
        ("🏃", "Regular Exercise",     "30 minutes of moderate activity daily controls BP and sugar."),
        ("📊", "Monitor Blood Sugar",  "Control HbA1c < 7% to protect kidneys if diabetic."),
        ("💊", "Medication Adherence", "Never skip blood pressure or diabetes medications."),
        ("🔬", "Annual Checkups",      "eGFR and urine tests annually for early detection."),
    ]
    p_cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(prevention):
        with p_cols[i % 3]:
            st.markdown(f"""
            <div class="ckd-card" style="padding:14px 16px;">
              <div style="display:flex; align-items:flex-start; gap:10px;">
                <div style="font-size:1.3rem;">{icon}</div>
                <div>
                  <div style="font-family:'Syne',sans-serif; font-size:0.85rem;
                              font-weight:700; color:#00E5A0;">{title}</div>
                  <div style="font-size:0.8rem; color:#7A9CC0; margin-top:3px; line-height:1.5;">{desc}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

    # ── Privacy ───────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="ckd-card" style="border-color:rgba(0,229,160,0.3);">
      <div style="font-family:'Syne',sans-serif; font-size:0.9rem;
                  font-weight:700; color:#00E5A0; margin-bottom:8px;">
        🔒 Data Privacy Notice
      </div>
      <div style="font-size:0.86rem; color:#7A9CC0; line-height:1.75;">
        All patient data entered into this system is processed <strong>locally on your device</strong>.
        No personal or medical information is transmitted to external servers or stored in the cloud.
        Data is encrypted in the session and used exclusively for CKD risk assessment purposes.
        This system complies with the principles of medical data privacy and patient confidentiality.
      </div>
    </div>
    """, unsafe_allow_html=True)
