import os
import re 
from pathlib import Path
from config.settings import POLICY_DOCS_DIR , VECTOR_DB_PATH
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyMuPDFLoader 
from langchain_text_splitters import RecursiveCharacterTextSplitter

VECTORSTORE_PATH = Path(VECTOR_DB_PATH)

def get_db(embeddings):

    if not VECTORSTORE_PATH.exists():
        print("Creating vectorstore...")

        # 1. Load document
        file_path = POLICY_DOCS_DIR / "Policy_Document.pdf"
        loader = PyMuPDFLoader(str(file_path))  # Preserves headers/structure
        docs = loader.load()
        for doc in docs:
            # Fix broken words and spacing artifacts
            doc.page_content = re.sub(r'(\w+)-\n(\w+)', r'\1\2', doc.page_content)  # Reconnect hyphenated words
            doc.page_content = re.sub(r'\n{3,}', '\n\n', doc.page_content)  # Reduce excess newlines
        # 2. Split documents
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=250,          # Smaller size to isolate sections
            chunk_overlap=30,
            separators=[
                "\n\n1.", "\n\n2.", "\n\n3.", "\n\n4.", "\n\n5.", "\n\n6.",  # Section breaks
                "\n\n", 
                "\n"
            ]
        )
        split_docs = splitter.split_documents(docs)

        # 3. Create & save DB
        db = FAISS.from_documents(split_docs, embeddings)
        db.save_local(VECTORSTORE_PATH)

        # ✅ IMPORTANT: return immediately
        return db

    # 4. Load existing DB
    print("Loading existing vectorstore...")
    return FAISS.load_local(
        VECTORSTORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
