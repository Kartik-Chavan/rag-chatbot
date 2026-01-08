import streamlit as st
import uuid


from llm.rag_chat_bot import ask_ai, app  # app = compiled LangGraph
from utils.session_db import (
    init_session_db,
    create_session,
    get_sessions, 
    delete_session, 
    rename_session

)

st.markdown(
    """
    <style>
    button[kind="secondary"] {
        border-radius: 10px;
        text-align: left;
        padding-left: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="RAG Chatbot", layout="wide")
st.title("💬 RAG Chatbot")

# Init DB
init_session_db()

# Session state
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

# -------- Sidebar --------
with st.sidebar:
    st.header("Chats")

    if st.button("➕ New Chat", use_container_width=True):
        thread_id = str(uuid.uuid4())
        session_name = f"Chat {thread_id[:8]}"
        create_session(session_name, thread_id)
        st.session_state.thread_id = thread_id
        st.rerun()

    st.divider()

    sessions = get_sessions()

    for name, tid in sessions:
        container = st.container()

        with container:
            col1, col2 = st.columns([0.9, 0.1], gap="small")

            with col1:
                if st.button(
                    name,
                    key=f"select_{tid}",
                    use_container_width=True
                ):
                    st.session_state.thread_id = tid
                    st.rerun()

            with col2:
                with st.popover("⋮"):
                    new_name = st.text_input(
                        "Rename chat",
                        value=name,
                        key=f"rename_input_{tid}"
                    )

                    if st.button("✏️ Rename", key=f"rename_{tid}"):
                        rename_session(tid, new_name)
                        st.rerun()

                    if st.button("🗑️ Delete", key=f"delete_{tid}"):
                        delete_session(tid)

                        if st.session_state.thread_id == tid:
                            st.session_state.thread_id = None

                        st.rerun()


# No chat selected
if not st.session_state.thread_id:
    st.info("Start a new chat or select an existing one.")
    st.stop()

thread_id = st.session_state.thread_id

# -------- Load Chat History from LangGraph --------
config = {"configurable": {"thread_id": thread_id}}
state = app.get_state(config)

messages = state.values.get("messages", [])

for msg in messages:
    role = "assistant" if msg.type == "ai" else "user"
    with st.chat_message(role):
        st.markdown(msg.content)

# -------- Chat Input --------
if prompt := st.chat_input("Ask something..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    response = ask_ai(prompt, thread_id)

    with st.chat_message("assistant"):
        st.markdown(response)
