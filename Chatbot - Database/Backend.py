from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
import sqlite3
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
import requests
import random
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

llm = ChatOpenAI()

#Tools
#Search_tool = DuckDuckGoSearchRun(region='us-en')


##we will make only mcp client, for mcp server we need to make another file with fastmcp
##connect the mcp client tool with the server

client = MultiServerMCPClient(
    {
        "arith":{
            "transport":"stdio",
            "command":"python",
            "args":['main.py']
        }
    }
)
#here main.py is the mcp server made using fastmcp

# @tool
# def calculator(first_num:float, second_num:float,operation:str)->dict:
#     """
#     A simple calculator tool to perform basic arithmetic operations.
#     supported operations: add, subtract, multiply, divide.
#     """
#     try:
#         if operation=='add':
#             result = first_num + second_num
#         elif operation=='subtract':
#             result = first_num-second_num
#         elif operation =='mul':
#             result = first_num*second_num
#         elif operation == 'div':
#             if second_num==0:
#                 return {'error':'division by zero is not allowed'}
#             result = first_num/second_num
#         else:
#             return {'error':'invalid operation'}

#         return {'first_num': first_num, 'second_num': second_num,'operation': operation, 'result': result}
#     except Exception as e:
#         return {'error': str(e)}


# @tool
# def get_stock_price(symbol:str) ->dict:
#     """
#     A tool to fetch the current stock price for a given stock symbol."""
#     url = "8R04E68ARVCM4C06."
#     r = requests.get(url)
#     return r.json()

# #make tool list 
# tools = [get_stock_price, calculator, Search_tool]




class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]



async def build_graph():

    tools = await client.get_tools()
    #make the llm tool aware
    llm_with_tools = llm.bind_tools(tools)

    async def chat_node(state: ChatState):
        """
        A node that takes in a list of messages and returns a response from the LLM."""
        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)
    
    
    graph = StateGraph(ChatState)
    
    #create databse in sqlite first
    conn = sqlite3.connect(databse='chatbot.db',check_same_thread=False)
    checkpoint = SqliteSaver(conn=conn)
    
    graph.add_node("chat_node", chat_node)
    graph.add_node('tools',tool_node)
    
    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges('chat_node', tools_condition)
    graph.add_edge('tools', "chat_node")
    graph.add_edge("chat_node", END)
    
    workflow = graph.compile(checkpointer=checkpoint)


def count_threads():
    all_threads = set()
    for c in checkpoint.list(None):
        all_threads.add(c.config['configurable']['thread_id'])
    
    return all_threads

