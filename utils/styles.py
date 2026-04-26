"""
utils/styles.py
---------------
Shared CSS theme for the entire CKD Early Diagnosis web application.
Medical AI aesthetic: deep navy + clinical cyan + alert reds, with
clean geometric structure and premium typography (Syne + DM Sans).
Supports dark mode (default) and light mode.
"""

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── CSS Variables — DARK MODE (default) ───────────────────── */
:root {
  --navy:      #0A1628;
  --navy-mid:  #0F2040;
  --navy-card: #132238;
  --cyan:      #00D4FF;
  --cyan-dim:  #0099BB;
  --green:     #00E5A0;
  --orange:    #FF8C42;
  --red:       #FF3B5C;
  --gold:      #FFD166;
  --text-main: #E8F0FE;
  --text-dim:  #7A9CC0;
  --border:    rgba(0,212,255,0.15);
  --card-bg:   rgba(19,34,56,0.95);
  --glass:     rgba(10,22,40,0.7);
  --mode:      dark;
}

/* ── CSS Variables — LIGHT MODE ────────────────────────────── */
[data-theme="light"] {
  --navy:      #F0F5FF;
  --navy-mid:  #E8F0FE;
  --navy-card: #FFFFFF;
  --cyan:      #0070CC;
  --cyan-dim:  #005299;
  --green:     #00875A;
  --orange:    #D4620A;
  --red:       #CC1F3A;
  --gold:      #B8860B;
  --text-main: #0D1B2A;
  --text-dim:  #4A6585;
  --border:    rgba(0,112,204,0.2);
  --card-bg:   rgba(255,255,255,0.98);
  --glass:     rgba(240,245,255,0.9);
  --mode:      light;
}

