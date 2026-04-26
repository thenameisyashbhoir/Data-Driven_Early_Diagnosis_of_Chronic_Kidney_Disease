"""
pages/chatbot.py  ──  CKD AI Health Assistant + Diet Plan
• Proper chat UI using st.chat_message (native Streamlit chat)
• Diet Plan tab with PDF download
"""
import io
import datetime
import streamlit as st
from utils.styles import inject_css, page_header
from utils.database import get_current_user, get_user_predictions


# ── Diet plan data ─────────────────────────────────────────────────────────────
def get_diet_plan(risk_level: str) -> dict:
    base = {
        "Low Risk": {
            "title": "Preventive Kidney Health Diet",
            "color": "#00E5A0",
            "icon": "🥦",
            "summary": "Focus on hydration, limiting processed foods, and maintaining a balanced diet rich in fruits, vegetables, and lean proteins.",
            "daily_water": "2.0-2.5 litres",
            "protein": "0.8-1.0 g/kg body weight",
            "sodium": "< 2300 mg/day",
            "potassium": "Normal: 3500-4700 mg/day",
            "phosphorus": "Normal: 700-1000 mg/day",
            "foods_eat": [
                ("🥦", "Broccoli, cabbage, cauliflower", "Low potassium, kidney-friendly"),
                ("🍎", "Apples, berries, grapes", "Antioxidants, low potassium"),
                ("🐟", "Fish (salmon, tuna)", "Omega-3, lean protein"),
                ("🍚", "White rice, white bread", "Low potassium & phosphorus"),
                ("🥚", "Egg whites", "High-quality protein, low phosphorus"),
                ("🫙", "Olive oil", "Healthy fats, anti-inflammatory"),
            ],
            "foods_limit": [
                ("🧂", "Salt & processed foods", "High sodium damages kidneys"),
                ("🥩", "Red meat", "High protein load on kidneys"),
                ("🥤", "Sugary drinks", "Linked to diabetes/hypertension"),
                ("🍺", "Alcohol", "Dehydrates and stresses kidneys"),
            ],
            "meals": {
                "Breakfast": ["Oatmeal with berries and apple slices", "1 egg white omelette with bell peppers", "Herbal tea or water"],
                "Lunch": ["Grilled fish with steamed cauliflower & white rice", "Cucumber salad with olive oil dressing", "1 cup water"],
                "Dinner": ["Chicken breast with boiled pasta", "Steamed broccoli with garlic", "Apple for dessert"],
                "Snacks": ["Apple slices", "Rice cakes", "Handful of grapes"],
            },
            "tips": [
                "Stay well-hydrated throughout the day",
                "Limit packaged and canned foods (high sodium)",
                "Exercise 30 min daily to maintain healthy BP",
                "Get annual kidney function tests (eGFR, creatinine)",
            ]
        },
        "Moderate Risk": {
            "title": "CKD-Protective Kidney Diet",
            "color": "#FF8C42",
            "icon": "⚠️",
            "summary": "Moderate protein restriction, reduced sodium & potassium. Focus on kidney-safe foods and regular monitoring.",
            "daily_water": "1.5-2.0 litres (as advised by doctor)",
            "protein": "0.6-0.8 g/kg body weight",
            "sodium": "< 1500 mg/day",
            "potassium": "Reduced: 2000-3000 mg/day",
            "phosphorus": "Reduced: 600-800 mg/day",
            "foods_eat": [
                ("🥬", "White cabbage, lettuce, green beans", "Low potassium vegetables"),
                ("🍊", "Apples, berries, pineapple", "Safe fruits for CKD"),
                ("🍚", "White rice, pasta, white bread", "Low phosphorus carbs"),
                ("🥚", "Egg whites only", "Pure protein, low phosphorus"),
                ("🐓", "Small portions of chicken (boiled)", "Lean protein source"),
                ("🫙", "Olive/canola oil", "Heart-healthy fats"),
            ],
            "foods_limit": [
                ("🍌", "Bananas, oranges, potatoes", "Very high potassium"),
                ("🧀", "Dairy (milk, cheese, yogurt)", "High phosphorus"),
                ("🫘", "Beans, lentils, nuts", "High potassium & phosphorus"),
                ("🥩", "Red meat, organ meats", "High protein & phosphorus"),
                ("🧂", "Salt substitutes (KCl)", "High potassium — dangerous!"),
                ("🍫", "Chocolate, cola drinks", "Very high phosphorus"),
            ],
            "meals": {
                "Breakfast": ["Scrambled egg whites with white toast", "Apple slices or berries", "Herbal tea (no milk)"],
                "Lunch": ["Small portion boiled chicken with white rice", "Boiled cabbage with olive oil", "Water (measured amount)"],
                "Dinner": ["Pasta with egg white sauce and herbs", "Steamed green beans", "Fresh apple or pineapple"],
                "Snacks": ["Rice cakes", "Apple", "Small portion of berries"],
            },
            "tips": [
                "Leach vegetables: peel, cut, boil in large water to reduce potassium",
                "Avoid salt substitutes — they contain potassium chloride",
                "Track fluid intake if your doctor has advised limits",
                "Consult a renal dietitian for personalized meal plans",
                "Get kidney function checked every 3-6 months",
            ]
        },
        "High Risk": {
            "title": "CKD Medical Nutrition Therapy",
            "color": "#FF3B5C",
            "icon": "🚨",
            "summary": "Strict dietary management essential. Low protein, very low potassium & phosphorus. Work closely with your nephrologist and renal dietitian.",
            "daily_water": "Fluid restricted — as prescribed by doctor",
            "protein": "0.5-0.6 g/kg (or as prescribed)",
            "sodium": "< 1000 mg/day",
            "potassium": "Strictly: < 2000 mg/day",
            "phosphorus": "Strictly: < 600 mg/day",
            "foods_eat": [
                ("🍚", "White rice, white pasta, white bread", "Only low-phosphorus carbs"),
                ("🥬", "Boiled/leached cabbage, lettuce, carrot", "Post-leaching only"),
                ("🥚", "Egg whites (2-3/day max)", "Controlled protein"),
                ("🍎", "Small apple, blueberries only", "Low potassium fruits"),
                ("🫙", "Olive oil, butter (unsalted)", "Calorie source"),
                ("🍬", "Hard candies, plain cookies", "Calorie without protein"),
            ],
            "foods_limit": [
                ("❌", "ALL dairy products", "Extremely high phosphorus"),
                ("❌", "ALL nuts, seeds, beans", "Very high phosphorus & potassium"),
                ("❌", "ALL whole grains (brown rice, oats)", "High phosphorus"),
                ("❌", "ALL potassium-rich fruits (banana, kiwi, avocado)", "Dangerous potassium"),
                ("❌", "Dark colas, chocolate, beer", "Very high phosphorus"),
                ("❌", "Processed/packaged foods", "Hidden sodium & phosphorus"),
            ],
            "meals": {
                "Breakfast": ["2 egg whites with white toast (unsalted)", "Small portion blueberries", "Limited water or approved fluid"],
                "Lunch": ["White rice with leached boiled vegetables", "Small portion egg white protein", "Measured fluid intake"],
                "Dinner": ["Plain pasta with olive oil and herbs only", "Leached carrot or lettuce", "Small apple"],
                "Snacks": ["Hard candy or plain rice crackers", "Small apple", "Only approved snacks"],
            },
            "tips": [
                "CRITICAL: Work with a registered renal dietitian immediately",
                "Phosphorus binders may be prescribed — take with meals",
                "Label reading is essential — check every food package",
                "Leach ALL vegetables: peel, cut small, boil in large water x2",
                "Track EVERY meal — keep a food diary for your doctor",
                "Dialysis patients have different needs — follow dialysis diet",
                "Seek hospital consultation for personalized medical nutrition plan",
            ]
        }
    }
    return base.get(risk_level, base["Low Risk"])



