


# 🤖 RAG Chatbot with Streamlit, LangGraph & SQLite

A **ChatGPT-like RAG (Retrieval-Augmented Generation) chatbot** built using **Streamlit**, **LangGraph**, **FAISS**, and **SQLite**, supporting:

- 📚 Policy document–based question answering
- 💬 Multiple persistent chat sessions
- 🧠 Stateful conversations using LangGraph
- 🗂️ Session management (New / Select / Rename / Delete chats)
- 💾 Persistent storage using SQLite
- 🔐 Secure API key handling via `.env`

---

## 📌 Key Features

- **RAG-based Answers**  
  Answers are generated strictly from provided policy documents.

- **ChatGPT-like UI**  
  Sidebar with multiple chat sessions, each having its own history.

- **Persistent Chat Memory**  
  Chat history is preserved even after restarting the application.

- **Session Management**  
  - Create new chat sessions  
  - Rename existing chats  
  - Delete chat sessions  

- **Clean Architecture**  
  Clear separation of UI, vector store, session storage, and RAG logic.

---

## 📂 Project Directory Structure

````text
├── app.py                     # Streamlit entry point
├── requirements.txt
├── README.md
│
├── config/
│   ├── prompt.py              # RAG agent persona / system prompt
│   └── settings.py            # Project root paths & configs
│
├── data/
│   └── policy_documents/      # Documents used for RAG
│       ├── document_1.txt
│       └── Policy_Document.pdf
│
├── db/
│   ├── chat_history.db        # LangGraph persistent state
│   └── session.db             # Chat session metadata
│
├── llm/
│   └── rag_chat_bot.py        # LangGraph RAG implementation
│
├── utils/
│   └── session_db.py          # Session DB helpers (create, rename, delete)
│
├── vectorstore/
│   ├── faiss_index/           # FAISS vector database
│   │   ├── index.faiss
│   │   └── index.pkl
│   ├── vectore_db.py          # Vector DB creation/loading
│   └── retriever.py           # Context retrieval logic
│
└── ui/
└── **init**.py
````
---

## ⚙️ Tech Stack

| Component        | Technology |
|------------------|------------|
| UI               | Streamlit |
| LLM              | Cohere (via LangChain) |
| RAG Framework    | LangGraph |
| Vector Database  | FAISS |
| Session Storage  | SQLite |
| Environment Mgmt | python-dotenv |

---

## 🔐 Environment Variable Setup

### 1️⃣ Create a `.env` file in the project root

```env
COHERE_API_KEY=your_api_key_here
````

⚠️ **Do NOT commit `.env` to GitHub**
Ensure it is listed in `.gitignore`.

---

## 📦 Installation & Setup

### 1️⃣ Create and activate a virtual environment

```bash
python -m venv menv
menv\Scripts\activate       # Windows
# source menv/bin/activate  # macOS/Linux
```

---

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

Start the Streamlit app:

```bash
streamlit run app.py
```

Then open your browser at:

```
http://localhost:8501
```

---

## 🧠 How It Works (Architecture Overview)

### 🔁 Data Flow

```
User Query
   ↓
Streamlit UI
   ↓
ask_ai(user_input, thread_id)
   ↓
LangGraph
   ├── Load state from chat_history.db
   ├── Retrieve context from FAISS
   ├── Apply RAG prompt
   └── Generate response via Cohere
   ↓
State saved back to SQLite
   ↓
Response shown in UI
```

---

## 🗂️ Chat Session Management

* Each chat session has a **unique `thread_id` (UUID)**.
* Session metadata is stored in `session.db`.
* Conversation state is stored and restored by **LangGraph checkpoints**.

### Supported Actions

* ➕ New Chat
* ✏️ Rename Chat
* 🗑️ Delete Chat

---

## 📚 RAG Behavior Rules

* Answers are generated **only from policy documents**.
* If information is not found:

  ```
  "This information is not available in the provided policy documents."
  ```
* Greetings and small talk are handled without document retrieval.

---

## 🔒 Security & Best Practices

* API keys stored in `.env`
* SQLite databases ignored in Git
* Vector store excluded from version control
* No hardcoded secrets

---

## 🧪 Example Questions

* *What is ABC Corporation's parental leave policy?*
* *How many paid leave days are allowed?*
* *What is the security policy regarding data access?*

---

## 🚀 Future Enhancements (Optional)

* Streaming responses
* Source document citations
* Chat export (PDF / TXT)
* Search chats
* Cleanup orphaned LangGraph states
* Multi-document upload via UI

---

## 👨‍💻 Author Notes

This project is designed to be:

* ✅ Interview-ready
* ✅ Easy to extend
* ✅ Production-aligned (without over-engineering)

---

## 📄 License

This project is for **educational and demonstration purposes only**.



