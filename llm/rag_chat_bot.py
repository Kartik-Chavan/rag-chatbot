import os
import sqlite3
from dotenv import load_dotenv
from langchain_cohere import ChatCohere
from config.prompt import RAG_AGENT_PERSONA
from config.settings import DB_DIR
from langgraph.checkpoint.sqlite import SqliteSaver
from vectorstore.retriever import get_context
from typing import TypedDict,Annotated,Sequence
from langchain_core.messages import BaseMessage , AIMessage,HumanMessage
from langgraph.graph import add_messages
from langgraph.graph import StateGraph
import time
from db_logger.mongo_logger import MongoLogger

# Load environment variables
load_dotenv()

# Initialize MongoDB Logger
logger = MongoLogger()



# Read API key securely
cohere_api_key = os.getenv("COHERE_API_KEY")

if not cohere_api_key:
    raise ValueError("COHERE_API_KEY not found in environment variables")

# Initialize LLM
llm = ChatCohere(cohere_api_key=cohere_api_key)

# DB Path creation 
DB_PATH = DB_DIR / "chat_history.db"
#SQLite Db connection
conn= sqlite3.connect(DB_PATH,check_same_thread=False)
memory = SqliteSaver(conn)

#State Creation 
class state(TypedDict):
    messages:Annotated[Sequence[BaseMessage],add_messages]


# Node Creation 
def llm_node(state:state):
    query= state['messages'][-1].content
    
    context=get_context(query)
    
    prompt = RAG_AGENT_PERSONA.format(
    context=context,
    messages=state['messages']
    )

    res = llm.invoke(prompt)
    

    return {"messages":res}

#Graph Creation 
graph =StateGraph(state) 

graph.add_node("llm_node",llm_node)

graph.set_entry_point("llm_node")
graph.set_finish_point("llm_node")
app=graph.compile(checkpointer=memory)




def ask_ai(user_input:str,thread_id:str):
    start_time = time.time()
    config= {"configurable":{"thread_id":thread_id}}
    
    try:
        res= app.invoke({"messages":HumanMessage(content=user_input)},config=config)
        response_text = res["messages"][-1].content
        latency_ms = int((time.time() - start_time) * 1000)
        # ✅ Chat success log
        
        logger.log_chat({
                "thread_id": thread_id,
                "user_message": user_input,
                "assistant_response": response_text,
                "context_length": len(get_context(user_input)),
                "latency_ms": latency_ms,
                "status": "success"
            })
  

        return response_text
    
    except Exception as e:
        print("Error in ask_ai:", e)
        latency_ms = int((time.time() - start_time) * 1000)

        # ❌ Error log
        logger.log_error({
            "location": "ask_ai",
            "thread_id": thread_id,
            "user_message": user_input,
            "error_message": str(e),
            "latency_ms": latency_ms,
            "severity": "ERROR"
        })

        raise