import os
from dotenv import load_dotenv
from langchain_cohere import CohereEmbeddings
from vectorstore.vectore_db import get_db
# Load environment variables
load_dotenv()



# Read API key securely
cohere_api_key = os.getenv("COHERE_API_KEY")

if not cohere_api_key:
    raise ValueError("COHERE_API_KEY not found in environment variables")
#Embedding Model Initialization
embeddings = CohereEmbeddings(
    model="embed-english-v3.0",  # Full model (not light) for HR policies
    cohere_api_key=cohere_api_key
)

db = get_db(embeddings=embeddings)

def get_context(query:str):
    res = db.similarity_search(query=query,k=3)
    context=""
    for chunk in res: 
        context+=chunk.page_content+" , "
    return context

