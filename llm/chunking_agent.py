import json
from langchain_core.messages import HumanMessage, SystemMessage
from config.prompt import DOCUMENT_CHUNKING_AGENT_PROMPT


def get_chunking_config(llm, document_text: str) -> dict:
    """
    Ask the LLM to generate a chunking configuration for a document.
    """

    messages = [
        SystemMessage(content=DOCUMENT_CHUNKING_AGENT_PROMPT),
        HumanMessage(content=document_text[:6000])  # limit tokens
    ]

    response = llm.invoke(messages)

    try:
        config = json.loads(response.content)

        # ✅ Basic validation
        assert "chunk_size" in config
        assert "chunk_overlap" in config
        assert "separators" in config

        return config

    except Exception:
        # 🔥 Safe fallback (never break ingestion)
        print("Defaulting chunking config due to error in LLM response parsing.")
        return {
            "chunk_size": 250,
            "chunk_overlap": 30,
            "separators": ["\n\n", "\n"]
        }
