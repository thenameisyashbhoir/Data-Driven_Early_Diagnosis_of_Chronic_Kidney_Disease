"""
pages/history.py  ──  Patient History + Dataset Export
"""
import streamlit as st
import pandas as pd
import os
from utils.styles   import inject_css, page_header
from utils.database import (get_user_predictions, get_all_predictions,
                             get_current_user, predictions_as_dataset_csv)

CSV_PATH = os.path.join(os.path.dirname(__file__),"..","data","patient_predictions.csv")


def render():
    inject_css()
    page_header("📂","Patient History","Screening records, trend monitoring & data exports")

    user = get_current_user()
    role = st.session_state.get("user_role","guest")

    if role == "guest":
        st.markdown("""<div class="warn-box">
          ⚠️ Guest access does not include history.
          <strong>Register</strong> to save & track your screenings.
        </div>""", unsafe_allow_html=True)
        if st.button("📝 Create Free Account"):
            st.session_state.logged_in = False
            st.rerun()
        return

    preds = get_all_predictions() if role=="admin" else (
            get_user_predictions(user["id"]) if user else [])

    if not preds:
        st.markdown('<div class="info-box">📋 No records yet. Complete a CKD screening first.</div>',
                    unsafe_allow_html=True)
        if st.button("🔬 Start Screening"):
            st.session_state.current_page = "Screening"
            st.rerun()
        return

    total = len(preds)
    high  = sum(1 for p in preds if p["risk_level"]=="High Risk")
    avg_r = round(sum(p["risk_percent"] for p in preds)/total,1) if total else 0

    # ── Summary cards ──────────────────────────────────────────────────────────
    s1,s2,s3 = st.columns(3)
    with s1:
        st.markdown(f"""<div class="metric-card"><div class="metric-val" style="color:#00D4FF;">{total}</div>
          <div class="metric-lbl">Total Records</div></div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""<div class="metric-card"><div class="metric-val" style="color:#FF3B5C;">{high}</div>
          <div class="metric-lbl">High Risk</div></div>""", unsafe_allow_html=True)
    with s3:
        st.markdown(f"""<div class="metric-card"><div class="metric-val" style="color:#FFD166;">{avg_r}%</div>
          <div class="metric-lbl">Average Risk</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Table ──────────────────────────────────────────────────────────────────
    ri = {"High Risk":"🔴","Moderate Risk":"🟡","Low Risk":"🟢"}
    rows = [{
        "ID"        : f"#{p['id']}",
        "Date"      : p["timestamp"][:16],
        "Risk %"    : f"{p['risk_percent']}%",
        "Risk Level": f"{ri.get(p['risk_level'],'')} {p['risk_level']}",
        "Stage"     : p.get("stage","").split("–")[0].strip(),
        "Model"     : p.get("model_used",""),
        **({"Patient":p.get("patient_name",""),"State":p.get("state","")} if role=="admin" else {}),
    } for p in preds]
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Download buttons ───────────────────────────────────────────────────────
    st.markdown('<div class="section-header">⬇️ Export Records</div>', unsafe_allow_html=True)
    dl1, dl2 = st.columns(2)

    # Button 1: Patient records CSV (full detail)
    with dl1:
        csv_rows = []
        for p in preds:
            row = {"ID":p["id"],"Timestamp":p["timestamp"],
                   "Risk %":p["risk_percent"],"Risk Level":p["risk_level"],
                   "Stage":p.get("stage",""),"Model":p.get("model_used",""),
                   "Age":p.get("age_input"),"BloodPressure":p.get("bp"),
                   "SerumCreatinine":p.get("serum_creatinine"),
                   "Hemoglobin":p.get("hemoglobin"),
                   "BloodUrea":p.get("blood_urea"),
                   "BloodGlucose":p.get("blood_glucose"),
                   "Hypertension":p.get("hypertension"),
                   "Diabetes":p.get("diabetes"),
                   "Anemia":p.get("anemia")}
            if role=="admin":
                row["Patient"] = p.get("patient_name","")
                row["Email"]   = p.get("email","")
                row["State"]   = p.get("state","")
            csv_rows.append(row)
        df_csv = pd.DataFrame(csv_rows)
        st.download_button(
            "📥 Download Patient Records (CSV)",
            df_csv.to_csv(index=False).encode(),
            "ckd_patient_records.csv", "text/csv",
            use_container_width=True,
            help="Full patient record with risk scores, explanations and model info"
        )

    # Button 2: Dataset-format export (same columns as original CKD dataset)
    with dl2:
        dataset_bytes = predictions_as_dataset_csv()
        st.download_button(
            "🗃️ Download as CKD Dataset Format",
            dataset_bytes,
            "ckd_patient_dataset.csv", "text/csv",
            use_container_width=True,
            help="Same column format as the original UCI CKD dataset — ready for ML training"
        )

    st.markdown("""
    <div class="info-box" style="margin-top:6px; font-size:0.8rem;">
      💡 <strong>CKD Dataset Format</strong> exports records with identical columns as the original
      UCI dataset (<code>PatientID, Age, BloodPressure, …, CKD</code>). The CKD label is set to
      <code>ckd</code> for High/Moderate risk and <code>notckd</code> for Low risk.
      Use this file to retrain or extend the ML model.
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Record detail ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🔍 Record Detail</div>', unsafe_allow_html=True)
    rec_opts = [f"#{p['id']} — {p['timestamp'][:16]}" for p in preds]
    selected = st.selectbox("Select a record to expand", rec_opts)
    sel_id   = int(selected.split("—")[0].strip().replace("#",""))
    sel_rec  = next((p for p in preds if p["id"]==sel_id), None)

    if sel_rec:
        clr = {"High Risk":"#FF3B5C","Moderate Risk":"#FF8C42",
               "Low Risk":"#00E5A0"}.get(sel_rec["risk_level"],"#7A9CC0")
        st.markdown(f"""
        <div class="ckd-card ckd-card-glow" style="border-left:3px solid {clr};">
          <div style="font-family:'Syne',sans-serif;font-size:1.0rem;font-weight:700;color:{clr};">
            {sel_rec['risk_level']} — {sel_rec['risk_percent']}%
          </div>
          <div style="font-size:0.8rem;color:#7A9CC0;margin-top:3px;">
            {sel_rec.get('stage','')} &nbsp;·&nbsp; {sel_rec['timestamp'][:16]}
            &nbsp;·&nbsp; Model: {sel_rec.get('model_used','')}
            {(' &nbsp;·&nbsp; ' + sel_rec.get('patient_name','')) if role=='admin' else ''}
          </div>
          <hr style="border-color:rgba(0,212,255,0.1);margin:10px 0;">
          <div style="font-size:0.88rem;color:#E8F0FE;line-height:1.7;">
            <strong style="color:#00D4FF;">AI Explanation:</strong><br>
            {sel_rec.get('explanation','')}
          </div>
        </div>""", unsafe_allow_html=True)

        with st.expander("📋 Input Parameters"):
            params = {"Age":sel_rec.get("age_input"),"BP":sel_rec.get("bp"),
                      "Specific Gravity":sel_rec.get("specific_gravity"),
                      "Albumin":sel_rec.get("albumin"),"Sugar":sel_rec.get("sugar"),
                      "Blood Glucose":sel_rec.get("blood_glucose"),
                      "Blood Urea":sel_rec.get("blood_urea"),
                      "Serum Creatinine":sel_rec.get("serum_creatinine"),
                      "Sodium":sel_rec.get("sodium"),"Potassium":sel_rec.get("potassium"),
                      "Hemoglobin":sel_rec.get("hemoglobin"),
                      "Packed Cell Volume":sel_rec.get("packed_cell_volume"),
                      "WBC Count":sel_rec.get("wbc_count"),"RBC Count":sel_rec.get("rbc_count"),
                      "Hypertension":sel_rec.get("hypertension"),
                      "Diabetes":sel_rec.get("diabetes"),"Anemia":sel_rec.get("anemia")}
            st.dataframe(pd.DataFrame([params]).T.rename(columns={0:"Value"}),
                         use_container_width=True)
