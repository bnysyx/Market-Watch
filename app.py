import streamlit as st

from financial_advisor import initialize_agent, ai_agent

st.title('Market Watch - An AI Financial Analyst')

# Initialize empty list if session state is not existing
if "messages" not in st.session_state:
    st.session_state.messages = []

# Re-Draw all previous messages on the screen (on every rerun)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Default --> Wait for user input
if prompt := st.chat_input("Ask about a stock..."):

    # Display new user question
    with st.chat_message("user"):
        st.markdown(prompt)

    # Save new question to session state
    st.session_state.messages.append({'role':'user','content':prompt})

    # Initialize system prompt
    ai_memmory = initialize_agent()

    # Create langchain memmory state [List of (tuples)]
    for message in st.session_state.messages:
        ai_memmory.append((message['role'],message['content']))

    # Create ai response
    ai_response = ai_agent(ai_memmory)    
    ai_response_text = ai_response["messages"][-1].content

    # Display AI response
    with st.chat_message("assistant"):
        st.markdown(ai_response_text)

    # Save response to session state
    st.session_state.messages.append({"role": "assistant", "content": ai_response_text})