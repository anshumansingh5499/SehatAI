import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Medical Triage Assistant",
    layout="centered"
)

st.title("⚕️ Medical Symptom Triage")
st.caption("Describe your symptoms and get general guidance. Not a substitute for a doctor.")

st.warning(
    "For emergencies call **108** (Ambulance) immediately. "
    "This tool provides general information only.",
    icon="⚠️"
)

# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            "Hello! I'm your medical triage assistant.\n\n"
            "Please describe your symptoms. It helps to mention:\n"
            "- What symptoms you have\n"
            "- How long you've had them\n"
            "- How severe they are (1-10)\n"
            "- Your age"
        )
    }]
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0
if "emergencies_caught" not in st.session_state:
    st.session_state.emergencies_caught = 0

# ── Chat history ───────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ─────────────────────────────────────────────────────────────────
prefill = st.session_state.pop("prefill", "")
prompt = st.chat_input("Describe your symptoms here...") or prefill

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analysing your symptoms..."):
            try:
                resp = requests.post(
                    f"{API_URL}/triage",
                    json={"message": prompt},
                    timeout=120
                )
                data = resp.json()
                answer = (
                    data.get("response") or
                    data.get("answer") or
                    data.get("detail") or
                    str(data)
                )
                is_emergency = data.get("is_emergency", False)
                sources = data.get("sources", [])

                if is_emergency:
                    st.session_state.emergencies_caught += 1
                    st.error(answer)
                else:
                    st.session_state.total_queries += 1
                    st.markdown(answer)
                    if sources:
                        with st.expander("Knowledge sources used"):
                            for s in sources:
                                st.text(f"• {s}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to the backend. Make sure uvicorn is running on port 8000.")
            except Exception as e:
                st.error(f"Error: {e}")

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:

    # ✅ ADDED: Logo from local assets
    st.image("assets/logo1.png", width=120)



    st.divider()

    # ── Emergency numbers ──
    st.markdown("### Emergency Numbers")
    st.error("Ambulance: 108")
    st.warning("Health Helpline: 104")
    st.success("Police: 100")
    st.info("Poison Control: 1800-116-117")

    st.divider()

    # ── Enhanced Session Stats ──
    st.markdown("### Session Analytics")

    st.markdown("""
    <style>
    .stat-box {
        padding: 12px;
        border-radius: 12px;
        background: #f5f7fa;
        text-align: center;
        margin-bottom: 10px;
        border: 1px solid #e0e0e0;
    }
    .stat-number {
        font-size: 22px;
        font-weight: bold;
    }
    .stat-label {
        font-size: 12px;
        color: gray;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{st.session_state.total_queries}</div>
            <div class="stat-label">Total Queries</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{st.session_state.emergencies_caught}</div>
            <div class="stat-label">Emergency Alerts</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Most searched ──
    st.markdown("### Most Searched")
    most_searched = [
        "🌡️  Fever and headache for 2 days",
        "🤧  Cold, cough and sore throat",
        "🤢  Nausea, vomiting and loose motions",
        "🦟  Dengue — fever, rash and body pain",
        "💊  Typhoid — prolonged fever and fatigue",
        "❤️  Chest pain and breathing difficulty",
    ]
    for item in most_searched:
        if st.button(item, key=f"ms_{item}", use_container_width=True):
            st.session_state["prefill"] = item[3:].strip()
            st.rerun()

    st.divider()

    # ── Common conditions ──
    st.markdown("### Common Conditions")
    common_conditions = [
        "🧠  Severe migraine headache",
        "💧  Urinary tract infection symptoms",
        "🩸  High blood pressure and dizziness",
        "🍬  Diabetes — thirst and fatigue",
        "🦴  Back pain and muscle stiffness",
        "🌿  Skin rash and itching all over",
        "😰  Anxiety and panic attack symptoms",
        "🌀  Stomach infection and diarrhea",
    ]
    for item in common_conditions:
        if st.button(item, key=f"cc_{item}", use_container_width=True):
            st.session_state["prefill"] = item[3:].strip()
            st.rerun()

    st.divider()

    # ── About ──
    st.markdown("### About")
    st.info(
        "This AI assistant helps you understand symptoms and "
        "decide how urgently you need medical care. "
        "Always consult a real doctor for diagnosis."
    )

    # ── Disclaimer ──
    st.caption(
        "This tool is for general information only. "
        "It does NOT replace professional medical advice. "
        "For emergencies call 108 immediately."
    )

    # ── Clear button ──
    if st.button("Clear Conversation", use_container_width=True, type="primary"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": (
                "Hello! I'm your medical triage assistant.\n\n"
                "Please describe your symptoms. It helps to mention:\n"
                "- What symptoms you have\n"
                "- How long you've had them\n"
                "- How severe they are (1-10)\n"
                "- Your age"
            )
        }]
        st.session_state.total_queries = 0
        st.session_state.emergencies_caught = 0
        st.rerun()