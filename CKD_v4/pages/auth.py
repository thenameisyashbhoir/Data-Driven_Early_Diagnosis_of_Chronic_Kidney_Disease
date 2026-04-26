"""
pages/auth.py  ──  Login + Registration (no extra top space, compact layout)
"""
import re
import streamlit as st
from utils.styles   import inject_css
from utils.database import login_user, register_user, validate_password

BLOOD_GROUPS = ["A+","A-","B+","B-","AB+","AB-","O+","O-"]
GENDERS      = ["Male","Female","Other","Prefer not to say"]
STATES = [
    "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Delhi",
    "Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala",
    "Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland",
    "Odisha","Puducherry","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana",
    "Tripura","Uttar Pradesh","Uttarakhand","West Bengal"
]

PW_HINT = "Min 6 chars · 1 uppercase · 1 lowercase · 1 number · 1 special character"


def _pw_strength_html(pw: str) -> str:
    checks = {
        "6+ chars"  : len(pw) >= 6,
        "A-Z"       : bool(re.search(r'[A-Z]', pw)),
        "a-z"       : bool(re.search(r'[a-z]', pw)),
        "0-9"       : bool(re.search(r'\d', pw)),
        "!@#..."    : bool(re.search(r'[!@#$%^&*()\-_=+\[\]{};:\'",.<>/?\\|`~]', pw)),
    }
    items = " &nbsp; ".join(
        f'<span style="color:{"#00E5A0" if v else "#FF3B5C"};font-size:0.76rem;">'
        f'{"✅" if v else "❌"} {k}</span>'
        for k, v in checks.items()
    )
    return f'<div style="padding:5px 0 2px 0;">{items}</div>'