# ── PDF Generator ──────────────────────────────────────────────────────────────
def _generate_diet_pdf(patient_name, risk_level, user_info, risk_pct):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, HRFlowable)
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER

    plan   = get_diet_plan(risk_level)
    buf    = io.BytesIO()
    doc    = SimpleDocTemplate(buf, pagesize=A4,
                               leftMargin=18*mm, rightMargin=18*mm,
                               topMargin=14*mm, bottomMargin=14*mm,
                               title=f"CKD Diet Plan - {patient_name}")
    W = A4[0] - 36*mm

    NAVY_MID  = colors.HexColor("#0F2040")
    NAVY_CARD = colors.HexColor("#132238")
    NAVY_ALT  = colors.HexColor("#0D1E35")
    CYAN      = colors.HexColor("#00D4FF")
    GREEN     = colors.HexColor("#00E5A0")
    RED       = colors.HexColor("#FF3B5C")
    WHITE     = colors.white
    DIM       = colors.HexColor("#7A9CC0")
    GRID      = colors.HexColor("#1A3050")
    RISK_CLR  = {"High Risk": RED,
                 "Moderate Risk": colors.HexColor("#FF8C42"),
                 "Low Risk": GREEN}.get(risk_level, CYAN)

    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    story = []

    # Header banner
    hdr = Table([[Paragraph("CKD Early Diagnosis System  |  Personalized Diet Plan",
                             S("h", fontSize=13, textColor=CYAN, fontName="Helvetica-Bold",
                               alignment=TA_CENTER))]], colWidths=[W])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), NAVY_MID),
        ("TOPPADDING",   (0,0),(-1,-1), 10), ("BOTTOMPADDING",(0,0),(-1,-1), 10),
        ("BOX",          (0,0),(-1,-1), 1, CYAN),
    ]))
    story += [hdr, Spacer(1, 6)]

    # Patient info
    story.append(Paragraph("Patient Information",
                            S("sec", fontSize=10, textColor=CYAN,
                              fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=4)))
    dim = lambda t: Paragraph(t, S("d", fontSize=7, textColor=DIM, fontName="Helvetica"))
    val = lambda t: Paragraph(str(t), S("v", fontSize=9, textColor=WHITE, fontName="Helvetica-Bold"))
    cw  = W/4
    date_s = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    info_rows = [
        [dim("Full Name"),   val(patient_name),                 dim("Date"),        val(date_s)],
        [dim("Age"),         val(user_info.get("age","—")),      dim("Gender"),      val(user_info.get("gender","—"))],
        [dim("Blood Group"), val(user_info.get("blood_group","—")), dim("Contact"), val(user_info.get("contact","—"))],
        [dim("City"),        val(user_info.get("city","—")),     dim("State"),       val(user_info.get("state","—"))],
        [dim("CKD Risk"),    Paragraph(risk_level, S("rv", fontSize=9, textColor=RISK_CLR,
                             fontName="Helvetica-Bold")),
         dim("Risk Score"),  val(f"{risk_pct:.1f}%" if isinstance(risk_pct,(int,float)) else str(risk_pct))],
    ]
    it = Table(info_rows, colWidths=[cw*0.85, cw*1.15, cw*0.85, cw*1.15])
    it.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[NAVY_CARD, NAVY_ALT]),
        ("TOPPADDING",   (0,0),(-1,-1), 4), ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING",  (0,0),(-1,-1), 6), ("RIGHTPADDING", (0,0),(-1,-1), 6),
        ("BOX",          (0,0),(-1,-1), 0.5, CYAN),
        ("INNERGRID",    (0,0),(-1,-1), 0.3, GRID),
    ]))
    story += [it, Spacer(1, 6),
              HRFlowable(width="100%", thickness=0.5, color=CYAN), Spacer(1, 4)]

    # Risk label
    story += [
        Paragraph(plan["title"], S("rl", fontSize=12, textColor=RISK_CLR,
                  fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=2)),
        Paragraph(plan["summary"], S("rs", fontSize=8, textColor=DIM,
                  fontName="Helvetica", alignment=TA_CENTER, spaceAfter=6)),
        HRFlowable(width="100%", thickness=0.5, color=CYAN), Spacer(1, 6),
    ]

    # Daily limits
    story.append(Paragraph("Daily Nutrient Targets",
                            S("s2", fontSize=10, textColor=CYAN,
                              fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=4)))
    limits = [("Daily Water",plan["daily_water"]),("Protein",plan["protein"]),
              ("Sodium",plan["sodium"]),("Potassium",plan["potassium"]),("Phosphorus",plan["phosphorus"])]
    for row_items in [limits[:3], limits[3:]]:
        cells = [Table([[dim(n)],[val(v)]], colWidths=[W/3-4]) for n,v in row_items]
        while len(cells) < 3:
            cells.append(Paragraph("", S("e", fontSize=8, fontName="Helvetica")))
        rt = Table([cells], colWidths=[W/3]*3)
        rt.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,-1), NAVY_CARD),
            ("LEFTPADDING",  (0,0),(-1,-1), 8), ("RIGHTPADDING",(0,0),(-1,-1), 8),
            ("TOPPADDING",   (0,0),(-1,-1), 5), ("BOTTOMPADDING",(0,0),(-1,-1), 5),
            ("BOX",          (0,0),(-1,-1), 0.4, GRID),
        ]))
        story += [rt, Spacer(1, 3)]
    story.append(Spacer(1, 4))

    # Food guide side-by-side
    def food_col(title, items, bc):
        rows = [[Paragraph(title, S("fh", fontSize=8, textColor=bc, fontName="Helvetica-Bold"))]]
        for icon, food, reason in items:
            rows.append([Paragraph(f"  {icon}  {food}",
                                   S("fi", fontSize=8, textColor=WHITE, fontName="Helvetica"))])
            rows.append([Paragraph(f"      {reason}",
                                   S("fr", fontSize=7, textColor=DIM,   fontName="Helvetica"))])
        t = Table(rows, colWidths=[W/2 - 4])
        t.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(0,0),   NAVY_MID),
            ("BACKGROUND",   (0,1),(-1,-1), NAVY_CARD),
            ("LINEBEFORE",   (0,0),(-1,-1), 2, bc),
            ("LEFTPADDING",  (0,0),(-1,-1), 8), ("RIGHTPADDING",(0,0),(-1,-1), 6),
            ("TOPPADDING",   (0,0),(-1,-1), 3), ("BOTTOMPADDING",(0,0),(-1,-1), 3),
            ("BOX",          (0,0),(-1,-1), 0.3, GRID),
        ]))
        return t

    story.append(Paragraph("Food Guide", S("s3", fontSize=10, textColor=CYAN,
                            fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=4)))
    ft = Table([[food_col("Foods to Include", plan["foods_eat"],  GREEN),
                 food_col("Foods to Avoid",   plan["foods_limit"], RED)]],
               colWidths=[W/2, W/2])
    ft.setStyle(TableStyle([
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING", (0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
    ]))
    story += [ft, Spacer(1, 8)]

    # Meal plan
    story.append(Paragraph("Sample Daily Meal Plan",
                            S("s4", fontSize=10, textColor=CYAN,
                              fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=4)))
    meal_rows = [[
        Paragraph("Meal",  S("mh", fontSize=8, textColor=CYAN, fontName="Helvetica-Bold")),
        Paragraph("Items", S("mh2",fontSize=8, textColor=CYAN, fontName="Helvetica-Bold")),
    ]]
    for mname, items in plan["meals"].items():
        meal_rows.append([
            Paragraph(mname, S("mb", fontSize=8, textColor=DIM, fontName="Helvetica-Bold")),
            Paragraph(" • ".join(items), S("mi", fontSize=8, textColor=WHITE,
                                           fontName="Helvetica", leading=12)),
        ])
    mt = Table(meal_rows, colWidths=[28*mm, W-28*mm])
    mt.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,0),   NAVY_MID),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [NAVY_CARD, NAVY_ALT]),
        ("TOPPADDING",   (0,0),(-1,-1), 5), ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",  (0,0),(-1,-1), 7), ("RIGHTPADDING", (0,0),(-1,-1), 7),
        ("BOX",          (0,0),(-1,-1), 0.5, CYAN),
        ("INNERGRID",    (0,0),(-1,-1), 0.3, GRID),
        ("LINEAFTER",    (0,0),(0,-1),  0.5, GRID),
    ]))
    story += [mt, Spacer(1, 8)]

    # Tips
    story.append(Paragraph("Key Health Tips",
                            S("s5", fontSize=10, textColor=CYAN,
                              fontName="Helvetica-Bold", spaceBefore=4, spaceAfter=4)))
    tip_rows = [[Paragraph(f"  • {tip}", S("ti", fontSize=8, textColor=WHITE,
                            fontName="Helvetica", leftIndent=10, leading=12))]
                for tip in plan["tips"]]
    tt = Table(tip_rows, colWidths=[W])
    tt.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[NAVY_CARD, NAVY_ALT]),
        ("TOPPADDING",   (0,0),(-1,-1), 4), ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("LEFTPADDING",  (0,0),(-1,-1), 8), ("RIGHTPADDING", (0,0),(-1,-1), 8),
        ("LINEBEFORE",   (0,0),(0,-1),  2,  CYAN),
        ("BOX",          (0,0),(-1,-1), 0.4, GRID),
    ]))
    story += [tt, Spacer(1, 10),
              HRFlowable(width="100%", thickness=0.5, color=CYAN), Spacer(1, 4),
              Paragraph("This diet plan is for general guidance only. Consult your nephrologist or "
                        "a registered renal dietitian for personalised advice.  "
                        "CKD Early Diagnosis System  |  AI-Powered Medical Screening",
                        S("ft", fontSize=7, textColor=DIM, fontName="Helvetica",
                          alignment=TA_CENTER))]

    doc.build(story)
    buf.seek(0)
    return buf.read()


