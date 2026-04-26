"""
pages/dashboard.py  ──  Analytics Dashboard (Admin)
"""
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os, sys
from utils.styles import inject_css, page_header
from utils.charts import (confusion_matrix_chart, roc_curve_chart,
                           model_comparison_chart, pie_chart)
from utils.database import get_analytics_db

def render(artefacts):
    inject_css()
    page_header("📈","Analytics Dashboard",
                "System statistics, model performance & prediction analytics")

    analytics = get_analytics_db()

    k1,k2,k3,k4,k5 = st.columns(5)
    kpis = [
        (str(analytics["total_users"]),  "Registered Users",  "#00D4FF"),
        (str(analytics["total"]),        "Total Predictions", "#FFD166"),
        (str(analytics["high"]),         "High Risk Cases",   "#FF3B5C"),
        (f"{analytics['avg_risk']}%",    "Average Risk",      "#FF8C42"),
        (f"{analytics['high_pct']}%",    "High Risk %",       "#FF3B5C"),
    ]
    for col,(val,lbl,clr) in zip([k1,k2,k3,k4,k5],kpis):
        with col:
            st.markdown(f"""<div class="metric-card">
              <div class="metric-val" style="color:{clr};">{val}</div>
              <div class="metric-lbl">{lbl}</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if artefacts:
        st.markdown('<div class="section-header">🤖 Model Comparison</div>', unsafe_allow_html=True)
        fig_mc = model_comparison_chart(artefacts["results_df"])
        st.pyplot(fig_mc, use_container_width=True)
        plt.close(fig_mc)
        st.dataframe(artefacts["results_df"], use_container_width=True)

        col_roc, col_cm = st.columns(2)
        with col_roc:
            try:
                sys.path.insert(0, os.path.join(os.path.dirname(__file__),"..","src"))
                from preprocessing import full_pipeline, scale_features
                from sklearn.model_selection import train_test_split
                from sklearn.metrics import roc_curve, auc
                DATA = os.path.join(os.path.dirname(__file__),"..","data","ckd_dataset_with_id.csv")
                X,y,feat,enc = full_pipeline(DATA)
                Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=0.2,random_state=42,stratify=y)
                _,Xte_sc,scaler = scale_features(Xtr,Xte)
                yp = artefacts["best_model"].predict_proba(Xte_sc)[:,1]
                fpr,tpr,_ = roc_curve(yte,yp)
                fig_r = roc_curve_chart(fpr,tpr,auc(fpr,tpr))
                st.pyplot(fig_r, use_container_width=True); plt.close(fig_r)
            except Exception as e:
                st.info(f"ROC unavailable: {e}")
        with col_cm:
            try:
                from sklearn.metrics import confusion_matrix
                ypred = artefacts["best_model"].predict(Xte_sc)
                fig_c = confusion_matrix_chart(confusion_matrix(yte,ypred))
                st.pyplot(fig_c, use_container_width=True); plt.close(fig_c)
            except Exception: pass

    if analytics["total"] > 0:
        st.markdown('<div class="section-header">🥧 Risk Distribution</div>', unsafe_allow_html=True)
        col_pie, col_det = st.columns([1,2])
        with col_pie:
            labels = ["High Risk","Moderate Risk","Low Risk"]
            sizes  = [analytics["high"],analytics["moderate"],analytics["low"]]
            colours= ["#FF3B5C","#FF8C42","#00E5A0"]
            nz     = [(l,s,c) for l,s,c in zip(labels,sizes,colours) if s>0]
            if nz:
                fig_p = pie_chart([x[0] for x in nz],[x[1] for x in nz],[x[2] for x in nz])
                st.pyplot(fig_p, use_container_width=True); plt.close(fig_p)
        with col_det:
            st.markdown(f"""<div class="ckd-card" style="margin-top:20px;">
              <div style="font-family:'Syne',sans-serif;font-size:0.9rem;font-weight:700;
                          color:#E8F0FE;margin-bottom:14px;">Breakdown</div>
              <div style="display:flex;flex-direction:column;gap:10px;">
                <div style="display:flex;justify-content:space-between;">
                  <span style="font-size:0.85rem;color:#7A9CC0;">🔴 High Risk</span>
                  <span style="font-weight:700;color:#FF3B5C;">{analytics['high']} ({analytics['high_pct']}%)</span>
                </div>
                <div style="display:flex;justify-content:space-between;">
                  <span style="font-size:0.85rem;color:#7A9CC0;">🟡 Moderate</span>
                  <span style="font-weight:700;color:#FF8C42;">{analytics['moderate']}</span>
                </div>
                <div style="display:flex;justify-content:space-between;">
                  <span style="font-size:0.85rem;color:#7A9CC0;">🟢 Low Risk</span>
                  <span style="font-weight:700;color:#00E5A0;">{analytics['low']}</span>
                </div>
                <div style="display:flex;justify-content:space-between;border-top:1px solid rgba(0,212,255,0.1);padding-top:10px;">
                  <span style="font-size:0.85rem;color:#7A9CC0;">Total Predictions</span>
                  <span style="font-size:1.1rem;font-weight:800;color:#00D4FF;">{analytics['total']}</span>
                </div>
              </div></div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">ℹ️ No screenings yet.</div>', unsafe_allow_html=True)
