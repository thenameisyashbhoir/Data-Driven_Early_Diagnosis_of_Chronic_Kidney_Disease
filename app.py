import os, sys, pickle, json
import streamlit as st
import streamlit.components.v1 as components

ROOT = os.path.dirname(__file__)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

st.set_page_config(
    page_title="CKD Early Diagnosis System",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.database import (init_session, logout, get_display_name,
                             check_session_timeout, refresh_activity)
from utils.styles   import inject_css, GLOBAL_CSS

init_session()
inject_css()

# ── Theme: inject dark/light CSS on root ──────────────────────────────────────
if not st.session_state.get("dark_mode", True):
    st.markdown("""
    <style>
    :root {
      --navy:      #F0F5FF !important;
      --navy-mid:  #E4EDFF !important;
      --navy-card: #FFFFFF !important;
      --cyan:      #0070CC !important;
      --cyan-dim:  #005299 !important;
      --green:     #00875A !important;
      --orange:    #D4620A !important;
      --red:       #CC1F3A !important;
      --gold:      #B8860B !important;
      --text-main: #0D1B2A !important;
      --text-dim:  #4A6585 !important;
      --border:    rgba(0,112,204,0.2) !important;
      --card-bg:   rgba(255,255,255,0.98) !important;
      --glass:     rgba(240,245,255,0.9) !important;
    }
    .stApp, .main, .block-container,
    [data-testid="stAppViewContainer"],
    [data-testid="stVerticalBlock"] {
      background: #F0F5FF !important;
      color: #0D1B2A !important;
    }
    section[data-testid="stSidebar"] {
      background: #E4EDFF !important;
    }
    section[data-testid="stSidebar"] * { color: #0D1B2A !important; }
    .stTextInput input, .stNumberInput input {
      background: #FFFFFF !important;
      color: #0D1B2A !important;
      border-color: rgba(0,112,204,0.3) !important;
    }
    .stSelectbox [data-baseweb="select"] { background: #FFFFFF !important; }
    p, div, span, label { color: #0D1B2A !important; }
    .page-title { color: #0D1B2A !important; }
    .page-sub { color: #4A6585 !important; }
    .ckd-card { background: rgba(255,255,255,0.98) !important; border-color: rgba(0,112,204,0.2) !important; }
    .metric-card { background: rgba(255,255,255,0.98) !important; }
    .stDataFrame { background: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# ── Hide deploy button (multiple selectors for different Streamlit versions) ───
st.markdown("""
<style>
.stDeployButton, [data-testid="stDeployButton"],
button[kind="header"], [data-testid="manage-app-button"],
[data-testid="stToolbar"], .viewerBadge_container__r5tak,
#MainMenu { display: none !important; visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

# ── Session timeout (2 min = 120 s) ───────────────────────────────────────────
check_session_timeout(600)

# ── Load ML models ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading ML models …")
def get_artefacts():
    path = os.path.join(ROOT, "models", "ckd_artefacts.pkl")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)

artefacts = get_artefacts()

# ── Auth gate ──────────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    from pages.auth import render_login
    render_login()
    st.stop()

refresh_activity()
role = st.session_state.get("user_role", "guest")

# ── Role-based navigation ──────────────────────────────────────────────────────
GUEST_PAGES = [
    ("Screening", "🧪"),
    ("Results",   "📊"),
]
USER_PAGES = [
    ("User Dashboard",  "🏠"),
    ("Screening",       "🧪"),
    ("Results",         "📊"),
    ("Patient History", "📂"),
    ("Health Assistant","🤖"),
    ("Profile",         "👤"),
    ("About CKD",       "📚"),
    ("Model Info",      "⚙️"),
]
ADMIN_PAGES = [
    ("Dashboard",        "📈"),
    ("Admin",            "🔐"),
    ("Screening",        "🧪"),
    ("Results",          "📊"),
    ("Patient History",  "📂"),
    ("Health Assistant", "🤖"),
    ("User Management",  "👥"),
    ("Admin Management", "👑"),
    ("Data Insights",    "🔍"),
    ("About CKD",        "📚"),
    ("Model Info",       "⚙️"),
    ("Profile",          "👤"),
]

NAV     = {"guest":GUEST_PAGES,"user":USER_PAGES,"admin":ADMIN_PAGES}.get(role, GUEST_PAGES)
allowed = [p for p,_ in NAV]
if st.session_state.get("current_page","") not in allowed:
    st.session_state.current_page = allowed[0]

# ── Sidebar CSS — applied once, governs ALL sidebar buttons ───────────────────
st.markdown("""
<style>
/* ── Kill Streamlit auto-pages nav ─────────────────────────────────────── */
[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavLink"],
section[data-testid="stSidebar"] nav,
div[data-testid="stSidebarNavSeparator"]  { display:none!important; }

/* ── EVERY sidebar button = transparent nav item ───────────────────────── */
section[data-testid="stSidebar"] .stButton > button {
    background    : transparent !important;
    color         : #7A9CC0   !important;
    border        : 1px solid transparent !important;
    border-radius : 9px  !important;
    text-align    : left !important;
    justify-content: flex-start !important;
    padding       : 10px 14px !important;
    font-family   : 'DM Sans', sans-serif !important;
    font-size     : 0.87rem !important;
    font-weight   : 500 !important;
    letter-spacing: 0.01em !important;
    transition    : background 0.15s, color 0.15s, border-color 0.15s !important;
    box-shadow    : none !important;
    margin        : 2px 0  !important;
    width         : 100%   !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background  : rgba(0,212,255,0.09) !important;
    color       : #00D4FF !important;
    border-color: rgba(0,212,255,0.25) !important;
}
section[data-testid="stSidebar"] .stButton > button:focus {
    box-shadow: none !important;
    outline: none !important;
}

/* ── ACTIVE nav item (class injected by JS below) ───────────────────────── */
section[data-testid="stSidebar"] .stButton > button.ckd-nav-active {
    background  : rgba(0,212,255,0.12) !important;
    color       : #00D4FF !important;
    border-color: rgba(0,212,255,0.38) !important;
    font-weight : 700 !important;
    box-shadow  : inset 3px 0 0 #00D4FF !important;
}

/* ── Sign-out button gets a distinct red-ish style ──────────────────────── */
section[data-testid="stSidebar"] .stButton > button.ckd-signout {
    color       : #FF3B5C !important;
    border-color: rgba(255,59,92,0.2) !important;
    margin-top  : 4px !important;
}
section[data-testid="stSidebar"] .stButton > button.ckd-signout:hover {
    background  : rgba(255,59,92,0.1) !important;
    border-color: rgba(255,59,92,0.4) !important;
}

/* ── Section label in nav ───────────────────────────────────────────────── */
.nav-section-lbl {
    font-size     : 0.63rem;
    font-weight   : 700;
    color         : #3A5F80;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding       : 14px 4px 4px 6px;
    margin-bottom : 2px;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:

    # ── Brand ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding:14px 4px 16px 4px; border-bottom:1px solid rgba(0,212,255,0.12);
                margin-bottom:14px; text-align:center;">
      <div style="font-size:1.9rem; line-height:1;">🩺</div>
      <div style="font-family:'Syne',sans-serif; font-size:1.05rem; font-weight:800;
                  color:#00D4FF; margin-top:7px; line-height:1.2;">
        CKD Early Diagnosis
      </div>
      <div style="font-size:0.68rem; color:#3A5F80; margin-top:3px;">
        AI-Powered Medical Screening
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── User badge ─────────────────────────────────────────────────────────────
    role_lbl  = {"admin":"👑 Admin","user":"👤 Patient","guest":"👤 Guest"}
    role_clr  = {"admin":"#FFD166","user":"#00D4FF","guest":"#7A9CC0"}
    st.markdown(f"""
    <div style="background:rgba(0,212,255,0.06); border:1px solid rgba(0,212,255,0.18);
                border-radius:10px; padding:10px 13px; margin-bottom:14px;
                display:flex; align-items:center; gap:10px;">
      <div style="width:34px;height:34px;border-radius:50%;
                  background:linear-gradient(135deg,#00D4FF22,#00D4FF55);
                  display:flex;align-items:center;justify-content:center;
                  font-size:1rem; flex-shrink:0;">
        {"👑" if role=="admin" else "👤"}
      </div>
      <div style="overflow:hidden;">
        <div style="font-size:0.84rem;font-weight:600;color:#E8F0FE;
                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
          {get_display_name()}
        </div>
        <div style="font-size:0.7rem;color:{role_clr.get(role,'#7A9CC0')};">
          {role_lbl.get(role,role)}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Guest signup nudge ─────────────────────────────────────────────────────
    if role == "guest":
        st.markdown("""
        <div style="background:rgba(255,140,66,0.07);border:1px solid rgba(255,140,66,0.25);
                    border-radius:8px;padding:9px 12px;margin-bottom:10px;font-size:0.76rem;
                    color:#FFB347;line-height:1.6;">
          ⚡ Guest mode · Screening &amp; Results only.<br>
          <strong>Sign up</strong> for history &amp; full access!
        </div>""", unsafe_allow_html=True)
        if st.button("📝  Create Free Account", use_container_width=True, key="guest_signup"):
            st.session_state.logged_in = False
            st.rerun()

    # ── Inactivity notice ──────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-size:0.65rem;color:#2A4560;text-align:center;margin-bottom:6px;">
      ⏱ Auto-logout after 2 min inactivity
    </div>""", unsafe_allow_html=True)

    # ── Nav section groupings ──────────────────────────────────────────────────
    # Define groups per role (page_name must match NAV exactly)
    if role == "admin":
        NAV_GROUPS = [
            ("OVERVIEW",    ["Dashboard", "Admin"]),
            ("SCREENING",   ["Screening", "Results"]),
            ("PATIENT CARE",["Health Assistant"]),
            ("MANAGEMENT",  ["Patient History", "User Management", "Admin Management"]),
            ("ANALYTICS",   ["Data Insights", "About CKD", "Model Info"]),
            ("ACCOUNT",     ["Profile"]),
        ]
    elif role == "user":
        NAV_GROUPS = [
            ("MAIN",        ["User Dashboard"]),
            ("SCREENING",   ["Screening", "Results", "Patient History"]),
            ("HEALTH TOOLS",["Health Assistant"]),
            ("RESOURCES",   ["About CKD", "Model Info"]),
            ("ACCOUNT",     ["Profile"]),
        ]
    else:
        NAV_GROUPS = [
            ("SCREENING",   ["Screening", "Results"]),
        ]

    current_page = st.session_state.get("current_page", allowed[0])
    nav_dict     = dict(NAV)   # page_name → icon

    for grp_label, grp_pages in NAV_GROUPS:
        # Only show group if at least one page is in allowed
        visible = [p for p in grp_pages if p in allowed]
        if not visible:
            continue

        st.markdown(f'<div class="nav-section-lbl">{grp_label}</div>', unsafe_allow_html=True)

        for page_name in visible:
            icon = nav_dict.get(page_name, "•")
            btn_key = f"nav_{page_name.replace(' ','_')}"
            if st.button(f"{icon}  {page_name}", key=btn_key, use_container_width=True):
                if page_name != "Admin Management":
                    st.session_state["admin_key_verified"] = False
                st.session_state.current_page = page_name
                refresh_activity()
                st.rerun()

    # ── JS: highlight active nav button ───────────────────────────────────────
    # Runs inside an invisible iframe, reaches into parent DOM to add .ckd-nav-active
    active_page_js = json.dumps(current_page)
    components.html(f"""
    <script>
    (function() {{
      var ACTIVE = {active_page_js};
      function applyActive() {{
        var sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
        if (!sidebar) return;
        var allBtns = sidebar.querySelectorAll('.stButton > button');
        allBtns.forEach(function(btn) {{
          var label = btn.innerText.trim();
          // Match buttons whose text ENDS with the active page name
          if (label.endsWith(ACTIVE)) {{
            btn.classList.add('ckd-nav-active');
          }} else {{
            btn.classList.remove('ckd-nav-active');
          }}
        }});
      }}
      applyActive();
      setTimeout(applyActive,  80);
      setTimeout(applyActive, 250);
      setTimeout(applyActive, 600);
    }})();
    </script>
    """, height=0, scrolling=False)

    # ── Dark / Light mode toggle ───────────────────────────────────────────────
    st.markdown('<div style="border-top:1px solid rgba(0,212,255,0.1);margin:10px 0 12px 0;"></div>',
                unsafe_allow_html=True)

    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = True

    mode_icon  = "🌙" if st.session_state.dark_mode else "☀️"
    mode_label = "Dark Mode" if st.session_state.dark_mode else "Light Mode"
    mode_next  = "Switch to Light Mode" if st.session_state.dark_mode else "Switch to Dark Mode"

    if st.button(f"{mode_icon}  {mode_next}", use_container_width=True, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    # ── Divider ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="border-top:1px solid rgba(0,212,255,0.1);margin:14px 0 10px 0;"></div>
    """, unsafe_allow_html=True)

    # ── Models status ──────────────────────────────────────────────────────────
    if artefacts:
        best_auc = artefacts["results_df"]["ROC-AUC"].max()
        st.markdown(f"""
        <div style="background:rgba(0,229,160,0.07);border:1px solid rgba(0,229,160,0.22);
                    border-radius:8px;padding:9px 12px;font-size:0.75rem;
                    color:#7DFFCC;line-height:1.7;margin-bottom:10px;">
          ✅ <strong>Models Loaded</strong><br>
          <span style="color:#7A9CC0;">Best:</span> {artefacts['best_name']}<br>
          <span style="color:#7A9CC0;">ROC-AUC:</span> {best_auc:.4f}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:rgba(255,140,66,0.07);border:1px solid rgba(255,140,66,0.22);
                    border-radius:8px;padding:9px 12px;font-size:0.75rem;
                    color:#FFB347;line-height:1.7;margin-bottom:10px;">
          ⚠️ No models loaded.<br>
          Run: <code>python src/train.py</code>
        </div>""", unsafe_allow_html=True)

    # ── Sign out ───────────────────────────────────────────────────────────────
    if st.button("🚪  Sign Out", use_container_width=True, key="signout_btn"):
        logout()
        st.rerun()

    # JS: mark sign-out button with ckd-signout class
    components.html("""
    <script>
    (function() {
      function styleSignOut() {
        var sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
        if (!sidebar) return;
        var btns = sidebar.querySelectorAll('.stButton > button');
        btns.forEach(function(btn) {
          if (btn.innerText.trim().includes('Sign Out')) {
            btn.classList.add('ckd-signout');
          }
        });
      }
      styleSignOut();
      setTimeout(styleSignOut, 150);
      setTimeout(styleSignOut, 500);
    })();
    </script>
    """, height=0, scrolling=False)

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="margin-top:12px;font-size:0.63rem;color:#243850;
                text-align:center;line-height:1.7;padding:0 4px;">
      CKD Early Diagnosis System v4.0<br>
      SQLite · PBKDF2-SHA256 · XAI
    </div>""", unsafe_allow_html=True)


# ── Page Router ────────────────────────────────────────────────────────────────
page = st.session_state.get("current_page", allowed[0])

if role == "guest" and page not in ["Screening","Results"]:
    page = "Screening"
    st.session_state.current_page = page

if   page == "User Dashboard"  : from pages.user_dashboard   import render; render()
elif page == "Home"             : from pages.home             import render; render()
elif page == "Screening"        : from pages.screening        import render; render(artefacts)
elif page == "Results"          : from pages.results          import render; render()
elif page == "Dashboard"        : from pages.dashboard        import render; render(artefacts)
elif page == "Patient History"  : from pages.history          import render; render()
elif page == "Health Assistant" : from pages.chatbot          import render; render()
elif page == "User Management"  : from pages.user_management  import render; render()
elif page == "Admin Management" : from pages.admin_management import render; render()
elif page == "Data Insights"    : from pages.eda_page         import render; render()
elif page == "About CKD"        : from pages.about_ckd        import render; render()
elif page == "Model Info"       : from pages.model_info       import render; render(artefacts)
elif page == "Admin"            : from pages.admin            import render; render(artefacts)
elif page == "Profile"          : from pages.profile          import render; render()
else:
    if role=="admin"  : from pages.dashboard      import render; render(artefacts)
    elif role=="user" : from pages.user_dashboard import render; render()
    else              : from pages.screening      import render; render(artefacts)
