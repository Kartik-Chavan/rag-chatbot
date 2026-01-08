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
# Load environment variables
load_dotenv()



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
    config= {"configurable":{"thread_id":thread_id}}
    

    res= app.invoke({"messages":HumanMessage(content=user_input)},config=config)
    return res['messages'][-1].content