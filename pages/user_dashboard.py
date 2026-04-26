"""
pages/user_dashboard.py  ──  User Dashboard (post-login home)
"""
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from utils.styles import inject_css, page_header
from utils.database import get_user_predictions, get_current_user
from utils.charts import risk_trend_chart


def render():
    inject_css()
    user = get_current_user()
    if not user:
        st.session_state.current_page = "Home"
        st.rerun()
        return

    name        = user.get("patient_name","User")
    city        = user.get("city","")
    blood_group = user.get("blood_group","")
    age         = user.get("age","")
    gender      = user.get("gender","")

    preds = get_user_predictions(user["id"])
    total = len(preds)
    high  = sum(1 for p in preds if p["risk_level"] == "High Risk")
    avg_r = round(sum(p["risk_percent"] for p in preds) / total, 1) if total else 0
    last  = preds[0] if preds else None

    # ── Welcome banner ─────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="ckd-card ckd-card-glow" style="padding:24px 28px; margin-bottom:20px;
         background:linear-gradient(135deg,rgba(0,212,255,0.07),rgba(10,22,40,0.95));">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px;">
        <div>
          <div style="font-size:0.78rem; color:#7A9CC0; text-transform:uppercase;
                      letter-spacing:0.1em; margin-bottom:4px;">Welcome back</div>
          <div style="font-family:'Syne',sans-serif; font-size:1.8rem;
                      font-weight:800; color:#E8F0FE;">{name}</div>
          <div style="font-size:0.85rem; color:#7A9CC0; margin-top:4px;">
            {gender} · Age {age} · Blood Group <span style="color:#00D4FF;">{blood_group}</span>
            {' · ' + city if city else ''}
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:0.78rem; color:#7A9CC0;">Last Screening</div>
          <div style="font-size:0.88rem; color:#E8F0FE; margin-top:2px;">
            {last['timestamp'] if last else 'No screenings yet'}
          </div>
          {'<div style="font-size:0.82rem; color:' + ("#FF3B5C" if last and last["risk_level"]=="High Risk" else "#00E5A0") + '; margin-top:2px; font-weight:600;">' + (last["risk_level"] + " — " + str(last["risk_percent"]) + "%") + '</div>' if last else ''}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stat cards ──────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-val" style="color:#00D4FF;">{total}</div>
          <div class="metric-lbl">Total Screenings</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-val" style="color:#FF3B5C;">{high}</div>
          <div class="metric-lbl">High Risk Results</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-val" style="color:#FFD166;">{avg_r}%</div>
          <div class="metric-lbl">Average Risk Score</div></div>""", unsafe_allow_html=True)
    with k4:
        last_risk = last["risk_level"].split()[0] if last else "N/A"
        lclr = {"High":"#FF3B5C","Moderate":"#FF8C42","Low":"#00E5A0"}.get(last_risk,"#7A9CC0")
        st.markdown(f"""<div class="metric-card">
          <div class="metric-val" style="color:{lclr}; font-size:1.3rem;">{last_risk}</div>
          <div class="metric-lbl">Latest Risk Level</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Quick actions ───────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)
    a1, a2, a3, a4 = st.columns(4)
    actions = [
        ("🔬 Start Screening",   "Screening"),
        ("📊 View Last Result",  "Results"),
        ("📂 My History",        "Patient History"),
        ("👤 My Profile",        "Profile"),
    ]
    for col, (label, page) in zip([a1,a2,a3,a4], actions):
        with col:
            if st.button(label, use_container_width=True, key=f"qa_{page}"):
                st.session_state.current_page = page
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Risk trend ──────────────────────────────────────────────────────────────
    if len(preds) >= 2:
        st.markdown('<div class="section-header">📈 Risk Trend Over Time</div>',
                    unsafe_allow_html=True)
        trend_data = [{"date": p["timestamp"][:10], "risk": p["risk_percent"],
                       "level": p["risk_level"]} for p in reversed(preds[:10])]
        fig = risk_trend_chart(trend_data)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    elif total == 0:
        st.markdown("""
        <div class="info-box">
          📋 You haven't done any screenings yet. Click <strong>Start Screening</strong> above
          to get your CKD risk assessed by our AI system.
        </div>""", unsafe_allow_html=True)

    # ── Recent screenings ────────────────────────────────────────────────────────
    if preds:
        st.markdown('<div class="section-header">🕐 Recent Screenings</div>',
                    unsafe_allow_html=True)
        risk_icon = {"High Risk":"🔴","Moderate Risk":"🟡","Low Risk":"🟢"}
        for p in preds[:5]:
            icon  = risk_icon.get(p["risk_level"],"⚪")
            clr   = {"High Risk":"#FF3B5C","Moderate Risk":"#FF8C42",
                     "Low Risk":"#00E5A0"}.get(p["risk_level"],"#7A9CC0")
            stage_short = p["stage"].split("–")[0].strip() if p["stage"] else ""
            st.markdown(f"""
            <div class="ckd-card" style="padding:12px 18px; margin-bottom:8px;
                 border-left:3px solid {clr};">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <span style="font-size:1.1rem;">{icon}</span>
                  <span style="font-family:'Syne',sans-serif; font-size:0.92rem;
                               font-weight:700; color:{clr}; margin-left:8px;">
                    {p['risk_level']} — {p['risk_percent']}%</span>
                  <span style="font-size:0.8rem; color:#7A9CC0; margin-left:10px;">
                    {stage_short}</span>
                </div>
                <div style="font-size:0.78rem; color:#7A9CC0;">{p['timestamp'][:16]}</div>
              </div>
              <div style="font-size:0.8rem; color:#7A9CC0; margin-top:4px; font-style:italic;">
                {p.get('explanation','')[:100]}...</div>
            </div>""", unsafe_allow_html=True)

    # ── Health tips ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">💡 Daily Health Tips</div>', unsafe_allow_html=True)
    tips = [
        ("💧", "Stay Hydrated", "Drink 2–3 litres of water daily"),
        ("🥗", "Balanced Diet", "Low sodium, low phosphorus diet"),
        ("🏃", "Stay Active",   "30 min moderate exercise daily"),
        ("📊", "Monitor BP",    "Keep blood pressure below 130/80"),
        ("🩺", "Regular Check", "Annual kidney function tests"),
        ("💊", "Medications",   "Never skip prescribed medicines"),
    ]
    tip_cols = st.columns(6)
    for col, (icon, title, desc) in zip(tip_cols, tips):
        with col:
            st.markdown(f"""
            <div class="ckd-card" style="padding:12px 10px; text-align:center;">
              <div style="font-size:1.4rem; margin-bottom:5px;">{icon}</div>
              <div style="font-family:'Syne',sans-serif; font-size:0.75rem;
                          font-weight:700; color:#00D4FF; margin-bottom:3px;">{title}</div>
              <div style="font-size:0.7rem; color:#7A9CC0; line-height:1.5;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer" style="margin-top:20px;">
      🔒 All your screening data is stored securely with end-to-end encryption.
      This dashboard is for personal health monitoring only.
    </div>""", unsafe_allow_html=True)
