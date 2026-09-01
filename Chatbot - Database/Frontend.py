import streamlit as st
from Backend import workflow,count_threads
from langchain_core.messages import BaseMessage, HumanMessage
import uuid #for genarting dynamic thread_ids


#*******************UTILITY FUNCTION********************************
def generate_thread_id():
     thread_id = uuid.uuid4()
     return thread_id

def reset_chat():
     thread_id = generate_thread_id()
     st.session_state['thread_id']=thread_id
     add_thread(thread_id)
     st.session_state['message_history'] = []

def add_thread(thread_id):
     if thread_id not in st.session_state['chat_thread_id']:
          st.session_state['chat_thread_id'].append(thread_id)

def load_conversation(thread_id):
     return workflow.get_state(config={"configurable": {"thread_id": thread_id}})["messages"]


## st.session_state ->dict 
##content doesnt refresh on enter, only when the site is refreshed
if 'message_history' not in st.session_state:
     st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
     st.session_state['thread_id'] = generate_thread_id()

if 'chat_thread_id' not in st.session_state:
     st.session_state['chat_thread_id'] = count_threads()

add_thread(st.session_state['thread_id'])
     

#*********************SIDE BAR****************************************
st.sidebar.title('LangGarph Chatbot')

if(st.sidebar.button('New Chat')):
     reset_chat()

st.sidebar.header('My Coversations')
for c in st.session_state['chat_thread_id'][::-1]:
     if st.sidebar.button(str(c)):
          st.session_state['thread_id'] = c
          messages = load_conversation(c)

          temp_messages=[]
          for m in messages:
               if isinstance(m, HumanMessage):
                    temp_messages.append({'role':'user','content':m.content})
               else:
                    temp_messages.append({'role':'assistant','content':m.content})

          st.session_state['message_history'] = temp_messages



#******************************MAIN UI*************************************

for x in st.session_state['message_history']:
        with st.chat_message(x['role']):
            st.text(x['content'])

user_input = st.chat_input('Type here')

if(user_input):
    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
       st.text(user_input)

    thread_id = st.session_state['thread_id']
    config = {"configurable": {"thread_id": thread_id}}
    ##Ai_response = workflow.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
    ##response = Ai_response["messages"][-1].content
    
    with st.chat_message('assistant'):
           ai_message= st.write_stream(
                message_chunk.content for message_chunk,metadata in workflow.stream(
                     {'message':[HumanMessage(content=user_input)]},
                     config = config,
                     stream_mode = 'messages'
                     
                )
           )

    st.session_state['message_history'].append({'role':'assistant','content':ai_message})