/* ── Reset & Base ───────────────────────────────────────────── */
html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
  color: var(--text-main);
}
.main { background: var(--navy) !important; }
.block-container { 
  padding: 1.5rem 2rem 3rem 2rem !important; 
  max-width: 1280px;
}
section[data-testid="stSidebar"] {
  background: var(--navy-mid) !important;
  border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * { color: var(--text-main) !important; }

/* ── Light mode: force main content background ──────────────── */
[data-theme="light"] .main { background: #F0F5FF !important; }
[data-theme="light"] .stApp { background: #F0F5FF !important; }
[data-theme="light"] .block-container { background: #F0F5FF !important; }
[data-theme="light"] section[data-testid="stSidebar"] { background: #E8F0FE !important; }
[data-theme="light"] section[data-testid="stSidebar"] * { color: #0D1B2A !important; }

/* ── Light mode: input fields ───────────────────────────────── */
[data-theme="light"] .stTextInput input,
[data-theme="light"] .stNumberInput input { 
  background: #FFFFFF !important; 
  color: #0D1B2A !important;
  border-color: rgba(0,112,204,0.3) !important;
}

/* ── Light mode: dataframe ──────────────────────────────────── */
[data-theme="light"] .stDataFrame { background: #FFFFFF !important; }
[data-theme="light"] .stDataFrame th { background: rgba(0,112,204,0.1) !important; }

/* ── Hide streamlit chrome ──────────────────────────────────── */
#MainMenu { display: none !important; }   /* hide 3 dots only */
footer { display: none !important; }      /* hide footer only */
.stDeployButton { display: none; }

/* ── HIDE Streamlit's auto-generated pages/ folder navigation ── */
/* This removes the duplicate nav that appears because pages/ folder exists */
[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavLink"],
section[data-testid="stSidebar"] nav,
section[data-testid="stSidebar"] > div > div > div > ul,
.st-emotion-cache-1aw8i8e,
div[data-testid="stSidebarNavSeparator"] {
  display: none !important;
  visibility: hidden !important;
  height: 0 !important;
  overflow: hidden !important;
}

/* ── Typography ─────────────────────────────────────────────── */
h1, h2, h3, h4 { font-family: 'Syne', sans-serif !important; }

/* ── Sidebar nav buttons ────────────────────────────────────── */
.nav-btn {
  display: flex; align-items: center; gap: 10px;
  padding: 11px 16px; margin: 3px 0;
  border-radius: 8px; cursor: pointer;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.88rem; font-weight: 500;
  color: var(--text-dim);
  border: 1px solid transparent;
  transition: all 0.2s ease;
  text-decoration: none; width: 100%;
  background: transparent;
}
.nav-btn:hover {
  background: rgba(0,212,255,0.08);
  color: var(--cyan);
  border-color: var(--border);
}
.nav-btn.active {
  background: rgba(0,212,255,0.12);
  color: var(--cyan) !important;
  border-color: rgba(0,212,255,0.3);
  font-weight: 600;
}
.nav-icon { font-size: 1.05rem; width: 20px; }

/* ── Cards ──────────────────────────────────────────────────── */
.ckd-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 22px 24px;
  margin-bottom: 16px;
  backdrop-filter: blur(12px);
}
.ckd-card-glow {
  box-shadow: 0 0 24px rgba(0,212,255,0.08);
}

/* ── Metric Cards ───────────────────────────────────────────── */
.metric-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px 20px;
  text-align: center;
  position: relative; overflow: hidden;
}
.metric-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--cyan), var(--green));
}
.metric-val {
  font-family: 'Syne', sans-serif;
  font-size: 2.0rem; font-weight: 800;
  line-height: 1.1; margin-bottom: 4px;
}
.metric-lbl {
  font-size: 0.78rem; font-weight: 500;
  color: var(--text-dim); letter-spacing: 0.05em;
  text-transform: uppercase;
}

/* ── Risk Cards ─────────────────────────────────────────────── */
.risk-low    { border-color: var(--green)  !important; }
.risk-mod    { border-color: var(--orange) !important; }
.risk-high   { border-color: var(--red)    !important; }
.risk-low  .metric-card::before  { background: var(--green); }
.risk-mod  .metric-card::before  { background: var(--orange); }
.risk-high .metric-card::before  { background: var(--red); }

/* ── Page Title ─────────────────────────────────────────────── */
.page-title {
  font-family: 'Syne', sans-serif;
  font-size: 1.75rem; font-weight: 800;
  color: var(--text-main);
  margin-bottom: 4px;
}
.page-sub {
  font-size: 0.9rem; color: var(--text-dim);
  margin-bottom: 20px;
}
.cyan-line {
  height: 2px; width: 48px;
  background: linear-gradient(90deg, var(--cyan), transparent);
  margin-bottom: 24px; border-radius: 2px;
}

/* ── Section Header ─────────────────────────────────────────── */
.section-header {
  font-family: 'Syne', sans-serif;
  font-size: 1.1rem; font-weight: 700;
  color: var(--cyan); letter-spacing: 0.03em;
  margin: 20px 0 12px 0;
  display: flex; align-items: center; gap: 8px;
}

/* ── Badges ─────────────────────────────────────────────────── */
.badge {
  display: inline-block; padding: 3px 10px;
  border-radius: 20px; font-size: 0.72rem;
  font-weight: 600; letter-spacing: 0.05em;
  text-transform: uppercase;
}
.badge-cyan   { background: rgba(0,212,255,0.15); color: var(--cyan); }
.badge-green  { background: rgba(0,229,160,0.15); color: var(--green); }
.badge-orange { background: rgba(255,140,66,0.15); color: var(--orange); }
.badge-red    { background: rgba(255,59,92,0.15);  color: var(--red); }
.badge-gold   { background: rgba(255,209,102,0.15);color: var(--gold); }

/* ── Table ──────────────────────────────────────────────────── */
.stDataFrame { 
  background: var(--navy-card) !important; 
  border-radius: 10px !important;
}
.stDataFrame th {
  background: rgba(0,212,255,0.1) !important;
  color: var(--cyan) !important;
  font-family: 'Syne', sans-serif !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.05em !important;
}

/* ── Inputs ─────────────────────────────────────────────────── */
.stTextInput input, .stNumberInput input, .stSelectbox select {
  background: var(--navy-card) !important;
  color: var(--text-main) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
}
.stSelectbox [data-baseweb="select"] {
  background: var(--navy-card) !important;
}

/* ── Buttons ────────────────────────────────────────────────── */
.stButton > button {
  background: linear-gradient(135deg, var(--cyan), var(--cyan-dim)) !important;
  color: var(--navy) !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 700 !important;
  border: none !important;
  border-radius: 8px !important;
  padding: 10px 28px !important;
  letter-spacing: 0.03em !important;
  transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* ── Expander ───────────────────────────────────────────────── */
.streamlit-expanderHeader {
  background: var(--navy-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--text-main) !important;
  font-family: 'DM Sans', sans-serif !important;
}
.streamlit-expanderContent {
  background: var(--card-bg) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 8px 8px !important;
}

/* ── Alert / Info boxes ─────────────────────────────────────── */
.info-box {
  background: rgba(0,212,255,0.06);
  border: 1px solid rgba(0,212,255,0.2);
  border-left: 3px solid var(--cyan);
  border-radius: 8px; padding: 12px 16px;
  font-size: 0.88rem; color: var(--text-main);
  line-height: 1.7; margin: 10px 0;
}
.warn-box {
  background: rgba(255,140,66,0.06);
  border: 1px solid rgba(255,140,66,0.2);
  border-left: 3px solid var(--orange);
  border-radius: 8px; padding: 12px 16px;
  font-size: 0.88rem; line-height: 1.7; margin: 10px 0;
}
.danger-box {
  background: rgba(255,59,92,0.06);
  border: 1px solid rgba(255,59,92,0.2);
  border-left: 3px solid var(--red);
  border-radius: 8px; padding: 12px 16px;
  font-size: 0.88rem; line-height: 1.7; margin: 10px 0;
}
.success-box {
  background: rgba(0,229,160,0.06);
  border: 1px solid rgba(0,229,160,0.2);
  border-left: 3px solid var(--green);
  border-radius: 8px; padding: 12px 16px;
  font-size: 0.88rem; line-height: 1.7; margin: 10px 0;
}

/* ── Dividers ───────────────────────────────────────────────── */
.ckd-divider {
  border: none;
  border-top: 1px solid var(--border);
  margin: 20px 0;
}

/* ── Progress bar override ──────────────────────────────────── */
.stProgress > div > div > div > div {
  background: linear-gradient(90deg, var(--cyan), var(--green)) !important;
}

/* ── Sidebar logo area ──────────────────────────────────────── */
.sidebar-logo {
  padding: 12px 0 20px 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 16px;
}
.sidebar-logo-title {
  font-family: 'Syne', sans-serif;
  font-size: 1.1rem; font-weight: 800;
  color: var(--cyan);
  line-height: 1.2;
}
.sidebar-logo-sub {
  font-size: 0.72rem; color: var(--text-dim);
  margin-top: 2px;
}

/* ── Tabs override ──────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--navy-card) !important;
  border-radius: 10px !important;
  padding: 4px !important;
  border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
  color: var(--text-dim) !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.85rem !important;
  border-radius: 7px !important;
}
.stTabs [aria-selected="true"] {
  background: rgba(0,212,255,0.15) !important;
  color: var(--cyan) !important;
  font-weight: 600 !important;
}

/* ── Disclaimer bar ─────────────────────────────────────────── */
.disclaimer {
  background: rgba(255,209,102,0.06);
  border: 1px solid rgba(255,209,102,0.2);
  border-radius: 8px; padding: 10px 16px;
  font-size: 0.78rem; color: var(--text-dim);
  line-height: 1.6; margin-top: 16px;
}

/* ── Mono text ──────────────────────────────────────────────── */
.mono { font-family: 'JetBrains Mono', monospace; }

/* ── Gauge arc colors ───────────────────────────────────────── */
.gauge-low    { fill: var(--green); }
.gauge-mod    { fill: var(--orange); }
.gauge-high   { fill: var(--red); }

/* ── Scrollbar ──────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--navy); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>
"""


def inject_css():
    import streamlit as st
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str = ""):
    import streamlit as st
    st.markdown(f"""
    <div>
      <div class="page-title">{icon} {title}</div>
      <div class="page-sub">{subtitle}</div>
      <div class="cyan-line"></div>
    </div>
    """, unsafe_allow_html=True)


def card(content_html: str, extra_class: str = ""):
    return f'<div class="ckd-card {extra_class}">{content_html}</div>'


def metric_card(value: str, label: str, color: str = "var(--cyan)", risk_class: str = ""):
    return f"""
    <div class="{risk_class}">
      <div class="metric-card">
        <div class="metric-val" style="color:{color}">{value}</div>
        <div class="metric-lbl">{label}</div>
      </div>
    </div>"""


def badge(text: str, kind: str = "cyan") -> str:
    return f'<span class="badge badge-{kind}">{text}</span>'
