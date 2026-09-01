from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
import sqlite3

load_dotenv()

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


llm = ChatOpenAI()


def chat_node(state: ChatState):
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


graph = StateGraph(ChatState)

#create databse in sqlite first
conn = sqlite3.connect(databse='chatbot.db',check_same_thread=False)
checkpoint = SqliteSaver(conn=conn)

graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

workflow = graph.compile(checkpointer=checkpoint)

def count_threads():
    all_threads = set()
    for c in checkpoint.list(None):
        all_threads.add(c.config['configurable']['thread_id'])
    
    return all_threads

