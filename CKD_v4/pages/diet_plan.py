"""
pages/diet_plan.py  ──  Personalized CKD Diet Plan
AI-generated diet plans based on patient risk level and profile
"""
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
            "🍎 Apples, berries, grapes (small portions)",
            "🥦 Cabbage, cauliflower, green beans",
            "🍚 White rice, white bread, pasta",
            "🥚 Egg whites (2-3 per day)",
            "🫒 Olive oil, unsalted butter",
            "🍯 Honey, sugar (in moderation)",
            "🌿 Herbs (not salt-based seasonings)",
        ],
        "avoid": [
            "🚫 Bananas, oranges, potatoes (high potassium)",
            "🚫 Dairy products — milk, cheese, yogurt (high phosphorus)",
            "🚫 Nuts, seeds, whole grains (high phosphorus)",
            "🚫 Processed meats, canned foods (high sodium)",
            "🚫 Dark colas, chocolate (high phosphorus)",
            "🚫 Tomatoes, spinach, avocado (high potassium)",
            "🚫 Red meat, organ meats (high protein & phosphorus)",
        ],
        "meal_plan": [
            ("☀️ Breakfast", "White rice porridge with egg white omelette + apple slices + herbal tea"),
            ("🌤️ Mid-Morning", "Small bowl of grapes or berries"),
            ("🌞 Lunch", "White rice + boiled chicken breast (60g) + steamed cauliflower + cabbage salad"),
            ("🌅 Evening Snack", "Plain white crackers with unsalted butter"),
            ("🌙 Dinner", "Pasta with olive oil + boiled fish (60g) + steamed green beans"),
        ],
        "tips": [
            "💧 Track fluid intake carefully if you have swelling",
            "🧂 Use lemon juice and herbs instead of salt for flavor",
            "🔬 Get blood tests every 3 months to monitor levels",
            "👨‍⚕️ Work with a renal dietitian for personalized advice",
            "💊 Take phosphorus binders if prescribed with meals",
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
            "🍎 Apples, berries, pears, peaches",
            "🥦 Broccoli, cauliflower, cabbage, peppers",
            "🍚 White rice, bread, pasta, oats",
            "🥚 Eggs (1-2 per day, whites preferred)",
            "🐟 Fish (2-3 times/week, moderate portions)",
            "🫒 Olive oil, canola oil",
            "🫘 Small portions of white beans or lentils",
        ],
        "avoid": [
            "⚠️ High-potassium fruits: bananas, dried fruits, coconut",
            "⚠️ Limit dairy: max 1 serving/day",
            "⚠️ Processed snacks, fast food (high sodium)",
            "⚠️ Cola drinks, chocolate desserts",
            "⚠️ High-protein diets or protein supplements",
            "⚠️ Excessive salt — use max ½ tsp/day",
        ],
        "meal_plan": [
            ("☀️ Breakfast", "Oatmeal with berries + 1 egg + green tea"),
            ("🌤️ Mid-Morning", "Apple or pear + small handful of unsalted crackers"),
            ("🌞 Lunch", "Rice/chapati + dal (lentils, moderate) + vegetable sabji + salad"),
            ("🌅 Evening Snack", "Roasted makhana or poha with herbs"),
            ("🌙 Dinner", "Grilled fish or chicken (80g) + steamed vegetables + rice"),
        ],
        "tips": [
            "💧 Drink 6-8 glasses of water daily unless restricted",
            "🧂 Cook at home to control sodium intake",
            "🏃 30 minutes of light exercise (walking) most days",
            "📊 Monitor blood pressure daily if you have hypertension",
            "🩺 Visit nephrologist every 6 months",
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
            "🥗 All vegetables — especially leafy greens",
            "🍎 All fresh fruits — berries, citrus, melons",
            "🌾 Whole grains — brown rice, oats, quinoa",
            "🐟 Fish, lean chicken, eggs",
            "🫘 Legumes — lentils, chickpeas, beans",
            "🥛 Dairy — yogurt, milk (1-2 servings/day)",
            "🥜 Nuts and seeds (small portions)",
        ],
        "avoid": [
            "🚫 Processed and ultra-processed foods",
            "🚫 Excessive red meat or organ meats",
            "🚫 High-sugar beverages — sodas, juices",
            "🚫 Excess salt / high-sodium condiments",
            "🚫 Alcohol (or limit strictly)",
            "🚫 Fried and fast food",
        ],
        "meal_plan": [
            ("☀️ Breakfast", "Daliya/oats with fruits + 2 eggs + green tea or low-fat milk"),
            ("🌤️ Mid-Morning", "Seasonal fruit + handful of mixed nuts"),
            ("🌞 Lunch", "Brown rice/chapati + dal + paneer/chicken + salad + buttermilk"),
            ("🌅 Evening Snack", "Sprout chaat or fruit smoothie"),
            ("🌙 Dinner", "Grilled fish or sabzi + whole wheat roti + raita"),
        ],
        "tips": [
            "💧 Drink 8-10 glasses of water daily — kidneys love hydration",
            "🏃 Exercise 30–45 min daily to support kidney health",
            "🧂 Use minimal salt; prefer rock salt over table salt",
            "🩺 Annual kidney function test (creatinine, GFR, urine test)",
            "🚭 Quit smoking — it significantly worsens kidney disease",
            "🍭 Control blood sugar if diabetic — #1 cause of CKD",
        ]
    }
}


