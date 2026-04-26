"""
pages/results.py  ──  Prediction Results with state-based hospital recommendations
"""
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime
from utils.styles           import inject_css, page_header
from utils.charts           import gauge_chart, risk_bar_chart, risk_trend_chart
from utils.database         import (get_current_user, get_user_predictions,
                                    get_hospitals_for_city_state)
from utils.pdf_report       import generate_pdf
from utils.health_screening import run_health_screening, findings_summary


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

    # ── Additional Health Findings ─────────────────────────────────────────────
    findings = run_health_screening(patient)
    summary  = findings_summary(findings)

    n_crit = summary["critical"]
    n_warn = summary["warning"]
    banner_clr = "#FF3B5C" if n_crit else "#FF8C42" if n_warn else "#00E5A0"
    banner_txt = (f"🔴 {n_crit} Critical finding{'s' if n_crit!=1 else ''} detected — urgent review advised"
                  if n_crit else
                  f"🟡 {n_warn} finding{'s' if n_warn!=1 else ''} need{'s' if n_warn==1 else ''} attention"
                  if n_warn else
                  "🟢 All additional health markers within normal range")

    st.markdown('<div class="section-header">🏥 Additional Health Findings</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="ckd-card" style="border-color:{banner_clr}44;background:rgba(10,22,40,0.9);
         padding:14px 18px;margin-bottom:16px;">
      <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
        <div style="font-size:1.4rem;">🔬</div>
        <div style="flex:1;">
          <div style="font-family:'Syne',sans-serif;font-size:0.95rem;font-weight:700;
                       color:{banner_clr};">{banner_txt}</div>
          <div style="font-size:0.78rem;color:#7A9CC0;margin-top:3px;">
            Rule-based screening across 6 health domains using your submitted lab values.
            These are <em>indicative findings</em> — not clinical diagnoses.
          </div>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          {"<span style='background:rgba(255,59,92,0.12);color:#FF3B5C;border:1px solid #FF3B5C55;border-radius:6px;padding:4px 10px;font-size:0.78rem;font-weight:700;'>🔴 " + str(n_crit) + " Critical</span>" if n_crit else ""}
          {"<span style='background:rgba(255,140,66,0.12);color:#FF8C42;border:1px solid #FF8C4255;border-radius:6px;padding:4px 10px;font-size:0.78rem;font-weight:700;'>🟡 " + str(n_warn) + " Warning</span>" if n_warn else ""}
          <span style='background:rgba(0,229,160,0.10);color:#00E5A0;border:1px solid #00E5A033;border-radius:6px;padding:4px 10px;font-size:0.78rem;font-weight:700;'>🟢 {summary["normal"]} Normal</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    for finding in findings:
        clr    = finding.color
        is_bad = finding.severity in ("critical", "warning")
        sev_bg = {"critical": "rgba(255,59,92,0.08)",
                  "warning":  "rgba(255,140,66,0.08)",
                  "normal":   "rgba(0,229,160,0.05)"}.get(finding.severity, "rgba(0,0,0,0.3)")

        with st.expander(
            f"{finding.icon}  {finding.condition}  —  {finding.status}",
            expanded=is_bad
        ):
            param_badges = ""
            for p in finding.parameters:
                flag    = p.get("flag", "NORMAL")
                bg_flag = "#FF3B5C" if flag in ("HIGH", "PRESENT", "LOW") else "#00E5A0"
                param_badges += (
                    f"<span style='background:{bg_flag}22;color:{bg_flag};"
                    f"border:1px solid {bg_flag}44;border-radius:6px;"
                    f"padding:3px 10px;font-size:0.75rem;margin-right:6px;margin-bottom:4px;display:inline-block;'>"
                    f"<strong>{p['name']}</strong>: {p['value']} {p['unit']} "
                    f"<span style='font-size:0.65rem;background:{bg_flag}33;padding:1px 5px;"
                    f"border-radius:4px;'>{flag}</span></span>"
                )

            st.markdown(f"""
            <div style="background:{sev_bg};border:1px solid {clr}33;border-radius:10px;padding:14px 16px;">
              <div style="margin-bottom:10px;line-height:2;">{param_badges}</div>
              <div style="border-left:3px solid {clr};padding-left:12px;margin-bottom:12px;">
                <div style="font-size:0.7rem;color:{clr};text-transform:uppercase;
                             letter-spacing:0.08em;margin-bottom:3px;">Triggered By</div>
                <div style="font-size:0.83rem;color:#E8F0FE;">{finding.triggered_by}</div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                <div style="background:rgba(10,22,40,0.6);border-radius:8px;padding:12px;">
                  <div style="font-size:0.7rem;color:#00D4FF;text-transform:uppercase;
                               letter-spacing:0.08em;margin-bottom:5px;">🧬 About this condition</div>
                  <div style="font-size:0.81rem;color:#C8D8EE;line-height:1.7;">{finding.explanation}</div>
                </div>
                <div style="background:rgba(10,22,40,0.6);border-radius:8px;padding:12px;">
                  <div style="font-size:0.7rem;color:#00E5A0;text-transform:uppercase;
                               letter-spacing:0.08em;margin-bottom:5px;">💊 Medical Recommendation</div>
                  <div style="font-size:0.81rem;color:#C8D8EE;line-height:1.9;
                               white-space:pre-wrap;">{finding.recommendation}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer" style="margin-bottom:10px;">
      ⚕️ <strong>Note:</strong> Additional health findings are rule-based screening indicators
      derived from your submitted values. They are not clinical diagnoses. Always consult a
      qualified physician for confirmation and treatment.
    </div>
    """, unsafe_allow_html=True)

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

    # ── Doctor Consultation Card (Moderate + High Risk only) ──────────────────
    if risk in ("Moderate Risk", "High Risk"):
        st.markdown('<div class="section-header">👨‍⚕️ Doctor Consultation</div>',
                    unsafe_allow_html=True)

        wa_msg = (f"Hello Doctor, I have used an AI-based CKD screening system. "
                  f"My result shows {risk} with a {prob}% risk probability. "
                  f"I would like to consult you regarding my kidney health and next steps.")

        urgency_clr  = "#FF3B5C" if risk == "High Risk" else "#FF8C42"
        urgency_icon = "🚨" if risk == "High Risk" else "⚠️"
        urgency_msg  = ("Your CKD risk is HIGH. Please consult a nephrologist as soon as possible."
                        if risk == "High Risk" else
                        "Your CKD risk is MODERATE. A nephrology consultation is strongly advised.")

        st.markdown(f"""
        <div class="ckd-card ckd-card-glow" style="border-color:{urgency_clr}55;
             background:linear-gradient(135deg,rgba(19,34,56,0.98),rgba(10,22,40,0.95));
             margin-bottom:16px;">

          <!-- Header -->
          <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;">
            <div style="font-size:2.5rem;">🏥</div>
            <div style="flex:1;">
              <div style="font-family:'Syne',sans-serif;font-size:1.15rem;font-weight:800;
                           color:#00D4FF;">Connect with a Certified Nephrologist</div>
              <div style="font-size:0.82rem;color:#7A9CC0;margin-top:3px;">
                Get expert medical advice from a qualified kidney specialist
              </div>
            </div>
            <div style="background:{urgency_clr}18;border:1px solid {urgency_clr}44;
                         border-radius:10px;padding:10px 16px;text-align:center;">
              <div style="font-size:1.3rem;">{urgency_icon}</div>
              <div style="font-size:0.72rem;color:{urgency_clr};font-weight:700;margin-top:2px;">
                {risk}</div>
            </div>
          </div>

          <!-- Urgency alert -->
          <div style="background:{urgency_clr}12;border-left:3px solid {urgency_clr};
                       border-radius:0 8px 8px 0;padding:10px 14px;margin-bottom:16px;
                       font-size:0.85rem;color:#E8F0FE;">
            {urgency_icon} {urgency_msg}
          </div>

          <!-- Apollo 24/7 info strip -->
          <div style="background:rgba(0,212,255,0.05);border:1px solid rgba(0,212,255,0.15);
                       border-radius:8px;padding:10px 14px;margin-bottom:14px;
                       display:flex;align-items:center;gap:10px;">
            <div style="font-size:1.4rem;">🩺</div>
            <div style="font-size:0.82rem;color:#C8D8EE;line-height:1.6;">
              <strong style="color:#00D4FF;">Apollo 24/7</strong> connects you with India's top
              certified nephrologists for online video/chat consultations — available 24 hours a day,
              7 days a week. Bring your screening report for a more productive consultation.
            </div>
          </div>

        </div>
        """, unsafe_allow_html=True)

        # Buttons row
        btn_c1, btn_c2, btn_c3 = st.columns(3)

        with btn_c1:
            st.link_button(
                "🏥 Consult on Apollo 24/7",
                url="https://www.apollo247.com/specialties/nephrology",
                use_container_width=True,
            )
            st.markdown(
                '<div style="font-size:0.72rem;color:#7A9CC0;text-align:center;margin-top:3px;">'
                'Nephrology specialists · Online now</div>',
                unsafe_allow_html=True
            )

        with btn_c2:
            st.link_button(
                "🔍 Find Doctors Near You",
                url="https://www.apollo247.com/doctors",
                use_container_width=True,
            )
            st.markdown(
                '<div style="font-size:0.72rem;color:#7A9CC0;text-align:center;margin-top:3px;">'
                'Browse & book by location</div>',
                unsafe_allow_html=True
            )

        with btn_c3:
            st.link_button(
                "📞 Book Appointment",
                url="https://www.apollo247.com/specialties/nephrology",
                use_container_width=True,
            )
            st.markdown(
                '<div style="font-size:0.72rem;color:#7A9CC0;text-align:center;margin-top:3px;">'
                'Schedule a slot</div>',
                unsafe_allow_html=True
            )

        # WhatsApp-style copy message
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.82rem;color:#7A9CC0;margin-bottom:6px;">
          💬 <strong style="color:#E8F0FE;">Doctor Message Template</strong>
          &nbsp;— Copy and paste when you connect with your doctor:
        </div>
        """, unsafe_allow_html=True)

        st.code(wa_msg, language=None)

        st.markdown("""
        <div style="font-size:0.74rem;color:#7A9CC0;margin-top:4px;">
          📋 Click the copy icon on the top-right of the message box above, then paste it
          in the Apollo 24/7 chat or WhatsApp to your doctor.
        </div>
        <br>
        """, unsafe_allow_html=True)

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
