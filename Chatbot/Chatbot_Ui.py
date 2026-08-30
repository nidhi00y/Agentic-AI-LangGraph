import streamlit as st
from chatbot_backend import workflow
from langchain_core.messages import BaseMessage, HumanMessage


## st.session_state ->dict 
##content doesnt refresh on enter, only when the site is refreshed
if 'message_history' not in st.session_state:
     st.session_state['message_history'] = []

for x in st.session_state['message_history']:
        with st.chat_message(x['role']):
            st.text(x['content'])

user_input = st.chat_input('Type here')

if(user_input):
    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
       st.text(user_input)

    thread_id = '1'
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


