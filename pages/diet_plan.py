"""
pages/diet_plan.py  ──  Personalized CKD Diet Plan
AI-generated diet plans based on patient risk level and profile
PDF download with patient details via ReportLab
"""
import io
import datetime
import streamlit as st
from utils.styles import inject_css, page_header


# ── Static diet data ───────────────────────────────────────────────────────────
DIET_DATA = {
    "High": {
        "color": "#FF3B5C",
        "icon": "🔴",
        "label": "High Risk CKD Diet",
        "description": "Strict kidney-protective diet — low potassium, phosphorus, sodium & protein",
        "daily_limits": {
            "Protein": "40–50g/day",
            "Sodium": "< 1,500mg/day",
            "Potassium": "< 2,000mg/day",
            "Phosphorus": "< 800mg/day",
            "Fluid": "As advised by doctor",
        },
        "eat_freely": [
            "Apples, berries, grapes (small portions)",
            "Cabbage, cauliflower, green beans",
            "White rice, white bread, pasta",
            "Egg whites (2–3 per day)",
            "Olive oil, unsalted butter",
            "Honey, sugar (in moderation)",
            "Herbs (not salt-based seasonings)",
        ],
        "avoid": [
            "Bananas, oranges, potatoes (high potassium)",
            "Dairy products — milk, cheese, yogurt (high phosphorus)",
            "Nuts, seeds, whole grains (high phosphorus)",
            "Processed meats, canned foods (high sodium)",
            "Dark colas, chocolate (high phosphorus)",
            "Tomatoes, spinach, avocado (high potassium)",
            "Red meat, organ meats (high protein & phosphorus)",
        ],
        "meal_plan": [
            ("Breakfast",     "White rice porridge with egg white omelette + apple slices + herbal tea"),
            ("Mid-Morning",   "Small bowl of grapes or berries"),
            ("Lunch",         "White rice + boiled chicken breast (60g) + steamed cauliflower + cabbage salad"),
            ("Evening Snack", "Plain white crackers with unsalted butter"),
            ("Dinner",        "Pasta with olive oil + boiled fish (60g) + steamed green beans"),
        ],
        "tips": [
            "Track fluid intake carefully if you have swelling",
            "Use lemon juice and herbs instead of salt for flavor",
            "Get blood tests every 3 months to monitor levels",
            "Work with a renal dietitian for personalized advice",
            "Take phosphorus binders if prescribed with meals",
        ]
    },
    "Moderate": {
        "color": "#FF8C42",
        "icon": "🟠",
        "label": "Moderate Risk CKD Diet",
        "description": "Kidney-friendly diet — moderate restrictions on key nutrients",
        "daily_limits": {
            "Protein": "50–60g/day",
            "Sodium": "< 2,000mg/day",
            "Potassium": "< 3,000mg/day",
            "Phosphorus": "< 1,000mg/day",
            "Fluid": "6–8 glasses/day",
        },
        "eat_freely": [
            "Apples, berries, pears, peaches",
            "Broccoli, cauliflower, cabbage, peppers",
            "White rice, bread, pasta, oats",
            "Eggs (1–2 per day, whites preferred)",
            "Fish (2–3 times/week, moderate portions)",
            "Olive oil, canola oil",
            "Small portions of white beans or lentils",
        ],
        "avoid": [
            "High-potassium fruits: bananas, dried fruits, coconut",
            "Limit dairy: max 1 serving/day",
            "Processed snacks, fast food (high sodium)",
            "Cola drinks, chocolate desserts",
            "High-protein diets or protein supplements",
            "Excessive salt — use max 1/2 tsp/day",
        ],
        "meal_plan": [
            ("Breakfast",     "Oatmeal with berries + 1 egg + green tea"),
            ("Mid-Morning",   "Apple or pear + small handful of unsalted crackers"),
            ("Lunch",         "Rice/chapati + dal (lentils, moderate) + vegetable sabji + salad"),
            ("Evening Snack", "Roasted makhana or poha with herbs"),
            ("Dinner",        "Grilled fish or chicken (80g) + steamed vegetables + rice"),
        ],
        "tips": [
            "Drink 6–8 glasses of water daily unless restricted",
            "Cook at home to control sodium intake",
            "30 minutes of light exercise (walking) most days",
            "Monitor blood pressure daily if you have hypertension",
            "Visit nephrologist every 6 months",
        ]
    },
    "Low": {
        "color": "#00E5A0",
        "icon": "🟢",
        "label": "Low Risk Kidney-Healthy Diet",
        "description": "Preventive kidney-friendly diet to maintain kidney function",
        "daily_limits": {
            "Protein": "60–80g/day",
            "Sodium": "< 2,300mg/day",
            "Potassium": "Normal (3,500–4,700mg)",
            "Phosphorus": "Normal intake",
            "Fluid": "8–10 glasses/day",
        },
        "eat_freely": [
            "All vegetables — especially leafy greens",
            "All fresh fruits — berries, citrus, melons",
            "Whole grains — brown rice, oats, quinoa",
            "Fish, lean chicken, eggs",
            "Legumes — lentils, chickpeas, beans",
            "Dairy — yogurt, milk (1–2 servings/day)",
            "Nuts and seeds (small portions)",
        ],
        "avoid": [
            "Processed and ultra-processed foods",
            "Excessive red meat or organ meats",
            "High-sugar beverages — sodas, juices",
            "Excess salt / high-sodium condiments",
            "Alcohol (or limit strictly)",
            "Fried and fast food",
        ],
        "meal_plan": [
            ("Breakfast",     "Daliya/oats with fruits + 2 eggs + green tea or low-fat milk"),
            ("Mid-Morning",   "Seasonal fruit + handful of mixed nuts"),
            ("Lunch",         "Brown rice/chapati + dal + paneer/chicken + salad + buttermilk"),
            ("Evening Snack", "Sprout chaat or fruit smoothie"),
            ("Dinner",        "Grilled fish or sabzi + whole wheat roti + raita"),
        ],
        "tips": [
            "Drink 8–10 glasses of water daily — kidneys love hydration",
            "Exercise 30–45 min daily to support kidney health",
            "Use minimal salt; prefer rock salt over table salt",
            "Annual kidney function test (creatinine, GFR, urine test)",
            "Quit smoking — it significantly worsens kidney disease",
            "Control blood sugar if diabetic — #1 cause of CKD",
        ]
    }
}

