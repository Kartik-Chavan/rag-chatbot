from pathlib import Path
import os

# =========================
# PROJECT ROOT
# =========================
# rag-chatbot/
ROOT_DIR = Path(__file__).resolve().parents[1]

# =========================
# ENVIRONMENT
# =========================
ENV = os.getenv("ENV", "development")

# =========================
# DATA PATHS
# =========================
DATA_DIR = ROOT_DIR / "data"
POLICY_DOCS_DIR = DATA_DIR / "policy_documents"

# =========================
# VECTOR STORE
# =========================
VECTORSTORE_DIR = ROOT_DIR / "vectorstore"
VECTOR_DB_PATH = VECTORSTORE_DIR / "faiss_index"

# =========================
# DATABASES
# =========================
DB_DIR = ROOT_DIR / "db"
DB_DIR.mkdir(exist_ok=True)

CHAT_DB_PATH = DB_DIR / "chat_history.sqlite"

# =========================
# MODELS
# =========================
LLM_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

# =========================
# RAG CONFIG
# =========================
TOP_K = 3
MAX_TOKENS = 1024
TEMPERATURE = 0.2

# =========================
# STREAMLIT
# =========================
APP_TITLE = "📘 Policy RAG Chatbot"