def render():
    inject_css()
    if st.session_state.get("user_role") == "guest":
        st.markdown('<div class="danger-box">🚫 Please create an account to access your Diet Plan.</div>',
                    unsafe_allow_html=True)
        return

    page_header("🥗", "Personalized Diet Plan", "Kidney-friendly nutrition based on your CKD risk level")

    user_info = st.session_state.get("user_info", {})
    patient_name = user_info.get("patient_name", "Patient")
    last_result = st.session_state.get("last_prediction", {})
    risk_level = last_result.get("risk_level", "") if last_result else ""

    # If no risk level from prediction, let user select
    if risk_level not in ["High", "Moderate", "Low"]:
        st.markdown("""
        <div class="info-box">
          ℹ️ No recent screening found. Select your risk level to view your personalized diet plan,
          or go to <strong>Screening</strong> first for an AI assessment.
        </div>
        """, unsafe_allow_html=True)
        risk_level = st.selectbox("Select your CKD Risk Level",
                                  ["Low", "Moderate", "High"],
                                  index=0, key="diet_risk_select")
    else:
        st.markdown(f"""
        <div class="success-box" style="margin-bottom:16px;">
          ✅ Showing diet plan for your latest screening result:
          <strong>{risk_level} Risk</strong>
        </div>
        """, unsafe_allow_html=True)

    data = DIET_DATA[risk_level]
    color = data["color"]

    # Header card
    st.markdown(f"""
    <div style="background:linear-gradient(135deg, rgba(10,22,40,0.95), rgba(19,34,56,0.98));
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

    # Daily Limits
    st.markdown('<div class="section-header">📊 Daily Nutrient Limits</div>', unsafe_allow_html=True)
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

    # Foods to eat / avoid
    col_eat, col_avoid = st.columns(2)
    with col_eat:
        st.markdown('<div class="section-header">✅ Foods to Include</div>', unsafe_allow_html=True)
        items_html = "".join(
            f'<div style="padding:6px 10px; margin:3px 0; background:rgba(0,229,160,0.07); '
            f'border-left:3px solid #00E5A0; border-radius:0 6px 6px 0; '
            f'font-size:0.83rem; color:#E8F0FE;">{item}</div>'
            for item in data["eat_freely"]
        )
        st.markdown(items_html, unsafe_allow_html=True)

    with col_avoid:
        st.markdown('<div class="section-header">❌ Foods to Limit/Avoid</div>', unsafe_allow_html=True)
        items_html = "".join(
            f'<div style="padding:6px 10px; margin:3px 0; background:rgba(255,59,92,0.07); '
            f'border-left:3px solid #FF3B5C; border-radius:0 6px 6px 0; '
            f'font-size:0.83rem; color:#E8F0FE;">{item}</div>'
            for item in data["avoid"]
        )
        st.markdown(items_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Sample Meal Plan
    st.markdown('<div class="section-header">🍽️ Sample Daily Meal Plan</div>', unsafe_allow_html=True)
    for time_label, meal in data["meal_plan"]:
        st.markdown(f"""
        <div style="display:flex; gap:14px; align-items:flex-start; padding:10px 14px;
                    background:rgba(10,22,40,0.6); border:1px solid rgba(0,212,255,0.1);
                    border-radius:10px; margin-bottom:6px;">
          <div style="min-width:120px; font-size:0.8rem; font-weight:700; color:#00D4FF;
                      padding-top:1px;">{time_label}</div>
          <div style="font-size:0.84rem; color:#E8F0FE; line-height:1.5;">{meal}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Key Tips
    st.markdown('<div class="section-header">💡 Key Health Tips</div>', unsafe_allow_html=True)
    tips_html = "".join(
        f'<div style="padding:8px 14px; margin:4px 0; background:rgba(0,212,255,0.06); '
        f'border:1px solid rgba(0,212,255,0.15); border-radius:8px; '
        f'font-size:0.84rem; color:#E8F0FE;">{tip}</div>'
        for tip in data["tips"]
    )
    st.markdown(tips_html, unsafe_allow_html=True)

    # Download diet plan
    st.markdown("<br>", unsafe_allow_html=True)
    col_dl, _ = st.columns([2, 3])
    with col_dl:
        diet_text = f"""CKD DIET PLAN — {patient_name}
Risk Level: {risk_level}
Generated by CKD Early Diagnosis System
{'='*50}

{data['label']}
{data['description']}

DAILY LIMITS:
{chr(10).join(f'  • {k}: {v}' for k, v in data['daily_limits'].items())}

FOODS TO INCLUDE:
{chr(10).join(f'  {item}' for item in data['eat_freely'])}

FOODS TO AVOID:
{chr(10).join(f'  {item}' for item in data['avoid'])}

SAMPLE MEAL PLAN:
{chr(10).join(f'  {t}: {m}' for t, m in data['meal_plan'])}

KEY TIPS:
{chr(10).join(f'  {tip}' for tip in data['tips'])}

⚠️ This diet plan is for general guidance only.
   Please consult your nephrologist or dietitian for personalized advice.
"""
        st.download_button(
            "⬇️ Download Diet Plan (TXT)",
            diet_text.encode("utf-8"),
            f"ckd_diet_plan_{risk_level.lower()}.txt",
            "text/plain",
            use_container_width=True
        )

    # AI Chat button
    if st.button("🤖 Ask AI Assistant About This Diet", use_container_width=False, key="diet_to_chat"):
        st.session_state.current_page = "AI Assistant"
        # Pre-load a question about the diet
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []
        st.session_state.chat_messages.append({
            "role": "user",
            "content": f"I have {risk_level} risk CKD. Can you give me more details about my diet plan and some recipe ideas?"
        })
        st.rerun()

    st.markdown("""
    <div class="disclaimer" style="margin-top:14px;">
      🔬 Diet guidelines based on NKF KDOQI & Indian CKD dietary recommendations.
      Always consult a registered renal dietitian for personalized meal planning.
    </div>
    """, unsafe_allow_html=True)
