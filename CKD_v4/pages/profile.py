"""
pages/profile.py  ──  User Profile: View, Edit, Change Password
"""
import streamlit as st
from utils.styles   import inject_css, page_header
from utils.database import (get_current_user, update_user_profile,
                             change_password, get_user_predictions,
                             get_user_by_id, validate_password)

BLOOD_GROUPS = ["A+","A-","B+","B-","AB+","AB-","O+","O-"]
GENDERS      = ["Male","Female","Other","Prefer not to say"]
STATES = [
    "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Delhi",
    "Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala",
    "Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland",
    "Odisha","Puducherry","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana",
    "Tripura","Uttar Pradesh","Uttarakhand","West Bengal"
]


def render():
    inject_css()
    user = get_current_user()
    if not user:
        st.session_state.current_page = "Home"; st.rerun(); return

    page_header("👤","My Profile","View and update your personal details")

    tab_view, tab_edit, tab_pw = st.tabs(
        ["👁️ Profile Overview","✏️ Edit Profile","🔒 Change Password"])

    # ══ VIEW ══════════════════════════════════════════════════════════════════
    with tab_view:
        preds = get_user_predictions(user["id"])
        c_info, c_stats = st.columns([3,2])
        with c_info:
            role_ico = "👑" if user.get("role")=="admin" else "👤"
            st.markdown(f"""
            <div class="ckd-card ckd-card-glow">
              <div style="text-align:center;margin-bottom:16px;">
                <div style="width:68px;height:68px;border-radius:50%;
                            background:linear-gradient(135deg,#00D4FF,#0099BB);
                            display:flex;align-items:center;justify-content:center;
                            margin:0 auto 8px auto;font-size:1.9rem;">{role_ico}</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.25rem;
                            font-weight:800;color:#E8F0FE;">{user.get('patient_name','')}</div>
                <div style="font-size:0.78rem;color:#7A9CC0;">
                  @{user.get('username','')} ·
                  <span style="color:#00D4FF;">{'Admin' if user.get('role')=='admin' else 'Patient'}</span>
                </div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
            """, unsafe_allow_html=True)
            fields = [
                ("📧 Email",       user.get("email","")),
                ("📞 Contact",     user.get("contact","")),
                ("🎂 Age",         f"{user.get('age','')} years"),
                ("👤 Gender",      user.get("gender","")),
                ("🩸 Blood Group", user.get("blood_group","")),
                ("🏙️ City",        user.get("city","")),
                ("📍 State",       user.get("state","")),
                ("📮 PIN Code",    user.get("pin","")),
                ("📅 Joined",      str(user.get("created_at",""))[:10]),
            ]
            for label, value in fields:
                st.markdown(f"""
                <div style="background:rgba(0,212,255,0.05);border:1px solid rgba(0,212,255,0.1);
                            border-radius:8px;padding:7px 10px;">
                  <div style="font-size:0.7rem;color:#7A9CC0;margin-bottom:1px;">{label}</div>
                  <div style="font-size:0.86rem;color:#E8F0FE;font-weight:500;">{value or '—'}</div>
                </div>""", unsafe_allow_html=True)
            if user.get("address"):
                st.markdown(f"""
                <div style="background:rgba(0,212,255,0.05);border:1px solid rgba(0,212,255,0.1);
                            border-radius:8px;padding:7px 10px;grid-column:span 2;">
                  <div style="font-size:0.7rem;color:#7A9CC0;margin-bottom:1px;">📍 Address</div>
                  <div style="font-size:0.86rem;color:#E8F0FE;font-weight:500;">{user.get('address','')}</div>
                </div>""", unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)

        with c_stats:
            total = len(preds)
            high  = sum(1 for p in preds if p["risk_level"]=="High Risk")
            avg_r = round(sum(p["risk_percent"] for p in preds)/total,1) if total else 0
            st.markdown(f"""
            <div class="ckd-card" style="text-align:center;">
              <div style="font-family:'Syne',sans-serif;font-size:0.88rem;
                          font-weight:700;color:#00D4FF;margin-bottom:14px;">
                Screening Stats
              </div>
              <div class="metric-card" style="margin-bottom:10px;">
                <div class="metric-val" style="color:#00D4FF;">{total}</div>
                <div class="metric-lbl">Total Screenings</div>
              </div>
              <div class="metric-card" style="margin-bottom:10px;">
                <div class="metric-val" style="color:#FF3B5C;">{high}</div>
                <div class="metric-lbl">High Risk Results</div>
              </div>
              <div class="metric-card">
                <div class="metric-val" style="color:#FFD166;">{avg_r}%</div>
                <div class="metric-lbl">Average Risk Score</div>
              </div>
            </div>""", unsafe_allow_html=True)

    # ══ EDIT ══════════════════════════════════════════════════════════════════
    with tab_edit:
        with st.form("edit_profile"):
            st.markdown('<div class="section-header">✏️ Update Details</div>', unsafe_allow_html=True)
            e1, e2 = st.columns(2)
            patient_name = e1.text_input("Full Name",   value=user.get("patient_name",""))
            contact      = e2.text_input("Contact No.", value=user.get("contact",""))

            e3, e4, e5 = st.columns(3)
            gender      = e3.selectbox("Gender",     GENDERS,
                          index=GENDERS.index(user.get("gender",GENDERS[0]))
                                if user.get("gender") in GENDERS else 0)
            age         = e4.number_input("Age", 1, 120,
                          value=int(user.get("age",25)))
            blood_group = e5.selectbox("Blood Group", BLOOD_GROUPS,
                          index=BLOOD_GROUPS.index(user.get("blood_group",BLOOD_GROUPS[0]))
                                if user.get("blood_group") in BLOOD_GROUPS else 0)

            e6, e7, e8, e9 = st.columns(4)
            state   = e6.selectbox("State", STATES,
                      index=STATES.index(user.get("state",STATES[0]))
                            if user.get("state") in STATES else 0)
            city    = e7.text_input("City",    value=user.get("city",""))
            pin     = e8.text_input("PIN",     value=user.get("pin",""))
            address = e9.text_input("Address", value=user.get("address",""))

            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                ok, msg = update_user_profile(user["id"], {
                    "patient_name":patient_name,"contact":contact,"address":address,
                    "blood_group":blood_group,"gender":gender,"age":age,
                    "city":city,"state":state,"pin":pin,
                })
                if ok:
                    st.session_state.user_info = get_user_by_id(user["id"])
                    st.markdown('<div class="success-box">✅ Profile updated!</div>',
                                unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="danger-box">❌ {msg}</div>', unsafe_allow_html=True)

    # ══ CHANGE PASSWORD ═══════════════════════════════════════════════════════
    with tab_pw:
        st.markdown("<br>", unsafe_allow_html=True)
        import re
        col_l, col_pw, col_r = st.columns([1,2,1])
        with col_pw:
            with st.form("change_pw"):
                st.markdown('<div class="section-header">🔒 Change Password</div>',
                            unsafe_allow_html=True)
                old_pw  = st.text_input("Current Password", type="password")
                new_pw  = st.text_input("New Password",     type="password",
                                        help="Min 6 · 1 uppercase · 1 lowercase · 1 number · 1 special")
                conf_pw = st.text_input("Confirm New Password", type="password")
                submitted_pw = st.form_submit_button("🔑 Update Password", use_container_width=True)

            # Strength indicator
            if new_pw:
                checks = {
                    "6+ chars":"✅" if len(new_pw)>=6 else "❌",
                    "A-Z":"✅" if re.search(r'[A-Z]',new_pw) else "❌",
                    "a-z":"✅" if re.search(r'[a-z]',new_pw) else "❌",
                    "0-9":"✅" if re.search(r'\d',new_pw) else "❌",
                    "!@#":"✅" if re.search(r'[!@#$%^&*]',new_pw) else "❌",
                }
                items = " &nbsp; ".join(f'{v} <span style="font-size:0.75rem;">{k}</span>'
                                         for k,v in checks.items())
                st.markdown(f'<div style="padding:4px 0;">{items}</div>', unsafe_allow_html=True)

            if submitted_pw:
                if not old_pw or not new_pw:
                    st.markdown('<div class="warn-box">⚠️ Fill all fields.</div>',
                                unsafe_allow_html=True)
                elif new_pw != conf_pw:
                    st.markdown('<div class="warn-box">⚠️ Passwords do not match.</div>',
                                unsafe_allow_html=True)
                else:
                    ok, msg = change_password(user["id"], old_pw, new_pw)
                    if ok:
                        st.markdown(f'<div class="success-box">✅ {msg}</div>',
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="danger-box">❌ {msg}</div>',
                                    unsafe_allow_html=True)

        st.markdown("""<div class="info-box" style="margin-top:14px;">
          🔐 Passwords hashed with <strong>PBKDF2-SHA256</strong> · 260,000 iterations · Random salt.
          Your plain-text password is never stored.
        </div>""", unsafe_allow_html=True)
