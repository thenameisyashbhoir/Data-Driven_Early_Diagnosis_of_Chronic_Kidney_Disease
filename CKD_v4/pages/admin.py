"""
pages/admin.py  ──  Admin Dashboard — Role-Based Access
"""
import streamlit as st
import pandas as pd
import os, sys
from utils.styles import inject_css, page_header
from utils.database import (get_all_users, get_all_predictions,
                             get_analytics_db, get_current_user)

CSV_PATH = os.path.join(os.path.dirname(__file__),"..","data","patient_predictions.csv")
ROOT     = os.path.join(os.path.dirname(__file__),"..")


def render(artefacts):
    inject_css()

    if st.session_state.get("user_role") != "admin":
        st.markdown('<div class="danger-box">🚫 Access Denied. Admins only.</div>',
                    unsafe_allow_html=True)
        return

    page_header("🔐","Admin Dashboard",
                "Manage patients, view predictions, model stats & data exports")

    analytics = get_analytics_db()

    # ── KPI Row ────────────────────────────────────────────────────────────────
    k1,k2,k3,k4,k5 = st.columns(5)
    kpis = [
        (str(analytics["total_users"]),  "Registered Users", "#00D4FF"),
        (str(analytics["total"]),        "Total Predictions","#FFD166"),
        (str(analytics["high"]),         "High Risk Cases",  "#FF3B5C"),
        (f"{analytics['avg_risk']}%",    "Avg Risk Score",   "#FF8C42"),
        (f"{analytics['high_pct']}%",    "High Risk %",      "#FF3B5C"),
    ]
    for col,(val,lbl,clr) in zip([k1,k2,k3,k4,k5],kpis):
        with col:
            st.markdown(f"""<div class="metric-card">
              <div class="metric-val" style="color:{clr};">{val}</div>
              <div class="metric-lbl">{lbl}</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    tab_patients, tab_predictions, tab_predict_csv, tab_model, tab_users = st.tabs([
        "👥 Patient Records",
        "📊 All Predictions",
        "🔬 Predict on CSV",
        "🤖 Model Stats",
        "👤 User Management",
    ])

    # ══ PATIENT RECORDS ════════════════════════════════════════════════════════
    with tab_patients:
        st.markdown('<div class="section-header">🔍 Filter Records</div>', unsafe_allow_html=True)
        fc1, fc2 = st.columns(2)
        filter_risk = fc1.selectbox("Filter by Risk Level",
                                    ["All","High Risk","Moderate Risk","Low Risk"])
        filter_user = fc2.text_input("Search by name/email/city")

        preds = get_all_predictions()
        if filter_risk != "All":
            preds = [p for p in preds if p["risk_level"] == filter_risk]
        if filter_user:
            q = filter_user.lower()
            preds = [p for p in preds if
                     q in (p.get("patient_name","")).lower() or
                     q in (p.get("email","")).lower() or
                     q in (p.get("city","")).lower()]

        st.markdown(f'<div class="section-header">📋 Records ({len(preds)} found)</div>',
                    unsafe_allow_html=True)
        risk_icon = {"High Risk":"🔴","Moderate Risk":"🟡","Low Risk":"🟢"}
        if preds:
            rows = [{
                "ID"        : f"#{p['id']}",
                "Patient"   : p.get("patient_name",""),
                "Email"     : p.get("email",""),
                "City"      : p.get("city",""),
                "Timestamp" : p["timestamp"][:16],
                "Risk %"    : f"{p['risk_percent']}%",
                "Risk Level": f"{risk_icon.get(p['risk_level'],'')} {p['risk_level']}",
                "Stage"     : p["stage"].split("–")[0].strip() if p.get("stage") else "",
                "Model"     : p.get("model_used",""),
            } for p in preds]
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

            high_cnt = sum(1 for p in preds if p["risk_level"]=="High Risk")
            if high_cnt:
                st.markdown(f"""
                <div class="danger-box">🚨 <strong>{high_cnt}</strong> high-risk patient(s) require
                immediate nephrology referral.</div>""", unsafe_allow_html=True)

        # Download predictions CSV
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH,"rb") as f:
                st.download_button("⬇️ Download Patient Predictions CSV",
                                   f.read(), "patient_predictions.csv",
                                   "text/csv", use_container_width=True)

    # ══ ALL PREDICTIONS ════════════════════════════════════════════════════════
    with tab_predictions:
        preds_all = get_all_predictions()
        if preds_all:
            df_all = pd.DataFrame([{
                "ID": p["id"], "Patient": p.get("patient_name",""),
                "City": p.get("city",""), "Timestamp": p["timestamp"][:16],
                "Risk %": f"{p['risk_percent']}%",
                "Risk": p["risk_level"],
                "Stage": p.get("stage","").split("–")[0].strip(),
                "Creatinine": p.get("serum_creatinine"),
                "Hemoglobin": p.get("hemoglobin"),
                "BP": p.get("bp"),
                "Age": p.get("age_input"),
            } for p in preds_all])
            st.dataframe(df_all, use_container_width=True, hide_index=True)
        else:
            st.markdown('<div class="info-box">ℹ️ No predictions yet.</div>', unsafe_allow_html=True)

    # ══ PREDICT ON CSV ═════════════════════════════════════════════════════════
    with tab_predict_csv:
        st.markdown("""
        <div class="section-header">🔬 Predict CKD Risk on Patient Records CSV</div>
        <div class="info-box" style="margin-bottom:14px;">
          Upload a CSV file with patient parameters to run batch predictions.
          The system will predict CKD risk for each row using the best ML model.
        </div>""", unsafe_allow_html=True)

        uploaded = st.file_uploader("Upload Patient CSV", type=["csv"])

        if uploaded and artefacts:
            import pandas as pd_import
            try:
                df_up = pd_import.read_csv(uploaded)
                st.markdown(f"**Uploaded:** {len(df_up)} patients, {len(df_up.columns)} columns")
                st.dataframe(df_up.head(), use_container_width=True)

                if st.button("🔍 Run Batch Prediction", use_container_width=True):
                    sys.path.insert(0, os.path.join(ROOT,"src"))
                    from inference import predict as ml_predict
                    from utils.database import save_prediction

                    results_list = []
                    prog = st.progress(0)
                    for i, row in df_up.iterrows():
                        pd_dict = row.to_dict()
                        try:
                            res = ml_predict(pd_dict, artefacts)
                            results_list.append({
                                **pd_dict,
                                "Predicted_Risk_%"    : res["risk_percent"],
                                "Predicted_Risk_Level": res["risk_level"],
                                "Predicted_Stage"     : res["stage"],
                                "AI_Explanation"      : res["explanation_text"],
                            })
                        except Exception as e:
                            results_list.append({**pd_dict, "Error": str(e)})
                        prog.progress((i+1)/len(df_up))

                    df_result = pd_import.DataFrame(results_list)
                    st.success(f"✅ Batch prediction complete for {len(df_result)} patients!")
                    st.dataframe(df_result, use_container_width=True)
                    st.download_button("⬇️ Download Predictions",
                                       df_result.to_csv(index=False).encode(),
                                       "batch_predictions.csv","text/csv",
                                       use_container_width=True)
            except Exception as e:
                st.error(f"Error reading CSV: {e}")

        elif uploaded and not artefacts:
            st.warning("Models not loaded. Run training first.")

        # Also allow running on internal patient_predictions CSV
        st.markdown('<hr class="ckd-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🗄️ Run Prediction on Internal Patient Records</div>',
                    unsafe_allow_html=True)
        if os.path.exists(CSV_PATH) and artefacts:
            import pandas as pd_int
            df_internal = pd_int.read_csv(CSV_PATH)
            st.markdown(f"**Internal records:** {len(df_internal)} patient entries")
            st.dataframe(df_internal.head(), use_container_width=True)
            if st.button("🔍 Re-run Predictions on Internal CSV"):
                sys.path.insert(0, os.path.join(ROOT,"src"))
                from inference import predict as ml_predict
                re_results = []
                feature_map = {
                    "Age":"Age","BloodPressure":"BloodPressure",
                    "SpecificGravity":"SpecificGravity","Albumin":"Albumin",
                    "Sugar":"Sugar","BloodGlucose":"BloodGlucose","BloodUrea":"BloodUrea",
                    "SerumCreatinine":"SerumCreatinine","Sodium":"Sodium","Potassium":"Potassium",
                    "Hemoglobin":"Hemoglobin","PackedCellVolume":"PackedCellVolume",
                    "WBCCount":"WBCCount","RBCCount":"RBCCount",
                    "RedBloodCells":"RedBloodCells","PusCells":"PusCells",
                    "PusCellClumps":"PusCellClumps","Bacteria":"Bacteria",
                    "Hypertension":"Hypertension","DiabetesMellitus":"DiabetesMellitus",
                    "CoronaryArteryDisease":"CoronaryArteryDisease","Appetite":"Appetite",
                    "PedalEdema":"PedalEdema","Anemia":"Anemia",
                }
                for _, row in df_internal.iterrows():
                    pd_dict = {v: row.get(k) for k,v in feature_map.items()}
                    try:
                        res = ml_predict(pd_dict, artefacts)
                        re_results.append({
                            "PatientName": row.get("PatientName",""),
                            "City": row.get("City",""),
                            "Timestamp": row.get("Timestamp",""),
                            "New_Risk_%": res["risk_percent"],
                            "New_Risk_Level": res["risk_level"],
                            "New_Stage": res["stage"],
                        })
                    except Exception as e:
                        re_results.append({"Error": str(e)})
                df_re = pd_int.DataFrame(re_results)
                st.dataframe(df_re, use_container_width=True)
                st.download_button("⬇️ Download Re-predicted CSV",
                                   df_re.to_csv(index=False).encode(),
                                   "repredicted.csv","text/csv")
        else:
            st.markdown('<div class="info-box">ℹ️ No internal patient records CSV found yet.</div>',
                        unsafe_allow_html=True)

    # ══ MODEL STATS ════════════════════════════════════════════════════════════
    with tab_model:
        if artefacts:
            st.markdown('<div class="section-header">📊 Model Performance</div>', unsafe_allow_html=True)
            st.dataframe(artefacts["results_df"], use_container_width=True)
            st.markdown(f"""
            <div class="success-box">
              🏆 <strong>Best Model:</strong> {artefacts['best_name']}<br>
              📈 <strong>ROC-AUC:</strong> {artefacts['results_df']['ROC-AUC'].max():.4f}<br>
              🎯 <strong>Best Recall:</strong> {artefacts['results_df']['Recall'].max():.4f}
            </div>""", unsafe_allow_html=True)
        else:
            st.warning("Models not loaded. Run `python src/train.py`")

    # ══ USER MANAGEMENT ════════════════════════════════════════════════════════
    with tab_users:
        st.markdown('<div class="section-header">👥 All Registered Users</div>',
                    unsafe_allow_html=True)
        users = get_all_users()
        if users:
            df_users = pd.DataFrame(users)
            st.dataframe(df_users, use_container_width=True, hide_index=True)
            st.download_button("⬇️ Export Users CSV",
                               df_users.to_csv(index=False).encode(),
                               "users_export.csv","text/csv",
                               use_container_width=True)
        else:
            st.info("No users registered yet.")