def render_login():
    inject_css()

    # Remove default streamlit top padding
    st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Chrome autofill / password-save support ────────────────────────────────
    # Streamlit renders inputs as shadow DOM; we inject a hidden real <form>
    # with proper autocomplete attributes so Chrome's credential manager sees it.
    import streamlit.components.v1 as components
    components.html("""
    <form id="ckd-login-shadow" method="POST" action="" style="display:none;"
          onsubmit="return false;">
      <input id="ckd-username" type="text"     name="username" autocomplete="username"     />
      <input id="ckd-password" type="password" name="password" autocomplete="current-password" />
      <button type="submit">Sign In</button>
    </form>
    <script>
    // Mirror values from Streamlit inputs → shadow form so Chrome sees a real login form
    (function() {
      function sync() {
        var doc = window.parent.document;
        // Find the identifier input (first text input in the login card)
        var inputs = doc.querySelectorAll('input[type="text"], input[type="email"]');
        var pwInputs = doc.querySelectorAll('input[type="password"]');
        if (inputs.length > 0) {
          document.getElementById('ckd-username').value = inputs[0].value || '';
        }
        if (pwInputs.length > 0) {
          document.getElementById('ckd-password').value = pwInputs[0].value || '';
        }
      }
      // When Streamlit Sign In button is clicked, trigger shadow form submit
      // so Chrome prompts to save credentials
      function watchSignIn() {
        var doc = window.parent.document;
        var btns = doc.querySelectorAll('button');
        btns.forEach(function(btn) {
          if (btn.innerText && btn.innerText.includes('Sign In')) {
            btn.addEventListener('click', function() {
              sync();
              // Submit shadow form to trigger Chrome's "Save Password?" prompt
              var form = document.getElementById('ckd-login-shadow');
              if (form) {
                form.style.display = 'block';
                form.submit();
                setTimeout(function() { form.style.display = 'none'; }, 100);
              }
            }, { once: false });
          }
        });
      }
      setTimeout(watchSignIn, 800);
      setTimeout(watchSignIn, 1500);
      setTimeout(watchSignIn, 3000);
    })();
    </script>
    """, height=0, scrolling=False)

    # ── Brand header (compact) ─────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding:14px 0 10px 0;">
      <div style="font-size:2.4rem; line-height:1;">🩺</div>
      <div style="font-family:'Syne',sans-serif; font-size:1.75rem; font-weight:800;
                  color:#00D4FF; margin-top:6px; line-height:1.1;">
        CKD Early Diagnosis
      </div>
      <div style="font-size:0.82rem; color:#7A9CC0; margin-top:4px;">
        AI-Powered Chronic Kidney Disease Screening System
      </div>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔐 Sign In", "📝 Create Account"])

    # ══════════════════════════════════════════════════════════════════════════
    # SIGN IN TAB
    # ══════════════════════════════════════════════════════════════════════════
    with tab_login:
        col_l, col_form, col_r = st.columns([1, 2, 1])
        with col_form:
            st.markdown('<div class="ckd-card ckd-card-glow" style="margin-top:12px;">',
                        unsafe_allow_html=True)
            st.markdown("""
            <div style="font-family:'Syne',sans-serif;font-size:1.0rem;font-weight:700;
                        color:#E8F0FE;text-align:center;margin-bottom:14px;">
              Welcome Back
            </div>""", unsafe_allow_html=True)

            identifier = st.text_input("📧 Email or Username",
                                       placeholder="Enter email or username", key="li_id")
            password   = st.text_input("🔒 Password", type="password",
                                       placeholder="Enter password", key="li_pw")

            if st.button("Sign In →", key="btn_signin", use_container_width=True):
                if not identifier or not password:
                    st.markdown('<div class="warn-box">⚠️ Please fill in all fields.</div>',
                                unsafe_allow_html=True)
                else:
                    ok, msg, user = login_user(identifier.strip(), password.strip())
                    if ok:
                        st.session_state.logged_in    = True
                        st.session_state.user_id      = user["id"]
                        st.session_state.user_role    = user["role"]
                        st.session_state.user_info    = user
                        st.session_state.current_page = (
                            "Dashboard" if user["role"] == "admin" else "User Dashboard"
                        )
                        from utils.database import refresh_activity
                        refresh_activity()
                        st.rerun()
                    else:
                        st.markdown(f'<div class="danger-box">❌ {msg}</div>',
                                    unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # Guest
            st.markdown("""
            <div style="text-align:center;font-size:0.8rem;color:#7A9CC0;
                        margin:8px 0 4px 0;">— or continue without account —</div>
            """, unsafe_allow_html=True)
            if st.button("👤 Continue as Guest (Screening Only)",
                         use_container_width=True, key="btn_guest"):
                st.session_state.logged_in    = True
                st.session_state.user_id      = None
                st.session_state.user_role    = "guest"
                st.session_state.user_info    = {"patient_name":"Guest","city":"","state":""}
                st.session_state.current_page = "Screening"
                from utils.database import refresh_activity
                refresh_activity()
                st.rerun()

            st.markdown("""
            <div class="info-box" style="margin-top:10px;font-size:0.76rem;">
              <b>Demo Admin:</b> &nbsp;
              <code>admin@ckd.ai</code> / <code>Admin@123</code>
            </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # REGISTER TAB
    # ══════════════════════════════════════════════════════════════════════════
    with tab_register:
        with st.form("register_form", clear_on_submit=True):
            st.markdown('<div class="section-header">👤 Personal Details</div>',
                        unsafe_allow_html=True)
            r1a, r1b, r1c = st.columns(3)
            patient_name = r1a.text_input("Full Name *",     placeholder="e.g. Yash Sharma")
            username     = r1b.text_input("Username *",      placeholder="e.g. yash123")
            email        = r1c.text_input("Email *",         placeholder="you@example.com")

            r2a, r2b, r2c, r2d = st.columns(4)
            gender      = r2a.selectbox("Gender *",      GENDERS)
            age         = r2b.number_input("Age *",      min_value=1, max_value=120, value=25)
            blood_group = r2c.selectbox("Blood Group *", BLOOD_GROUPS)
            contact     = r2d.text_input("Contact No. *",placeholder="10-digit mobile")

            st.markdown('<div class="section-header">📍 Address</div>', unsafe_allow_html=True)
            r3a, r3b, r3c, r3d = st.columns(4)
            state   = r3a.selectbox("State *", STATES)
            city    = r3b.text_input("City *",    placeholder="e.g. Mumbai")
            pin     = r3c.text_input("PIN Code *",placeholder="e.g. 400001")
            address = r3d.text_input("Address",   placeholder="Street, Area")

            st.markdown('<div class="section-header">🔒 Password</div>', unsafe_allow_html=True)
            p1, p2 = st.columns(2)
            password   = p1.text_input("New Password *",     type="password",
                                        help=PW_HINT, placeholder=PW_HINT)
            confirm_pw = p2.text_input("Confirm Password *", type="password",
                                        placeholder="Re-enter password")

            submitted = st.form_submit_button("📝 Create Account", use_container_width=True)

        # Show password strength outside form (after typing)
        if password:
            st.markdown(_pw_strength_html(password), unsafe_allow_html=True)

        if submitted:
            errors = []
            if not patient_name: errors.append("Full Name is required.")
            if not username:     errors.append("Username is required.")
            if not email or "@" not in email: errors.append("Valid email required.")
            if not contact or len(contact.strip()) < 10: errors.append("10-digit contact required.")
            if not city:         errors.append("City is required.")
            if not pin or len(pin.strip()) < 5: errors.append("Valid PIN required.")
            if not password:     errors.append("Password is required.")
            if password and password != confirm_pw: errors.append("Passwords do not match.")

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
                })
                if ok:
                    st.markdown(f"""
                    <div class="success-box">
                      ✅ <strong>Registration successful!</strong><br>
                      Welcome, {patient_name}! Please sign in using the Sign In tab.
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="danger-box">❌ {msg}</div>',
                                unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-top:14px;font-size:0.72rem;color:#3A5F80;">
      🔐 Passwords hashed with PBKDF2-SHA256 · 260,000 iterations · Random salt
    </div>""", unsafe_allow_html=True)
