"""
pages/admin_management.py  ──  Admin Account Management
• List all admin accounts
• Create new admin (requires secret admin key — key clears on every page visit)
"""
import re
import streamlit as st
import pandas as pd
from utils.styles   import inject_css, page_header
from utils.database import (get_all_users, register_user, validate_password,
                             ADMIN_SECRET_KEY)

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
    if st.session_state.get("user_role") != "admin":
        st.markdown('<div class="danger-box">🚫 Admin access only.</div>', unsafe_allow_html=True)
        return

    page_header("👑","Admin Account Management",
                "Create new admin accounts (key required) · View existing admins")

    # ── Reset key on every single render unless JUST verified this render ──────
    # We use a render counter: each render increments it.
    # Verification sets _admin_key_render = current render count.
    # On next render, counter increments → verified flag is cleared automatically.
    # This means: ANY button click, tab switch, or widget change resets the key.
    render_count = st.session_state.get("_admin_render_count", 0) + 1
    st.session_state["_admin_render_count"] = render_count

    last_verified_render = st.session_state.get("_admin_key_render", -1)
    # If key was NOT verified in the immediately preceding render, clear it
    if last_verified_render != render_count - 1:
        st.session_state["admin_key_verified"] = False

    tab_list, tab_create = st.tabs(["📋 All Admin Accounts", "➕ Create New Admin"])

    # ══ LIST ADMINS ════════════════════════════════════════════════════════════
    with tab_list:
        admins = get_all_users(role_filter="admin")
        st.markdown(f'<div class="section-header">👑 Registered Admins ({len(admins)})</div>',
                    unsafe_allow_html=True)
        if admins:
            df = pd.DataFrame([{
                "ID"      : a["id"],
                "Name"    : a["patient_name"],
                "Username": a["username"],
                "Email"   : a["email"],
                "City"    : a.get("city",""),
                "State"   : a.get("state",""),
                "Joined"  : str(a.get("created_at",""))[:10],
            } for a in admins])
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "⬇️ Export Admin List (CSV)",
                df.to_csv(index=False).encode(),
                "admin_list.csv", "text/csv",
                use_container_width=True
            )
        else:
            st.markdown('<div class="info-box">No admins found.</div>', unsafe_allow_html=True)

    # ══ CREATE ADMIN ═══════════════════════════════════════════════════════════
    with tab_create:
        st.markdown("""
        <div class="warn-box">
          🔐 <strong>Admin Key Required</strong> — You must enter the secret admin key every
          time you visit this page. Navigating away resets verification automatically.
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        verified = st.session_state.get("admin_key_verified", False)

        # ── STEP 1: Key verification ───────────────────────────────────────────
        if not verified:
            st.markdown('<div class="section-header">🔑 Step 1: Enter Admin Secret Key</div>',
                        unsafe_allow_html=True)
            col_l, col_k, col_r = st.columns([1, 2, 1])
            with col_k:
                key_input = st.text_input("Admin Secret Key", type="password",
                                          placeholder="Enter the admin creation key",
                                          key="admin_key_input")
                if st.button("✅ Verify Key", use_container_width=True, key="verify_key_btn"):
                    if key_input.strip() == ADMIN_SECRET_KEY:
                        st.session_state["admin_key_verified"] = True
                        st.session_state["_admin_key_render"] = render_count  # mark this render
                        st.rerun()
                    else:
                        st.markdown("""<div class="danger-box">
                          ❌ <strong>Wrong admin key.</strong>
                          You are not authorised to create admin accounts.
                          Contact your system administrator.
                        </div>""", unsafe_allow_html=True)
            return  # Don't render the form until key is verified

        # ── STEP 2: Registration form (only after key verified) ────────────────
        st.markdown("""
        <div class="success-box">
          ✅ Admin key verified. Fill in the details below to create a new admin account.
        </div>""", unsafe_allow_html=True)

        col_hdr, col_reset = st.columns([4, 1])
        with col_reset:
            if st.button("🔄 Re-verify Key", use_container_width=True):
                st.session_state["admin_key_verified"] = False
                st.session_state["_admin_key_render"] = -1
                st.rerun()

        st.markdown('<div class="section-header">📝 Step 2: New Admin Details</div>',
                    unsafe_allow_html=True)

        with st.form("create_admin_form", clear_on_submit=True):
            r1, r2, r3 = st.columns(3)
            patient_name = r1.text_input("Full Name *",  placeholder="e.g. Dr. Admin")
            username     = r2.text_input("Username *",   placeholder="e.g. admin2")
            email        = r3.text_input("Email *",      placeholder="admin2@ckd.ai")

            r4, r5, r6, r7 = st.columns(4)
            gender      = r4.selectbox("Gender",      GENDERS)
            age         = r5.number_input("Age",       min_value=18, max_value=80, value=30)
            blood_group = r6.selectbox("Blood Group",  BLOOD_GROUPS)
            contact     = r7.text_input("Contact",     placeholder="10-digit number")

            r8, r9, r10 = st.columns(3)
            state   = r8.selectbox("State",  STATES)
            city    = r9.text_input("City",   placeholder="e.g. New Delhi")
            pin     = r10.text_input("PIN",   placeholder="e.g. 110001")
            address = st.text_input("Office Address")

            st.markdown('<div class="section-header">🔒 Set Admin Password</div>',
                        unsafe_allow_html=True)
            p1, p2 = st.columns(2)
            password   = p1.text_input("Password *",         type="password",
                                        help="Min 6 · 1 uppercase · 1 lowercase · 1 number · 1 special")
            confirm_pw = p2.text_input("Confirm Password *", type="password")

            # Live strength indicator
            if password:
                checks = {
                    "6+ chars"  : len(password) >= 6,
                    "A-Z"       : bool(re.search(r'[A-Z]', password)),
                    "a-z"       : bool(re.search(r'[a-z]', password)),
                    "0-9"       : bool(re.search(r'\d', password)),
                    "!@#..."    : bool(re.search(r'[!@#$%^&*()\-_=+\[\]{};:\'",.<>/?\\|`~]', password)),
                }
                items = " &nbsp; ".join(
                    f'<span style="color:{"#00E5A0" if v else "#FF3B5C"};font-size:0.76rem;">'
                    f'{"✅" if v else "❌"} {k}</span>'
                    for k, v in checks.items()
                )
                st.markdown(f'<div style="padding:4px 0;">{items}</div>', unsafe_allow_html=True)

            submitted = st.form_submit_button("👑 Create Admin Account", use_container_width=True)

        if submitted:
            errors = []
            if not patient_name: errors.append("Full Name required.")
            if not username:     errors.append("Username required.")
            if not email or "@" not in email: errors.append("Valid email required.")
            if not contact or len(contact.strip()) < 10: errors.append("10-digit contact required.")
            if not city:         errors.append("City required.")
            if not pin:          errors.append("PIN required.")
            if not password:     errors.append("Password required.")
            if password != confirm_pw: errors.append("Passwords do not match.")

            if errors:
                for e in errors:
                    st.markdown(f'<div class="warn-box" style="margin-bottom:4px;">⚠️ {e}</div>',
                                unsafe_allow_html=True)
            else:
                ok, msg = register_user({
                    "patient_name": patient_name.strip(),
                    "username"    : username.strip().lower(),
                    "email"       : email.strip().lower(),
                    "contact"     : contact.strip(),
                    "address"     : address.strip(),
                    "blood_group" : blood_group,
                    "gender"      : gender,
                    "age"         : int(age),
                    "city"        : city.strip(),
                    "state"       : state,
                    "pin"         : pin.strip(),
                    "password"    : password,
                    "role"        : "admin",
                })
                if ok:
                    st.markdown(f"""<div class="success-box">
                      ✅ {msg}<br>
                      Admin key has been reset — you'll need to re-enter it to create another account.
                    </div>""", unsafe_allow_html=True)
                    # Reset verification after successful creation
                    st.session_state["admin_key_verified"] = False
                    st.session_state["_admin_key_render"] = -1
                else:
                    st.markdown(f'<div class="danger-box">❌ {msg}</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="disclaimer" style="margin-top:14px;">
          🔐 Admin key is server-side only · Passwords: PBKDF2-SHA256 · 260,000 iterations
        </div>""", unsafe_allow_html=True)