# Map DB risk_level values → diet keys
RISK_MAP = {
    "High Risk":     "High",
    "Moderate Risk": "Moderate",
    "Low Risk":      "Low",
    "High":          "High",
    "Moderate":      "Moderate",
    "Low":           "Low",
}


def _get_risk_from_session() -> str:
    """Try every possible session key to find a stored risk level."""
    # 1) Direct last_result (set by screening/results pages)
    result = st.session_state.get("last_result")
    if isinstance(result, dict):
        rl = result.get("risk_level", "")
        if rl in RISK_MAP:
            return RISK_MAP[rl]

    # 2) last_prediction (older key)
    result2 = st.session_state.get("last_prediction")
    if isinstance(result2, dict):
        rl = result2.get("risk_level", "")
        if rl in RISK_MAP:
            return RISK_MAP[rl]

    # 3) Fetch latest prediction from DB
    user_id = st.session_state.get("user_id")
    if user_id:
        try:
            from utils.database import get_user_predictions
            preds = get_user_predictions(user_id)
            if preds:
                rl = preds[0].get("risk_level", "")
                if rl in RISK_MAP:
                    return RISK_MAP[rl]
        except Exception:
            pass

    return ""


def _generate_pdf(patient_name: str, risk_key: str,
                  user_info: dict, result: dict) -> bytes:
    """Generate a styled PDF diet plan using ReportLab and return bytes."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, HRFlowable)
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    data = DIET_DATA[risk_key]
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=14*mm, bottomMargin=14*mm,
        title=f"CKD Diet Plan – {patient_name}"
    )

    # ── Colours ──────────────────────────────────────────────────────────────
    NAVY      = colors.HexColor("#0A1628")
    NAVY_MID  = colors.HexColor("#0F2040")
    NAVY_CARD = colors.HexColor("#132238")
    CYAN      = colors.HexColor("#00D4FF")
    GREEN     = colors.HexColor("#00E5A0")
    ORANGE    = colors.HexColor("#FF8C42")
    RED       = colors.HexColor("#FF3B5C")
    GOLD      = colors.HexColor("#FFD166")
    WHITE     = colors.white
    DIM       = colors.HexColor("#7A9CC0")
    RISK_COLOR = {"High": RED, "Moderate": ORANGE, "Low": GREEN}[risk_key]

    # ── Styles ───────────────────────────────────────────────────────────────
    def sty(name, **kw):
        return ParagraphStyle(name, **kw)

    S = {
        "title"   : sty("title",    fontSize=22, textColor=CYAN,
                         fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=2),
        "subtitle": sty("sub",      fontSize=9,  textColor=DIM,
                         fontName="Helvetica",     alignment=TA_CENTER, spaceAfter=6),
        "sec"     : sty("sec",      fontSize=11, textColor=CYAN,
                         fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4),
        "body"    : sty("body",     fontSize=9,  textColor=WHITE,
                         fontName="Helvetica",     spaceAfter=3, leading=13),
        "bullet"  : sty("bullet",   fontSize=9,  textColor=WHITE,
                         fontName="Helvetica",     leftIndent=12, spaceAfter=2,
                         leading=13),
        "risk_lbl": sty("risk_lbl", fontSize=13, textColor=RISK_COLOR,
                         fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=3),
        "risk_sub": sty("risk_sub", fontSize=8,  textColor=DIM,
                         fontName="Helvetica",     alignment=TA_CENTER, spaceAfter=8),
        "footer"  : sty("footer",   fontSize=7,  textColor=DIM,
                         fontName="Helvetica",     alignment=TA_CENTER),
        "cell_hdr": sty("cell_hdr", fontSize=8,  textColor=CYAN,
                         fontName="Helvetica-Bold"),
        "cell_val": sty("cell_val", fontSize=9,  textColor=WHITE,
                         fontName="Helvetica-Bold"),
        "cell_dim": sty("cell_dim", fontSize=8,  textColor=DIM,
                         fontName="Helvetica"),
    }

    story = []
    W = A4[0] - 36*mm   # usable width

    # ── Header Banner ────────────────────────────────────────────────────────
    hdr_data = [[
        Paragraph("CKD Early Diagnosis System", sty("h1", fontSize=16,
                  textColor=CYAN, fontName="Helvetica-Bold", alignment=TA_CENTER)),
        Paragraph("Personalized Diet Plan", sty("h2", fontSize=10,
                  textColor=DIM, fontName="Helvetica", alignment=TA_CENTER)),
    ]]
    hdr_tbl = Table([[Paragraph(
        "CKD Early Diagnosis System  |  Personalized Diet Plan",
        sty("hdr", fontSize=14, textColor=CYAN, fontName="Helvetica-Bold",
            alignment=TA_CENTER)
    )]], colWidths=[W])
    hdr_tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), NAVY_MID),
        ("TOPPADDING",  (0,0), (-1,-1), 10),
        ("BOTTOMPADDING",(0,0),(-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING",(0,0), (-1,-1), 8),
        ("ROUNDEDCORNERS", [6]),
        ("BOX",         (0,0), (-1,-1), 1, CYAN),
    ]))
    story.append(hdr_tbl)
    story.append(Spacer(1, 6))

    # ── Patient Info ─────────────────────────────────────────────────────────
    story.append(Paragraph("Patient Information", S["sec"]))
    age    = user_info.get("age", "—")
    gender = user_info.get("gender", "—")
    bg     = user_info.get("blood_group", "—")
    city   = user_info.get("city", "—")
    state  = user_info.get("state", "—")
    contact= user_info.get("contact", "—")
    date_str = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

    info_rows = [
        [Paragraph("Full Name",    S["cell_dim"]), Paragraph(patient_name, S["cell_val"]),
         Paragraph("Date",         S["cell_dim"]), Paragraph(date_str,     S["cell_val"])],
        [Paragraph("Age",          S["cell_dim"]), Paragraph(str(age),     S["cell_val"]),
         Paragraph("Gender",       S["cell_dim"]), Paragraph(str(gender),  S["cell_val"])],
        [Paragraph("Blood Group",  S["cell_dim"]), Paragraph(str(bg),      S["cell_val"]),
         Paragraph("Contact",      S["cell_dim"]), Paragraph(str(contact), S["cell_val"])],
        [Paragraph("City",         S["cell_dim"]), Paragraph(str(city),    S["cell_val"]),
         Paragraph("State",        S["cell_dim"]), Paragraph(str(state),   S["cell_val"])],
    ]
    # Add risk level from result if available
    if result:
        risk_pct = result.get("risk_percent", "")
        stage    = result.get("stage", "")
        info_rows.append([
            Paragraph("CKD Risk Level", S["cell_dim"]),
            Paragraph(result.get("risk_level", "—"), S["cell_val"]),
            Paragraph("Stage",          S["cell_dim"]),
            Paragraph(str(stage) if stage else "—", S["cell_val"]),
        ])
        if risk_pct:
            info_rows.append([
                Paragraph("Risk Score", S["cell_dim"]),
                Paragraph(f"{risk_pct:.1f}%" if isinstance(risk_pct, float) else str(risk_pct),
                          S["cell_val"]),
                Paragraph("", S["cell_dim"]), Paragraph("", S["cell_val"]),
            ])

    col_w = W / 4
    info_tbl = Table(info_rows, colWidths=[col_w*0.85, col_w*1.15, col_w*0.85, col_w*1.15])
    info_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), NAVY_CARD),
        ("ROWBACKGROUNDS",(0,0), (-1,-1), [NAVY_CARD, colors.HexColor("#0D1E35")]),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 7),
        ("RIGHTPADDING",  (0,0), (-1,-1), 7),
        ("BOX",           (0,0), (-1,-1), 0.5, CYAN),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, colors.HexColor("#1A3050")),
        ("ROUNDEDCORNERS",[4]),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 8))

    # ── Risk Level Badge ─────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=CYAN))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"{data['label']}", S["risk_lbl"]))
    story.append(Paragraph(data["description"], S["risk_sub"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=CYAN))
    story.append(Spacer(1, 6))

    # ── Daily Limits ─────────────────────────────────────────────────────────
    story.append(Paragraph("Daily Nutrient Limits", S["sec"]))
    limit_items = list(data["daily_limits"].items())
    limit_rows  = [limit_items[i:i+3] for i in range(0, len(limit_items), 3)]
    for row in limit_rows:
        cells = []
        for nutrient, limit in row:
            cells.append(Table(
                [[Paragraph(nutrient, S["cell_dim"])],
                 [Paragraph(limit,    S["cell_val"])]],
                colWidths=[W / 3 - 4]
            ))
        while len(cells) < 3:
            cells.append(Paragraph("", S["body"]))
        row_tbl = Table([cells], colWidths=[W/3]*3)
        row_tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0,0), (-1,-1), NAVY_CARD),
            ("BOX",          (0,0), (-1,-1), 0.5, colors.HexColor("#1A3050")),
            ("LEFTPADDING",  (0,0), (-1,-1), 8),
            ("RIGHTPADDING", (0,0), (-1,-1), 8),
            ("TOPPADDING",   (0,0), (-1,-1), 6),
            ("BOTTOMPADDING",(0,0), (-1,-1), 6),
        ]))
        story.append(row_tbl)
        story.append(Spacer(1, 3))
    story.append(Spacer(1, 4))

    # ── Foods side by side ───────────────────────────────────────────────────
    def food_list_table(title, items, border_color):
        rows = [[Paragraph(title,
                  sty("food_hdr", fontSize=9, textColor=border_color,
                      fontName="Helvetica-Bold"))]]
        for item in items:
            rows.append([Paragraph(f"  • {item}", S["bullet"])])
        t = Table(rows, colWidths=[W/2 - 4])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (0,0),  NAVY_MID),
            ("BACKGROUND",    (0,1), (-1,-1), NAVY_CARD),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
            ("RIGHTPADDING",  (0,0), (-1,-1), 8),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LINEBEFORE",    (0,0), (-1,-1), 2, border_color),
            ("BOX",           (0,0), (-1,-1), 0.4, colors.HexColor("#1A3050")),
        ]))
        return t

    eat_t  = food_list_table("Foods to Include", data["eat_freely"], GREEN)
    avoid_t= food_list_table("Foods to Avoid",   data["avoid"],      RED)
    food_tbl = Table([[eat_t, avoid_t]], colWidths=[W/2, W/2])
    food_tbl.setStyle(TableStyle([
        ("LEFTPADDING",  (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING",   (0,0), (-1,-1), 0),
        ("BOTTOMPADDING",(0,0), (-1,-1), 0),
        ("INNERGRID",    (0,0), (-1,-1), 0, colors.white),
    ]))
    story.append(Paragraph("Food Guide", S["sec"]))
    story.append(food_tbl)
    story.append(Spacer(1, 8))

    # ── Meal Plan ────────────────────────────────────────────────────────────
    story.append(Paragraph("Sample Daily Meal Plan", S["sec"]))
    meal_rows = [[
        Paragraph("Time", sty("mh", fontSize=8, textColor=CYAN,
                  fontName="Helvetica-Bold")),
        Paragraph("Meal", sty("mh2", fontSize=8, textColor=CYAN,
                  fontName="Helvetica-Bold")),
    ]]
    for time_lbl, meal in data["meal_plan"]:
        meal_rows.append([
            Paragraph(time_lbl, sty("ml", fontSize=8, textColor=DIM,
                      fontName="Helvetica-Bold")),
            Paragraph(meal,     S["body"]),
        ])
    meal_tbl = Table(meal_rows, colWidths=[30*mm, W - 30*mm])
    meal_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  NAVY_MID),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [NAVY_CARD, colors.HexColor("#0D1E35")]),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("BOX",           (0,0), (-1,-1), 0.5, CYAN),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, colors.HexColor("#1A3050")),
        ("LINEAFTER",     (0,0), (0,-1),  0.5, colors.HexColor("#1A3050")),
    ]))
    story.append(meal_tbl)
    story.append(Spacer(1, 8))

    # ── Key Tips ─────────────────────────────────────────────────────────────
    story.append(Paragraph("Key Health Tips", S["sec"]))
    tips_rows = []
    for tip in data["tips"]:
        tips_rows.append([Paragraph(f"  • {tip}", S["bullet"])])
    tips_tbl = Table(tips_rows, colWidths=[W])
    tips_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [NAVY_CARD, colors.HexColor("#0D1E35")]),
        ("TOPPADDING",   (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",  (0,0),(-1,-1), 8),
        ("RIGHTPADDING", (0,0),(-1,-1), 8),
        ("BOX",          (0,0),(-1,-1), 0.5, colors.HexColor("#1A3050")),
        ("LINEBEFORE",   (0,0),(0,-1),  2,   CYAN),
    ]))
    story.append(tips_tbl)
    story.append(Spacer(1, 10))

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=CYAN))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "This diet plan is for general guidance only. "
        "Please consult your nephrologist or a registered renal dietitian for personalised advice. "
        "CKD Early Diagnosis System  |  AI-Powered Medical Screening",
        S["footer"]
    ))

    doc.build(story)
    buf.seek(0)
    return buf.read()


def render():
    inject_css()
    if st.session_state.get("user_role") == "guest":
        st.markdown('<div class="danger-box">🚫 Please create an account to access your Diet Plan.</div>',
                    unsafe_allow_html=True)
        return

    page_header("🥗", "Personalized Diet Plan",
                "Kidney-friendly nutrition based on your CKD risk level")

    user_info    = st.session_state.get("user_info", {})
    patient_name = user_info.get("patient_name", "Patient")

    # ── Resolve risk level ────────────────────────────────────────────────────
    risk_key = _get_risk_from_session()
    result   = (st.session_state.get("last_result") or
                st.session_state.get("last_prediction") or {})

    if risk_key:
        st.markdown(f"""
        <div class="success-box" style="margin-bottom:16px;">
          ✅ Showing personalised diet plan based on your latest screening:
          <strong>{risk_key} Risk</strong>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-box" style="margin-bottom:12px;">
          ℹ️ No recent screening found. Select your risk level below,
          or go to <strong>Screening</strong> first for an AI-powered assessment.
        </div>
        """, unsafe_allow_html=True)
        risk_key = st.selectbox(
            "Select your CKD Risk Level",
            ["Low", "Moderate", "High"],
            index=0, key="diet_risk_select"
        )

    data  = DIET_DATA[risk_key]
    color = data["color"]

    # ── Header card ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(10,22,40,0.95),rgba(19,34,56,0.98));
                border:2px solid {color}44; border-radius:14px; padding:20px 24px;
                margin-bottom:20px;">
      <div style="display:flex; align-items:center; gap:12px;">
        <span style="font-size:2.2rem;">{data['icon']}</span>
        <div>
          <div style="font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:800;
                      color:{color};">{data['label']}</div>
          <div style="font-size:0.82rem; color:#7A9CC0; margin-top:3px;">{data['description']}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Daily Limits ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Daily Nutrient Limits</div>',
                unsafe_allow_html=True)
    limit_cols = st.columns(len(data["daily_limits"]))
    for col, (nutrient, limit) in zip(limit_cols, data["daily_limits"].items()):
        col.markdown(f"""
        <div style="background:rgba(10,22,40,0.7); border:1px solid {color}33;
                    border-radius:10px; padding:12px; text-align:center;">
          <div style="font-size:0.7rem; color:#7A9CC0; text-transform:uppercase;
                      letter-spacing:0.1em; margin-bottom:4px;">{nutrient}</div>
          <div style="font-size:0.88rem; font-weight:700; color:{color};">{limit}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Food lists ────────────────────────────────────────────────────────────
    col_eat, col_avoid = st.columns(2)
    with col_eat:
        st.markdown('<div class="section-header">✅ Foods to Include</div>',
                    unsafe_allow_html=True)
        items_html = "".join(
            f'<div style="padding:6px 10px;margin:3px 0;background:rgba(0,229,160,0.07);'
            f'border-left:3px solid #00E5A0;border-radius:0 6px 6px 0;'
            f'font-size:0.83rem;color:#E8F0FE;">✅ {item}</div>'
            for item in data["eat_freely"]
        )
        st.markdown(items_html, unsafe_allow_html=True)

    with col_avoid:
        st.markdown('<div class="section-header">❌ Foods to Limit/Avoid</div>',
                    unsafe_allow_html=True)
        items_html = "".join(
            f'<div style="padding:6px 10px;margin:3px 0;background:rgba(255,59,92,0.07);'
            f'border-left:3px solid #FF3B5C;border-radius:0 6px 6px 0;'
            f'font-size:0.83rem;color:#E8F0FE;">❌ {item}</div>'
            for item in data["avoid"]
        )
        st.markdown(items_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Meal plan ─────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🍽️ Sample Daily Meal Plan</div>',
                unsafe_allow_html=True)
    for time_label, meal in data["meal_plan"]:
        st.markdown(f"""
        <div style="display:flex;gap:14px;align-items:flex-start;padding:10px 14px;
                    background:rgba(10,22,40,0.6);border:1px solid rgba(0,212,255,0.1);
                    border-radius:10px;margin-bottom:6px;">
          <div style="min-width:120px;font-size:0.8rem;font-weight:700;color:#00D4FF;
                      padding-top:1px;">{time_label}</div>
          <div style="font-size:0.84rem;color:#E8F0FE;line-height:1.5;">{meal}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tips ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">💡 Key Health Tips</div>',
                unsafe_allow_html=True)
    tips_html = "".join(
        f'<div style="padding:8px 14px;margin:4px 0;background:rgba(0,212,255,0.06);'
        f'border:1px solid rgba(0,212,255,0.15);border-radius:8px;'
        f'font-size:0.84rem;color:#E8F0FE;">💡 {tip}</div>'
        for tip in data["tips"]
    )
    st.markdown(tips_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Download PDF ──────────────────────────────────────────────────────────
    col_dl, col_chat, _ = st.columns([2, 2, 2])
    with col_dl:
        with st.spinner("Preparing PDF…"):
            pdf_bytes = _generate_pdf(patient_name, risk_key, user_info, result)
        fname = f"CKD_Diet_Plan_{patient_name.replace(' ', '_')}_{risk_key}.pdf"
        st.download_button(
            "⬇️ Download Diet Plan (PDF)",
            data=pdf_bytes,
            file_name=fname,
            mime="application/pdf",
            use_container_width=True
        )

    with col_chat:
        if st.button("🤖 Ask AI Assistant", use_container_width=True, key="diet_to_chat"):
            st.session_state.current_page = "AI Assistant"
            if "chat_messages" not in st.session_state:
                st.session_state.chat_messages = []
            st.session_state.chat_messages.append({
                "role": "user",
                "content": (f"I have {risk_key} Risk CKD. "
                            "Can you give me more details about my diet and some recipe ideas?")
            })
            st.rerun()

    st.markdown("""
    <div class="disclaimer" style="margin-top:14px;">
      🔬 Diet guidelines based on NKF KDOQI &amp; Indian CKD dietary recommendations.
      Always consult a registered renal dietitian for personalised meal planning.
    </div>
    """, unsafe_allow_html=True)
