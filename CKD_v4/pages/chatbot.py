"""
pages/chatbot.py  ──  CKD AI Health Assistant Chatbot
Powered by Claude AI via Anthropic API
"""
import streamlit as st
import streamlit.components.v1 as components
from utils.styles import inject_css, page_header


def render():
    inject_css()
    if st.session_state.get("user_role") == "guest":
        st.markdown('<div class="danger-box">🚫 Please create an account to use the AI Assistant.</div>',
                    unsafe_allow_html=True)
        return

    page_header("🤖", "CKD AI Health Assistant", "Ask any question about kidney health, symptoms, diet, or your results")

    # Get patient context if available
    user_info = st.session_state.get("user_info", {})
    patient_name = user_info.get("patient_name", "Patient")
    last_result = st.session_state.get("last_prediction", {})
    risk_level = last_result.get("risk_level", "Unknown") if last_result else "Unknown"

    # System prompt context
    patient_context = f"""You are a compassionate and knowledgeable CKD (Chronic Kidney Disease) health assistant.
Patient name: {patient_name}
Last screening risk level: {risk_level}

Your role:
- Answer questions about CKD symptoms, stages, treatment, and prevention
- Provide diet and lifestyle guidance for kidney health
- Explain lab values and what they mean
- Offer emotional support and encouragement
- Always recommend consulting a nephrologist for medical decisions
- Be warm, empathetic, and use simple language

IMPORTANT: You are not a substitute for professional medical advice. Always remind patients to consult their doctor for diagnosis and treatment decisions.

Keep responses concise (3-5 sentences max unless more detail is specifically needed). Use bullet points for lists."""

    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Quick question buttons
    st.markdown('<div class="section-header">💡 Quick Questions</div>', unsafe_allow_html=True)
    quick_cols = st.columns(3)
    quick_questions = [
        ("🥗 Diet Tips", "What foods should I eat and avoid for kidney health?"),
        ("💊 CKD Stages", "Can you explain the 5 stages of CKD?"),
        ("🏃 Exercise", "What exercises are safe for CKD patients?"),
        ("💧 Hydration", "How much water should I drink with CKD?"),
        ("🧪 Lab Values", "What do creatinine and GFR numbers mean?"),
        ("😴 Symptoms", "What are warning signs that my kidneys are getting worse?"),
    ]
    for i, (label, question) in enumerate(quick_questions):
        col = quick_cols[i % 3]
        if col.button(label, key=f"quick_{i}", use_container_width=True):
            st.session_state.chat_messages.append({"role": "user", "content": question})
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat container with custom styling
    st.markdown("""
    <style>
    .chat-container {
        max-height: 450px;
        overflow-y: auto;
        padding: 12px;
        background: rgba(10,22,40,0.6);
        border: 1px solid rgba(0,212,255,0.15);
        border-radius: 12px;
        margin-bottom: 12px;
    }
    .chat-bubble-user {
        background: rgba(0,212,255,0.12);
        border: 1px solid rgba(0,212,255,0.25);
        border-radius: 12px 12px 2px 12px;
        padding: 10px 14px;
        margin: 8px 0 8px 20%;
        color: #E8F0FE;
        font-size: 0.87rem;
        line-height: 1.6;
    }
    .chat-bubble-bot {
        background: rgba(19,34,56,0.95);
        border: 1px solid rgba(0,229,160,0.2);
        border-radius: 12px 12px 12px 2px;
        padding: 10px 14px;
        margin: 8px 20% 8px 0;
        color: #E8F0FE;
        font-size: 0.87rem;
        line-height: 1.6;
    }
    .chat-label-user { text-align:right; font-size:0.7rem; color:#7A9CC0; margin-bottom:2px; }
    .chat-label-bot  { text-align:left;  font-size:0.7rem; color:#00E5A0; margin-bottom:2px; }
    </style>
    """, unsafe_allow_html=True)

    # Display chat history
    if st.session_state.chat_messages:
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                chat_html += f'<div class="chat-label-user">You</div>'
                chat_html += f'<div class="chat-bubble-user">{msg["content"]}</div>'
            else:
                content = msg["content"].replace("\n", "<br>").replace("•", "•")
                chat_html += f'<div class="chat-label-bot">🤖 CKD Assistant</div>'
                chat_html += f'<div class="chat-bubble-bot">{content}</div>'
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:30px; background:rgba(10,22,40,0.4);
                    border:1px solid rgba(0,212,255,0.12); border-radius:12px; margin-bottom:12px;">
            <div style="font-size:2rem;">🤖</div>
            <div style="color:#7A9CC0; font-size:0.9rem; margin-top:8px;">
                Hi! I'm your CKD Health Assistant.<br>Ask me anything about kidney disease, diet, or your health.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Input area
    col_input, col_send, col_clear = st.columns([6, 1, 1])
    with col_input:
        user_input = st.text_input("", placeholder="Ask about symptoms, diet, treatment, lab values...",
                                   key="chat_input", label_visibility="collapsed")
    with col_send:
        send_clicked = st.button("Send →", key="chat_send", use_container_width=True)
    with col_clear:
        if st.button("🗑️", key="chat_clear", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

    # Process message
    pending = None
    if send_clicked and user_input.strip():
        pending = user_input.strip()
    elif st.session_state.chat_messages and st.session_state.chat_messages[-1]["role"] == "user":
        # Quick question was added, need AI response
        if len(st.session_state.chat_messages) % 2 == 1:
            pending = None  # Will be handled below

    if send_clicked and user_input.strip():
        st.session_state.chat_messages.append({"role": "user", "content": user_input.strip()})
        st.rerun()

    # Auto-respond when last message is from user
    if (st.session_state.chat_messages and
            st.session_state.chat_messages[-1]["role"] == "user" and
            not (send_clicked and user_input.strip())):
        with st.spinner("🤖 Thinking..."):
            try:
                import json, urllib.request
                messages_payload = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.chat_messages
                ]
                payload = json.dumps({
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1000,
                    "system": patient_context,
                    "messages": messages_payload
                }).encode("utf-8")
                req = urllib.request.Request(
                    "https://api.anthropic.com/v1/messages",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read())
                reply = data["content"][0]["text"]
                st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                st.rerun()
            except Exception as e:
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": f"⚠️ I'm having trouble connecting right now. Please try again in a moment. (Error: {str(e)[:60]})"
                })
                st.rerun()

    st.markdown("""
    <div class="disclaimer" style="margin-top:10px;">
      🔒 This AI assistant provides general health information only.
      Always consult your nephrologist or healthcare provider for medical decisions.
    </div>
    """, unsafe_allow_html=True)
