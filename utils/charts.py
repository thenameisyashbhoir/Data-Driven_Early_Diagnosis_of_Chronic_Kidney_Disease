"""
utils/charts.py
---------------
Matplotlib/Seaborn chart helpers with the app's dark navy theme.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import seaborn as sns
import io

# ── Dark theme palette ─────────────────────────────────────────────────────────
NAVY    = "#0A1628"
CARD    = "#132238"
CYAN    = "#00D4FF"
GREEN   = "#00E5A0"
ORANGE  = "#FF8C42"
RED     = "#FF3B5C"
GOLD    = "#FFD166"
DIM     = "#7A9CC0"
TEXT    = "#E8F0FE"


def _setup_fig(ax, fig):
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(CARD)
    ax.tick_params(colors=DIM, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor("#1E3A5F")
    ax.xaxis.label.set_color(DIM)
    ax.yaxis.label.set_color(DIM)
    ax.title.set_color(TEXT)


def gauge_chart(prob: float) -> plt.Figure:
    """Semi-circular gauge showing risk probability."""
    colour = GREEN if prob < 30 else (ORANGE if prob < 60 else RED)

    fig, ax = plt.subplots(figsize=(5, 3),
                           subplot_kw=dict(polar=True))
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    # Background arc (grey)
    theta = np.linspace(np.pi, 0, 200)
    ax.plot(theta, [1]*200, color="#1E3A5F", linewidth=18, solid_capstyle="round")

    # Coloured arc for risk value
    end_angle = np.pi - (prob / 100) * np.pi
    theta_val = np.linspace(np.pi, end_angle, 200)
    ax.plot(theta_val, [1]*200, color=colour, linewidth=18, solid_capstyle="round")

    # Labels
    ax.text(0, 0.35, f"{prob}%", ha="center", va="center",
            fontsize=28, fontweight="bold", color=colour,
            fontfamily="DejaVu Sans")
    ax.text(0, 0.05, "CKD Risk Score", ha="center", va="center",
            fontsize=9, color=DIM)

    # Zone labels
    ax.text(np.pi*0.92,   1.28, "0%",   ha="center", color=DIM, fontsize=7)
    ax.text(np.pi*0.5,    1.28, "50%",  ha="center", color=DIM, fontsize=7)
    ax.text(np.pi*0.08,   1.28, "100%", ha="center", color=DIM, fontsize=7)

    ax.set_ylim(0, 1.5)
    ax.set_theta_zero_location("N")
    ax.axis("off")
    plt.tight_layout(pad=0)
    return fig


def risk_bar_chart(features: "pd.DataFrame") -> plt.Figure:
    """Horizontal bar chart of feature contributions."""
    fig, ax = plt.subplots(figsize=(8, max(3.5, len(features) * 0.5)))
    _setup_fig(ax, fig)

    colours = [RED if v > 0 else GREEN for v in features["SHAP Value"]]
    bars = ax.barh(features["Feature"], features["SHAP Value"],
                   color=colours, height=0.55, edgecolor="none")
    ax.axvline(0, color=TEXT, linewidth=0.6, alpha=0.4)
    ax.set_xlabel("Risk Contribution", color=DIM, fontsize=8)
    ax.set_title("Key Contributing Factors", color=TEXT, fontsize=10, fontweight="bold", pad=10)
    ax.invert_yaxis()

    red_p   = mpatches.Patch(color=RED,   label="↑ Increases Risk")
    green_p = mpatches.Patch(color=GREEN, label="↓ Decreases Risk")
    ax.legend(handles=[red_p, green_p], loc="lower right",
              fontsize=7, facecolor=CARD, edgecolor="#1E3A5F",
              labelcolor=TEXT)
    plt.tight_layout()
    return fig


def model_comparison_chart(results_df) -> plt.Figure:
    """Grouped bar chart comparing model metrics."""
    metrics = ["Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"]
    models  = results_df.index.tolist()
    x       = np.arange(len(metrics))
    n       = len(models)
    width   = 0.72 / n
    colours = [CYAN, RED, GREEN, ORANGE, GOLD]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    _setup_fig(ax, fig)
    ax.set_facecolor(CARD)

    for i, (model, row) in enumerate(results_df.iterrows()):
        offset = (i - n/2 + 0.5) * width
        vals   = [row[m] for m in metrics]
        ax.bar(x + offset, vals, width * 0.92, label=model,
               color=colours[i % len(colours)], alpha=0.88, edgecolor="none")

    ax.set_xticks(x); ax.set_xticklabels(metrics, color=DIM, fontsize=8)
    ax.set_ylim(0.5, 1.05)
    ax.set_ylabel("Score", color=DIM, fontsize=8)
    ax.set_title("Model Performance Comparison", color=TEXT, fontsize=11, fontweight="bold")
    ax.legend(fontsize=7, facecolor=CARD, edgecolor="#1E3A5F", labelcolor=TEXT)
    ax.grid(axis="y", alpha=0.12, color=TEXT)
    plt.tight_layout()
    return fig


def risk_trend_chart(risk_trend: list) -> plt.Figure:
    """Line chart of risk % over time."""
    dates = [r["date"] for r in risk_trend]
    risks = [r["risk"] for r in risk_trend]

    fig, ax = plt.subplots(figsize=(9, 3.5))
    _setup_fig(ax, fig)

    ax.fill_between(range(len(risks)), risks, alpha=0.15, color=CYAN)
    ax.plot(range(len(risks)), risks, color=CYAN, linewidth=2,
            marker="o", markersize=6, markerfacecolor=NAVY,
            markeredgecolor=CYAN, markeredgewidth=2)

    # Colour zones
    ax.axhspan(0,  30, alpha=0.05, color=GREEN)
    ax.axhspan(30, 60, alpha=0.05, color=ORANGE)
    ax.axhspan(60, 100, alpha=0.05, color=RED)

    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels(dates, rotation=30, ha="right", color=DIM, fontsize=7)
    ax.set_ylim(0, 105)
    ax.set_ylabel("Risk %", color=DIM, fontsize=8)
    ax.set_title("Risk Score Trend Over Time", color=TEXT, fontsize=10, fontweight="bold")
    ax.grid(alpha=0.08, color=TEXT)

    # Threshold lines
    ax.axhline(30, color=GREEN,  linewidth=0.8, linestyle="--", alpha=0.5)
    ax.axhline(60, color=ORANGE, linewidth=0.8, linestyle="--", alpha=0.5)
    plt.tight_layout()
    return fig


def confusion_matrix_chart(cm) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(4.5, 3.5))
    _setup_fig(ax, fig)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["No CKD","CKD"],
                yticklabels=["No CKD","CKD"],
                ax=ax, linewidths=0.5,
                annot_kws={"size":14, "weight":"bold", "color": TEXT})
    ax.set_title("Confusion Matrix", color=TEXT, fontsize=10, fontweight="bold")
    ax.xaxis.label.set_color(DIM)
    ax.yaxis.label.set_color(DIM)
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.tight_layout()
    return fig


def roc_curve_chart(fpr, tpr, auc_val: float) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(5, 4))
    _setup_fig(ax, fig)
    ax.plot(fpr, tpr, color=CYAN, linewidth=2.5, label=f"ROC-AUC = {auc_val:.4f}")
    ax.plot([0,1],[0,1], color=DIM, linewidth=1, linestyle="--", alpha=0.5)
    ax.fill_between(fpr, tpr, alpha=0.08, color=CYAN)
    ax.set_xlabel("False Positive Rate", color=DIM, fontsize=8)
    ax.set_ylabel("True Positive Rate",  color=DIM, fontsize=8)
    ax.set_title("ROC Curve",           color=TEXT, fontsize=10, fontweight="bold")
    ax.legend(fontsize=8, facecolor=CARD, edgecolor="#1E3A5F", labelcolor=TEXT)
    ax.grid(alpha=0.08, color=TEXT)
    plt.tight_layout()
    return fig


def pie_chart(labels, sizes, colours) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(4, 4))
    fig.patch.set_facecolor(NAVY)
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colours,
        autopct="%1.1f%%", startangle=90,
        wedgeprops=dict(edgecolor=NAVY, linewidth=2),
        textprops=dict(color=TEXT, fontsize=8)
    )
    for at in autotexts:
        at.set_color(NAVY); at.set_fontweight("bold"); at.set_fontsize(8)
    ax.set_facecolor(NAVY)
    plt.tight_layout()
    return fig


def fig_to_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()
