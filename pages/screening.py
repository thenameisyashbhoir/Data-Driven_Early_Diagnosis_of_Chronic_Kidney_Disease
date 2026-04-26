"""
pages/screening.py  ──  CKD Screening / Patient Input Form
"""
import streamlit as st
from utils.styles import inject_css, page_header
from utils.database import save_prediction, get_current_user


def render(artefacts):
    inject_css()
    page_header("🧪","CKD Screening","Enter patient medical parameters for AI-powered risk assessment")

    user = get_current_user()
    role = st.session_state.get("user_role","guest")

    if not artefacts:
        st.markdown('<div class="warn-box">⚠️ ML models not found. Run <code>python src/train.py</code>.</div>',
                    unsafe_allow_html=True)
        return

    model_names = list(artefacts["all_models"].keys())
    col_m, col_info = st.columns([2, 3])
    with col_m:
        selected_model = st.selectbox("🤖 ML Model", model_names,
                                      index=model_names.index(artefacts["best_name"]))
    with col_info:
        st.markdown(f"""
        <div class="info-box" style="margin-top:26px;">
          Using <strong>{selected_model}</strong> &nbsp;|&nbsp;
          Best model: <strong>{artefacts['best_name']}</strong> &nbsp;|&nbsp;
          All models ≥ <strong>98.75%</strong> accuracy
        </div>""", unsafe_allow_html=True)

    st.markdown('<hr class="ckd-divider">', unsafe_allow_html=True)

    with st.form("ckd_screening_form"):
        # Demographics & Vitals
        st.markdown('<div class="section-header">👤 Demographics & Vitals</div>', unsafe_allow_html=True)
        c1,c2,c3,c4,c5 = st.columns(5)
        age   = c1.number_input("Age (years)",           1,  110, 48)
        bp    = c2.number_input("Blood Pressure (mmHg)", 40, 250, 80)
        sg    = c3.selectbox("Specific Gravity", [1.005,1.010,1.015,1.020,1.025], index=2)
        alb   = c4.selectbox("Albumin (0–5)",    [0,1,2,3,4,5], index=1)
        sugar = c5.selectbox("Sugar (0–5)",      [0,1,2,3,4,5], index=0)

        # Lab Values
        st.markdown('<div class="section-header">🩸 Blood & Urine Lab Values</div>', unsafe_allow_html=True)
        c1,c2,c3,c4,c5 = st.columns(5)
        bg  = c1.number_input("Blood Glucose (mg/dL)",      50,  600, 120)
        bu  = c2.number_input("Blood Urea (mg/dL)",         5,   400, 36)
        sc  = c3.number_input("Serum Creatinine (mg/dL)",   0.1, 25.0,1.2, step=0.1)
        na  = c4.number_input("Sodium (mEq/L)",             100, 165, 135)
        k   = c5.number_input("Potassium (mEq/L)",          2.0, 12.0,4.5, step=0.1)

        # Blood Count
        st.markdown('<div class="section-header">🔬 Complete Blood Count</div>', unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        hgb = c1.number_input("Hemoglobin (g/dL)",          2.0, 20.0,13.0, step=0.1)
        pcv = c2.number_input("Packed Cell Volume (%)",     10,  65,  41)
        wbc = c3.number_input("WBC Count (/μL)",            1000,50000,7800)
        rbc = c4.number_input("RBC Count (millions/μL)",    1.0, 9.0, 4.5, step=0.1)

        # Microscopy & Flags
        st.markdown('<div class="section-header">🧫 Urine Microscopy & Clinical Flags</div>', unsafe_allow_html=True)
        r1,r2,r3,r4 = st.columns(4)
        rbc_flag = r1.selectbox("Red Blood Cells",  ["normal","abnormal"])
        pus_flag = r2.selectbox("Pus Cells",        ["normal","abnormal"])
        pcc_flag = r3.selectbox("Pus Cell Clumps",  ["notpresent","present"])
        bac_flag = r4.selectbox("Bacteria",         ["notpresent","present"])

        # Co-morbidities
        st.markdown('<div class="section-header">🏥 Co-morbidities & Symptoms</div>', unsafe_allow_html=True)
        r1,r2,r3,r4,r5,r6 = st.columns(6)
        htn = r1.selectbox("Hypertension",          ["no","yes"])
        dm  = r2.selectbox("Diabetes Mellitus",     ["no","yes"])
        cad = r3.selectbox("Coronary Artery Dis.",  ["no","yes"])
        app = r4.selectbox("Appetite",              ["good","poor"])
        ped = r5.selectbox("Pedal Edema",           ["no","yes"])
        anm = r6.selectbox("Anemia",                ["no","yes"])

        st.markdown('<hr class="ckd-divider">', unsafe_allow_html=True)
        col_l, col_btn, col_r = st.columns([2,3,2])
        with col_btn:
            submitted = st.form_submit_button("🔍 Analyse CKD Risk Now", use_container_width=True)

    if submitted:
        patient_data = {
            "Age":age,"BloodPressure":bp,"SpecificGravity":sg,
            "Albumin":alb,"Sugar":sugar,"BloodGlucose":bg,"BloodUrea":bu,
            "SerumCreatinine":sc,"Sodium":na,"Potassium":k,"Hemoglobin":hgb,
            "PackedCellVolume":pcv,"WBCCount":wbc,"RBCCount":rbc,
            "RedBloodCells":rbc_flag,"PusCells":pus_flag,"PusCellClumps":pcc_flag,
            "Bacteria":bac_flag,"Hypertension":htn,"DiabetesMellitus":dm,
            "CoronaryArteryDisease":cad,"Appetite":app,"PedalEdema":ped,"Anemia":anm,
        }
        import sys, os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__),"..","src"))
        from inference import predict as ml_predict

        with st.spinner("🤖 Running ML analysis …"):
            result = ml_predict(patient_data, artefacts, selected_model)

        # Save to DB + CSV (only for logged-in users, not guest)
        if role != "guest" and user:
            save_prediction(user["id"], patient_data, result, selected_model)

        st.session_state.last_result  = result
        st.session_state.last_patient = patient_data
        st.session_state.current_page = "Results"
        st.rerun()

    with st.expander("📖 Normal Reference Ranges"):
        st.markdown("""
        | Parameter | Normal Range | CKD Alert Level |
        |---|---|---|
        | Serum Creatinine | 0.6–1.2 mg/dL | > 1.5 mg/dL |
        | Hemoglobin | 12–17.5 g/dL | < 11 g/dL |
        | Blood Urea | 7–20 mg/dL | > 40 mg/dL |
        | Sodium | 136–145 mEq/L | < 130 or > 150 |
        | Potassium | 3.5–5.0 mEq/L | > 5.5 mEq/L |
        | Blood Pressure | < 120/80 mmHg | > 140/90 mmHg |
        """)