# ── Main render ────────────────────────────────────────────────────────────────
def render():
    inject_css()

    st.markdown("""
    <style>
    /* Tighten quick-chip buttons */
    div[data-testid="stHorizontalBlock"] .stButton > button {
        font-size: 0.74rem !important;
        padding: 4px 8px !important;
        height: auto !important;
        white-space: nowrap !important;
    }
    /* Chat message padding */
    .stChatMessage { padding: 4px 0 !important; }
    /* Chat input */
    .stChatInput > div { border-color: rgba(0,212,255,0.3) !important; }
    </style>
    """, unsafe_allow_html=True)

    user = get_current_user()
    if not user:
        st.markdown('<div class="danger-box">🚫 Please log in to access the health assistant.</div>',
                    unsafe_allow_html=True)
        return

    page_header("🤖", "AI Health Assistant", "CKD-focused chatbot & personalized diet plan")

    preds      = get_user_predictions(user["id"])
    last_pred  = preds[0] if preds else None
    risk_level = last_pred["risk_level"] if last_pred else "Low Risk"
    risk_pct   = last_pred.get("risk_percent", 0) if last_pred else 0

    tab_chat, tab_diet = st.tabs(["💬 AI Health Chatbot", "🥗 My Diet Plan"])

    # ══════════════════════════════════════════════════════════════════════════
    # CHATBOT TAB
    # ══════════════════════════════════════════════════════════════════════════
    with tab_chat:
        risk_color = ("#FF3B5C" if "High"     in risk_level else
                      "#FF8C42" if "Moderate" in risk_level else "#00E5A0")

        st.markdown(f"""
        <div class="ckd-card" style="margin-bottom:14px;
             background:linear-gradient(135deg,rgba(0,212,255,0.05),rgba(10,22,40,0.95));">
          <div style="display:flex;align-items:center;gap:12px;">
            <div style="font-size:2rem;">🤖</div>
            <div>
              <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:#00D4FF;">
                CKD Health Assistant</div>
              <div style="font-size:0.78rem;color:#7A9CC0;margin-top:2px;">
                Screening result: <strong style="color:{risk_color};">{risk_level}</strong>
                &nbsp;·&nbsp; Ask about symptoms, diet, medications, or your results.
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Quick chips
        st.markdown('<div style="font-size:0.76rem;color:#7A9CC0;margin-bottom:6px;">💡 Quick questions:</div>',
                    unsafe_allow_html=True)
        CHIPS = [
            ("What is CKD?",        "What is Chronic Kidney Disease? Explain its stages and how it progresses."),
            ("Foods to avoid",      "What foods should I avoid with CKD and why?"),
            ("Improve kidneys",     "How can I slow kidney function decline with CKD?"),
            ("CKD symptoms",        "What are warning signs and symptoms of CKD?"),
            ("My risk level",       f"My CKD risk is {risk_level} ({risk_pct}% probability). What does this mean for me?"),
        ]
        chip_cols = st.columns(len(CHIPS))
        for i, (col, (label, full_q)) in enumerate(zip(chip_cols, CHIPS)):
            if col.button(label, key=f"chip_{i}", use_container_width=True):
                st.session_state.setdefault("chat_messages", [])
                st.session_state.chat_messages.append({"role": "user", "content": full_q})
                st.session_state["_chat_needs_reply"] = True
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Init history
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

        # ── Render chat history using native st.chat_message ─────────────────
        if not st.session_state.chat_messages:
            st.markdown("""
            <div style="background:rgba(10,22,40,0.4);border:1px dashed rgba(0,212,255,0.2);
                         border-radius:12px;padding:28px;text-align:center;margin-bottom:8px;">
              <div style="font-size:1.8rem;margin-bottom:8px;">💬</div>
              <div style="color:#7A9CC0;font-size:0.87rem;">
                Start a conversation! Ask anything about CKD, diet, symptoms, or your health.
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_messages:
                avatar = "👤" if msg["role"] == "user" else "🤖"
                with st.chat_message(msg["role"], avatar=avatar):
                    st.markdown(msg["content"])

        # ── Chat input (native, renders at bottom of chat) ────────────────────
        user_input = st.chat_input(
            "Ask about CKD, diet, symptoms, medications…",
            key="chat_main_input"
        )

        # Clear button
        if st.button("🗑️ Clear chat", key="clear_chat_btn"):
            st.session_state.chat_messages = []
            st.session_state.pop("_chat_needs_reply", None)
            st.rerun()

        # Queue typed message
        if user_input and user_input.strip():
            st.session_state.chat_messages.append({"role": "user", "content": user_input.strip()})
            st.session_state["_chat_needs_reply"] = True
            st.rerun()

        # ── Generate AI reply ─────────────────────────────────────────────────
        if st.session_state.pop("_chat_needs_reply", False):
            system_prompt = (
                f"You are CKDBot, a compassionate AI health assistant specializing in CKD.\n"
                f"Patient: {user.get('patient_name','')}, Age: {user.get('age','')}, "
                f"Gender: {user.get('gender','')}.\n"
                f"Latest CKD risk: {risk_level} ({risk_pct}% probability).\n\n"
                "Guidelines:\n"
                "- Clear, empathetic, medically accurate responses\n"
                "- Always recommend consulting a nephrologist for medical decisions\n"
                "- Be specific about CKD diet (potassium, phosphorus, protein, sodium)\n"
                "- Concise but informative: 2-4 short paragraphs or brief bullet list\n"
                "- Simple language; avoid heavy jargon\n"
                "- For emergencies, urge immediate medical attention\n"
                "- Never start your reply with the word 'I'"
            )
            msgs_api = [{"role": m["role"], "content": m["content"]}
                        for m in st.session_state.chat_messages]

            with st.spinner("🤖 Thinking…"):
                try:
                    import urllib.request, json as _j
                    payload = _j.dumps({
                        "model":      "claude-sonnet-4-20250514",
                        "max_tokens": 800,
                        "system":     system_prompt,
                        "messages":   msgs_api,
                    }).encode()
                    req = urllib.request.Request(
                        "https://api.anthropic.com/v1/messages",
                        data=payload,
                        headers={"Content-Type": "application/json",
                                 "anthropic-version": "2023-06-01"},
                        method="POST"
                    )
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        reply = _j.loads(resp.read())["content"][0]["text"]
                except Exception as e:
                    reply = (
                        "Sorry, I couldn't reach the AI service right now. "
                        "Please try again in a moment.\n\n"
                        f"*(Error: {str(e)[:80]})*"
                    )
            st.session_state.chat_messages.append({"role": "assistant", "content": reply})
            st.rerun()

        st.markdown("""
        <div class="disclaimer" style="font-size:0.72rem;margin-top:10px;">
          ⚕️ <strong>Medical Disclaimer:</strong> CKDBot provides general health information only —
          not a substitute for professional medical advice. Always consult your nephrologist.
        </div>
        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # DIET PLAN TAB
    # ══════════════════════════════════════════════════════════════════════════
    with tab_diet:
        plan = get_diet_plan(risk_level)

        st.markdown(f"""
        <div class="ckd-card ckd-card-glow" style="margin-bottom:20px;
             background:linear-gradient(135deg,rgba(19,34,56,0.98),rgba(10,22,40,0.95));
             border-color:{plan['color']}44;">
          <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
            <div style="font-size:2.8rem;">{plan['icon']}</div>
            <div style="flex:1;">
              <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;
                           color:{plan['color']};margin-bottom:4px;">{plan['title']}</div>
              <div style="font-size:0.85rem;color:#7A9CC0;line-height:1.6;">{plan['summary']}</div>
            </div>
            <div style="background:rgba(0,0,0,0.3);border:1px solid {plan['color']}44;
                         border-radius:12px;padding:12px 20px;text-align:center;">
              <div style="font-size:0.7rem;color:#7A9CC0;text-transform:uppercase;letter-spacing:0.1em;">Risk Level</div>
              <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;
                           color:{plan['color']};margin-top:2px;">{risk_level}</div>
              <div style="font-size:0.75rem;color:#7A9CC0;">{risk_pct}% probability</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Nutrient limits
        st.markdown('<div class="section-header">📊 Daily Nutritional Targets</div>',
                    unsafe_allow_html=True)
        n_cols = st.columns(5)
        nutrients = [
            ("💧", "Daily Water",  plan["daily_water"],  "#00D4FF"),
            ("🥩", "Protein",      plan["protein"],      "#00E5A0"),
            ("🧂", "Sodium",       plan["sodium"],       plan["color"]),
            ("🍌", "Potassium",    plan["potassium"],    "#FFD166"),
            ("🦴", "Phosphorus",   plan["phosphorus"],   "#A78BFA"),
        ]
        for col, (icon, label, val, clr) in zip(n_cols, nutrients):
            col.markdown(f"""
            <div class="metric-card" style="border-color:{clr}33;padding:16px 12px;">
              <div style="font-size:1.5rem;margin-bottom:6px;">{icon}</div>
              <div style="font-size:0.75rem;color:{clr};font-weight:700;margin-bottom:4px;">{label}</div>
              <div style="font-size:0.72rem;color:#E8F0FE;line-height:1.4;">{val}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Food lists
        col_eat, col_avoid = st.columns(2)
        with col_eat:
            st.markdown('<div class="section-header" style="color:#00E5A0;">✅ Foods to Eat</div>',
                        unsafe_allow_html=True)
            for icon, food, reason in plan["foods_eat"]:
                st.markdown(f"""
                <div style="background:rgba(0,229,160,0.05);border:1px solid rgba(0,229,160,0.15);
                             border-radius:8px;padding:10px 13px;margin-bottom:8px;
                             display:flex;align-items:flex-start;gap:10px;">
                  <span style="font-size:1.2rem;">{icon}</span>
                  <div>
                    <div style="font-size:0.85rem;font-weight:600;color:#E8F0FE;">{food}</div>
                    <div style="font-size:0.75rem;color:#00E5A0;margin-top:1px;">{reason}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

        with col_avoid:
            st.markdown('<div class="section-header" style="color:#FF3B5C;">❌ Foods to Limit/Avoid</div>',
                        unsafe_allow_html=True)
            for icon, food, reason in plan["foods_limit"]:
                st.markdown(f"""
                <div style="background:rgba(255,59,92,0.05);border:1px solid rgba(255,59,92,0.15);
                             border-radius:8px;padding:10px 13px;margin-bottom:8px;
                             display:flex;align-items:flex-start;gap:10px;">
                  <span style="font-size:1.2rem;">{icon}</span>
                  <div>
                    <div style="font-size:0.85rem;font-weight:600;color:#E8F0FE;">{food}</div>
                    <div style="font-size:0.75rem;color:#FF3B5C;margin-top:1px;">{reason}</div>
                  </div>
                </div>""", unsafe_allow_html=True)

        # Meal plan
        st.markdown('<div class="section-header">🍽️ Sample Daily Meal Plan</div>',
                    unsafe_allow_html=True)
        meal_cols  = st.columns(4)
        meal_emoji = {"Breakfast":"🌅","Lunch":"☀️","Dinner":"🌙","Snacks":"🍎"}
        meal_color = {"Breakfast":"#FFD166","Lunch":"#00D4FF","Dinner":"#A78BFA","Snacks":"#00E5A0"}
        for col, (mname, items) in zip(meal_cols, plan["meals"].items()):
            clr  = meal_color.get(mname, "#7A9CC0")
            emj  = meal_emoji.get(mname, "🍽️")
            rows = "".join(
                f'<div style="font-size:0.78rem;color:#E8F0FE;padding:3px 0;'
                f'border-bottom:1px solid rgba(255,255,255,0.05);">• {i}</div>'
                for i in items
            )
            col.markdown(f"""
            <div class="ckd-card" style="border-color:{clr}33;padding:14px;">
              <div style="font-size:1.2rem;margin-bottom:6px;">{emj}</div>
              <div style="font-family:'Syne',sans-serif;font-size:0.9rem;font-weight:700;
                           color:{clr};margin-bottom:8px;">{mname}</div>
              {rows}
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tips
        st.markdown('<div class="section-header">💡 Important Tips</div>', unsafe_allow_html=True)
        for tip in plan["tips"]:
            tip_clr = "#FF3B5C" if tip.startswith("CRITICAL") else "#00D4FF"
            st.markdown(f"""
            <div style="background:rgba(0,212,255,0.04);border-left:3px solid {tip_clr};
                         border-radius:0 8px 8px 0;padding:10px 14px;margin-bottom:8px;
                         font-size:0.85rem;color:#E8F0FE;">💡 {tip}</div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # PDF Download + AI chat button
        col_pdf, col_ai, _ = st.columns([2, 2, 2])
        with col_pdf:
            pdf_bytes = _generate_diet_pdf(
                patient_name=user.get("patient_name", "Patient"),
                risk_level=risk_level,
                user_info=user,
                risk_pct=risk_pct,
            )
            fname = (f"CKD_Diet_Plan_"
                     f"{user.get('patient_name','Patient').replace(' ','_')}_"
                     f"{risk_level.replace(' ','_')}.pdf")
            st.download_button(
                "⬇️ Download Diet Plan (PDF)",
                data=pdf_bytes,
                file_name=fname,
                mime="application/pdf",
                use_container_width=True,
                key="diet_pdf_dl",
            )

        with col_ai:
            if st.button("💬 Ask AI About This Diet", use_container_width=True, key="diet_to_chat"):
                st.session_state.setdefault("chat_messages", [])
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": (f"I have {risk_level} CKD. "
                                "Give me more details about my diet plan and easy Indian recipe ideas.")
                })
                st.session_state["_chat_needs_reply"] = True
                st.info("💬 Switch to the **AI Health Chatbot** tab to see the AI response!")

        st.markdown("""
        <div class="disclaimer" style="margin-top:20px;">
          ⚕️ <strong>Important:</strong> This diet plan is a general guideline based on your risk level.
          Please consult a <strong>registered renal dietitian</strong> and your
          <strong>nephrologist</strong> for a personalised medical nutrition therapy plan.
        </div>
        """, unsafe_allow_html=True)
