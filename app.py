import streamlit as st
import uuid
import time
from pathlib import Path
from config.settings import POLICY_DOCS_DIR
from vectorstore.vectore_db import ingest_policy_pdf
from llm.rag_chat_bot import llm
from vectorstore.retriever import embeddings

from llm.rag_chat_bot import ask_ai, app  # app = compiled LangGraph
from utils.session_db import (
    init_session_db,
    create_session,
    get_sessions, 
    delete_session, 
    rename_session

)
POLICY_DOCS_DIR.mkdir(parents=True, exist_ok=True)

if "show_policy_success" not in st.session_state:
    st.session_state.show_policy_success = False


if "show_policy_success" not in st.session_state:
    st.session_state.show_policy_success = False

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


# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("📄 Available Policy Documents")

    policy_files = list(POLICY_DOCS_DIR.glob("*.pdf"))

    if policy_files:
        for pdf in policy_files:
            st.markdown(f"📄 {pdf.name}")
    else:
        st.info("No policy documents uploaded yet.")
    st.divider()

with st.sidebar:
    st.header("📄 Policy Management")

    uploaded_file = st.file_uploader(
        "Upload / Update Policy Document",
        type=["pdf"],
        accept_multiple_files=False,
        key="policy_uploader"
    )

    # Reset guard when uploader is cleared
    if uploaded_file is None:
        st.session_state.policy_processed = False

    if uploaded_file and not st.session_state.policy_processed:
        policy_path = POLICY_DOCS_DIR / uploaded_file.name
        
        # 🔹 NEW: Check if file already exists
        if policy_path.exists():
            st.info("Updating the existing policy document… ♻️")
        else:
            st.info("Uploading new policy document… 📄")

        with open(policy_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("Processing policy document..."):
            ingest_policy_pdf(
                llm=llm,
                embeddings=embeddings,
                pdf_path=policy_path,
                source_name=uploaded_file.name,
                file_id="active_policy"
            )

        st.session_state.policy_processed = True
        st.session_state.show_policy_success = True


        st.success("Policy document uploaded and indexed successfully ✅")
        time.sleep(2)

        # Clear uploader + prevent reprocessing
        st.rerun()


    st.divider()



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
