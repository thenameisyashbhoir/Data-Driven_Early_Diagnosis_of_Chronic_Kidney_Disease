"""
pages/user_management.py  ──  Admin: Patient/User Management
Separate page to view, filter, delete patient accounts.
"""
import streamlit as st
import pandas as pd
from utils.styles   import inject_css, page_header
from utils.database import get_all_users, delete_user, get_analytics_db


def render():
    inject_css()
    if st.session_state.get("user_role") != "admin":
        st.markdown('<div class="danger-box">🚫 Admin access only.</div>', unsafe_allow_html=True)
        return

    page_header("👥", "User Management", "View, filter and manage all registered patient accounts")

    analytics = get_analytics_db()
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-val" style="color:#00D4FF;">{analytics['total_users']}</div>
          <div class="metric-lbl">Registered Patients</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-val" style="color:#FF3B5C;">{analytics['total']}</div>
          <div class="metric-lbl">Total Screenings</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="metric-card">
          <div class="metric-val" style="color:#FFD166;">{analytics['avg_risk']}%</div>
          <div class="metric-lbl">Average Risk Score</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filters ────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🔍 Search Patients</div>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)
    search_name  = fc1.text_input("Search by name",  placeholder="e.g. Yash")
    search_city  = fc2.text_input("Search by city",  placeholder="e.g. Mumbai")
    search_state = fc3.text_input("Search by state", placeholder="e.g. Maharashtra")

    users = get_all_users(role_filter="user")

    if search_name:
        users = [u for u in users if search_name.lower() in u.get("patient_name","").lower()]
    if search_city:
        users = [u for u in users if search_city.lower() in u.get("city","").lower()]
    if search_state:
        users = [u for u in users if search_state.lower() in (u.get("state","") or "").lower()]

    st.markdown(f'<div class="section-header">📋 Patient List ({len(users)} found)</div>',
                unsafe_allow_html=True)

    if users:
        df = pd.DataFrame([{
            "ID"         : u["id"],
            "Name"       : u["patient_name"],
            "Username"   : u["username"],
            "Email"      : u["email"],
            "Contact"    : u.get("contact",""),
            "Blood Group": u.get("blood_group",""),
            "Gender"     : u.get("gender",""),
            "Age"        : u.get("age",""),
            "City"       : u.get("city",""),
            "State"      : u.get("state",""),
            "Joined"     : str(u.get("created_at",""))[:10],
        } for u in users])
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Export
        col_csv, col_del = st.columns([3,1])
        with col_csv:
            st.download_button(
                "⬇️ Export Patient List (CSV)",
                df.to_csv(index=False).encode(),
                "patients_list.csv", "text/csv",
                use_container_width=True
            )

        # Delete user
        st.markdown('<hr class="ckd-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">🗑️ Remove Patient Account</div>',
                    unsafe_allow_html=True)
        st.markdown("""<div class="warn-box">
          ⚠️ Deleting a patient removes their account but retains their screening records
          in the prediction database for audit purposes.
        </div>""", unsafe_allow_html=True)

        user_options = {f"#{u['id']} — {u['patient_name']} ({u['email']})": u["id"]
                        for u in users}
        selected_label = st.selectbox("Select patient to delete", ["— Select —"] + list(user_options.keys()))
        if selected_label != "— Select —":
            sel_id = user_options[selected_label]
            col_warn, col_btn = st.columns([3,1])
            with col_warn:
                st.markdown(f'<div class="danger-box">⚠️ Deleting: <strong>{selected_label}</strong></div>',
                            unsafe_allow_html=True)
            with col_btn:
                if st.button("🗑️ Confirm Delete", use_container_width=True):
                    ok, msg = delete_user(sel_id)
                    if ok:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
    else:
        st.markdown('<div class="info-box">ℹ️ No patients found matching your filters.</div>',
                    unsafe_allow_html=True)
