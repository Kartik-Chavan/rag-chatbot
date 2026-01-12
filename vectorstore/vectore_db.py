import re
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config.settings import VECTOR_DB_PATH
from llm.chunking_agent import get_chunking_config


VECTORSTORE_PATH = Path(VECTOR_DB_PATH)


def clean_text(text: str) -> str:
    # 1. Fix words broken across lines with hyphen
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

    # 2. Remove dot leaders used in table of contents
    text = re.sub(r'\.{2,}', '', text)

    # 3. Remove standalone page numbers (lines with only digits)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)

    # 4. Remove isolated section numbers (e.g., 1.5, 2.1, 3.2)
    text = re.sub(r'^\s*\d+(\.\d+)+\s*$', '', text, flags=re.MULTILINE)

    # 5. Reduce excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()



def get_db(embeddings):
    return Chroma(
        collection_name="policy_documents",
        embedding_function=embeddings,
        persist_directory=str(VECTORSTORE_PATH)
    )


def ingest_policy_pdf(
    llm,
    embeddings,
    pdf_path: Path,
    source_name: str,
    file_id: str
):
    vectorstore = get_db(embeddings)

    # 🔥 Remove old document chunks
    vectorstore.delete(where={"file_id": file_id}) # For single policy file 
    #vectorstore.delete(where={"source": source_name}) # For Multiple policy files 
    vectorstore.persist()

    # 1️⃣ Load document
    loader = PyMuPDFLoader(str(pdf_path))
    docs = loader.load()

    full_text = ""
    for doc in docs:
        doc.page_content = clean_text(doc.page_content)
        full_text += doc.page_content + "\n"

    # 2️⃣ Agent decides chunking strategy
    chunk_config = get_chunking_config(llm, full_text)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_config["chunk_size"],
        chunk_overlap=chunk_config["chunk_overlap"],
        separators=chunk_config["separators"]
    )

    split_docs = splitter.split_documents(docs)

    # 3️⃣ Add metadata
    enriched_docs = [
        Document(
            page_content=doc.page_content,
            metadata={
                "source": source_name,
                "file_id": file_id
            }
        )
        for doc in split_docs
    ]

    # 4️⃣ Store in Chroma
    vectorstore.add_documents(enriched_docs)
    vectorstore.persist()

    return vectorstore
