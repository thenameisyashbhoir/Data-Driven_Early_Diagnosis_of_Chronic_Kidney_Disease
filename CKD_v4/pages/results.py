"""
pages/results.py  ──  Prediction Results with state-based hospital recommendations
"""
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime
from utils.styles   import inject_css, page_header
from utils.charts   import gauge_chart, risk_bar_chart, risk_trend_chart
from utils.database import (get_current_user, get_user_predictions,
                             get_hospitals_for_city_state)
from utils.pdf_report import generate_pdf


def render():
    inject_css()
    result  = st.session_state.get("last_result")
    patient = st.session_state.get("last_patient", {})
    user    = get_current_user()
    role    = st.session_state.get("user_role","guest")

    if not result:
        st.markdown("""<div class="warn-box">
          ⚠️ No results found. Please complete the CKD Screening first.
        </div>""", unsafe_allow_html=True)
        if st.button("← Go to Screening"):
            st.session_state.current_page = "Screening"
            st.rerun()
        return

    prob  = result["risk_percent"]
    risk  = result["risk_level"]
    emoji = result.get("risk_emoji","")
    stage = result["stage"]
    rec   = result["recommendation"]
    feats = result["top_features"]
    expl  = result["explanation_text"]

    clr_map = {"Low Risk":"#00E5A0","Moderate Risk":"#FF8C42","High Risk":"#FF3B5C"}
    colour  = clr_map.get(risk,"#7A9CC0")

    page_header("📊","Prediction Results",
                f"Analysis completed · {datetime.now().strftime('%d %b %Y, %H:%M')}")

    # ── KPI row ────────────────────────────────────────────────────────────────
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-val" style="color:{colour};font-size:2.6rem;">{prob}%</div>
          <div class="metric-lbl">CKD Risk Probability</div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-val" style="color:{colour};font-size:1.4rem;">{emoji} {risk}</div>
          <div class="metric-lbl">Risk Category</div></div>""", unsafe_allow_html=True)
    with m3:
        s_short = stage.split("–")[0].strip() if "–" in stage else stage
        st.markdown(f"""<div class="metric-card">
          <div class="metric-val" style="color:#00D4FF;font-size:1.1rem;">{s_short}</div>
          <div class="metric-lbl">Estimated CKD Stage</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Gauge + Feature chart ──────────────────────────────────────────────────
    col_g, col_f = st.columns([1,2])
    with col_g:
        st.markdown('<div class="section-header">🎯 Risk Gauge</div>', unsafe_allow_html=True)
        fig_g = gauge_chart(prob)
        st.pyplot(fig_g, use_container_width=True); plt.close(fig_g)
        st.markdown("""
        <div style="display:flex;gap:8px;justify-content:center;margin-top:4px;">
          <span style="font-size:0.7rem;color:#7A9CC0;">🟢 Low (0–30%)</span>
          <span style="font-size:0.7rem;color:#7A9CC0;">🟡 Mod (30–60%)</span>
          <span style="font-size:0.7rem;color:#7A9CC0;">🔴 High (60–100%)</span>
        </div>""", unsafe_allow_html=True)

    with col_f:
        st.markdown('<div class="section-header">🧠 Key Contributing Factors</div>',
                    unsafe_allow_html=True)
        if not feats.empty:
            fig_b = risk_bar_chart(feats)
            st.pyplot(fig_b, use_container_width=True); plt.close(fig_b)
        else:
            st.info("Feature explanation not available for this model.")

    # ── Stage detail ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🔬 Stage Diagnosis Detail</div>', unsafe_allow_html=True)
    stage_info = {
        "No CKD" : ("🟢","#00E5A0","Normal kidney function. Monitor annually."),
        "Stage 1": ("🔵","#00D4FF","Kidney damage with normal/high GFR (≥90). Manage causes."),
        "Stage 2": ("🟡","#FFD166","Mildly reduced GFR (60–89). Reduce risk factors."),
        "Stage 3": ("🟠","#FF8C42","Moderately reduced GFR (30–59). See nephrologist."),
        "Stage 4": ("🔴","#FF3B5C","Severely reduced GFR (15–29). Prepare for KRT."),
        "Stage 5": ("🚨","#FF003C","Kidney failure. Dialysis/transplant required."),
    }
    s_key = next((k for k in stage_info if k in stage), "No CKD")
    s_ico, s_clr, s_desc = stage_info[s_key]
    st.markdown(f"""
    <div class="ckd-card" style="border-left:3px solid {s_clr};">
      <div style="display:flex;align-items:center;gap:14px;">
        <div style="font-size:2rem;">{s_ico}</div>
        <div>
          <div style="font-family:'Syne',sans-serif;font-size:1.0rem;
                      font-weight:700;color:{s_clr};">{stage}</div>
          <div style="font-size:0.85rem;color:#7A9CC0;margin-top:4px;">{s_desc}</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    # ── AI Explanation ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🧠 AI Explanation</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="ckd-card ckd-card-glow">
      <div style="font-size:0.75rem;color:#00D4FF;text-transform:uppercase;
                  letter-spacing:0.08em;margin-bottom:8px;">Explainable AI Insight</div>
      <div style="font-size:0.98rem;color:#E8F0FE;line-height:1.8;font-style:italic;">
        "{expl}"
      </div>
    </div>""", unsafe_allow_html=True)

    # ── Risk Trend ─────────────────────────────────────────────────────────────
    if role != "guest" and user:
        preds = get_user_predictions(user["id"])
        if len(preds) >= 2:
            st.markdown('<div class="section-header">📈 Risk Trend</div>', unsafe_allow_html=True)
            trend = [{"date":p["timestamp"][:10],"risk":p["risk_percent"],
                      "level":p["risk_level"]} for p in reversed(preds[:12])]
            fig_t = risk_trend_chart(trend)
            st.pyplot(fig_t, use_container_width=True); plt.close(fig_t)
            delta = trend[-1]["risk"] - trend[-2]["risk"]
            dclr  = "#FF3B5C" if delta > 0 else "#00E5A0"
            dstr  = f"+{delta:.1f}%" if delta > 0 else f"{delta:.1f}%"
            st.markdown(f"""<div class="info-box">
              Change since last visit: <strong style="color:{dclr};">{dstr}</strong> &nbsp;
              {'⚠️ Risk increasing — consult nephrologist.' if delta > 5 else
               '✅ Risk stable or improving.' if delta <= 0 else '📋 Slight increase — keep monitoring.'}
            </div>""", unsafe_allow_html=True)

    # ── Clinical Recommendation ────────────────────────────────────────────────
    st.markdown('<div class="section-header">💊 Clinical Recommendation</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="ckd-card" style="border-color:{colour}33;">
      <div style="white-space:pre-wrap;font-size:0.9rem;color:#E8F0FE;line-height:1.9;">{rec}</div>
    </div>""", unsafe_allow_html=True)

    # ── Hospital Recommendations (state-based, 5+) ─────────────────────────────
    city  = (user.get("city","")  if user else "") or ""
    state = (user.get("state","") if user else "") or ""

    if risk in ("High Risk","Moderate Risk") or city or state:
        hospitals = get_hospitals_for_city_state(city, state, n=5)
        loc_label = f" in {state}" if state else (" near " + city if city else "")
        st.markdown(f'<div class="section-header">🏥 Recommended Nephrology Centres{loc_label}</div>',
                    unsafe_allow_html=True)

        for hosp in hospitals:
            rating     = float(hosp.get("Rating",0))
            stars_full = int(rating)
            stars_html = "⭐" * stars_full
            h_type     = hosp.get("Type","")
            type_clr   = "#00E5A0" if h_type=="Government" else "#00D4FF"
            st.markdown(f"""
            <div class="ckd-card" style="padding:14px 18px;margin-bottom:10px;
                 border-left:3px solid {type_clr};">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;
                          flex-wrap:wrap;gap:8px;">
                <div style="flex:1;">
                  <div style="font-family:'Syne',sans-serif;font-size:0.95rem;
                              font-weight:700;color:#00D4FF;">{hosp.get('Hospital Name','')}</div>
                  <div style="font-size:0.78rem;color:#7A9CC0;line-height:1.9;margin-top:5px;">
                    📍 <strong>{hosp.get('Address','')}</strong><br>
                    🏙️ {hosp.get('City','')} &nbsp;·&nbsp;
                    📍 {hosp.get('State','')}<br>
                    📞 {hosp.get('Phone','')}<br>
                    🩺 {hosp.get('Specialty','')}<br>
                    {stars_html} <span style="color:#FFD166;">{rating}</span>
                  </div>
                </div>
                <div style="text-align:right;">
                  <span style="font-size:0.72rem;background:rgba(0,212,255,0.08);
                               color:{type_clr};border:1px solid {type_clr}33;
                               border-radius:4px;padding:3px 8px;">{h_type}</span>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

    # ── PDF Download ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📄 Download Report</div>', unsafe_allow_html=True)

    display_user = user if user else {
        "patient_name":"Guest","email":"","contact":"","city":city,
        "state":state,"pin":"","gender":"","age":"","blood_group":"","address":""
    }
    hospitals_for_pdf = get_hospitals_for_city_state(
        display_user.get("city",""),
        display_user.get("state",""), n=5
    )

    col_pdf, col_new = st.columns(2)
    with col_pdf:
        try:
            pdf_bytes = generate_pdf(result, patient, display_user, hospitals_for_pdf)
            st.download_button(
                "⬇️ Download Screening Report (PDF)",
                data=pdf_bytes,
                file_name=f"CKD_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF error: {e}")

    with col_new:
        if st.button("🔄 New Screening", use_container_width=True):
            st.session_state.last_result  = None
            st.session_state.last_patient = None
            st.session_state.current_page = "Screening"
            st.rerun()

    if role == "guest":
        st.markdown("""<div class="info-box" style="margin-top:10px;">
          💡 <strong>Register free</strong> to save history, track risk trends over time
          and get personalised state-based hospital recommendations!
        </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="disclaimer">
      🔒 All data is processed locally. This report is for screening only — not a clinical diagnosis.
    </div>""", unsafe_allow_html=True)
