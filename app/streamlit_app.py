import uuid
import requests
import streamlit as st

API_BASE = "http://127.0.0.1:8001" 

st.set_page_config(
    page_title="Library Desk Agent",
    page_icon="📚",
    layout="wide",
)


def init_state():
    if "sessions" not in st.session_state:
        first_id = str(uuid.uuid4())
        st.session_state.sessions = [
            {"id": first_id, "name": "Session 1"},
        ]
        st.session_state.current_session_id = first_id
        st.session_state.chat_history = {first_id: []}

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {
            st.session_state.current_session_id: []
        }


init_state()

with st.sidebar:
    st.header("💬 Sessions")

    name_to_id = {
        s["name"]: s["id"] for s in st.session_state.sessions
    }
    session_names = list(name_to_id.keys())

    current_id = st.session_state.current_session_id
    try:
        current_index = next(
            i for i, s in enumerate(st.session_state.sessions) if s["id"] == current_id
        )
    except StopIteration:
        current_index = 0

    selected_name = st.selectbox(
        "Choose Session",
        session_names,
        index=current_index,
    )
    st.session_state.current_session_id = name_to_id[selected_name]

    if st.button("➕ New Session"):
        new_id = str(uuid.uuid4())
        new_name = f"Session {len(st.session_state.sessions) + 1}"
        st.session_state.sessions.append({"id": new_id, "name": new_name})
        st.session_state.current_session_id = new_id
        st.session_state.chat_history[new_id] = []
        st.rerun()

    st.markdown("---")
    st.caption("Each session has its own conversation independent from the others.")


st.title("📚 Library Desk Agent")

current_id = st.session_state.current_session_id
history = st.session_state.chat_history.get(current_id, [])

for msg in history:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask about books, orders, inventory...")

if user_input:
    history.append({"role": "user", "content": user_input})
    st.session_state.chat_history[current_id] = history

    try:
        payload = {
            "message": user_input,
            "session_id": current_id,  
        }
        resp = requests.post(f"{API_BASE}/chat", json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        reply = data.get("reply", "(No reply)")
    except Exception as e:
        reply = f"An error occurred while communicating with the server: {e}"

    history.append({"role": "assistant", "content": reply})
    st.session_state.chat_history[current_id] = history

    st.rerun()


