from pydantic_core.core_schema import ArgumentsSchema
import streamlit as st
import random
import time

from ai import call_agent


ASSISTANT_ICON = "csp_image.jpg"
USER_ICON = "user_image.jpg"
# Add a title to the app
st.title("CSP LLM")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting! 👇"}]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=USER_ICON if message["role"] == "user" else ASSISTANT_ICON):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Type here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt, "avatar": USER_ICON})
    # Display user message in chat message container
    with st.chat_message("user", avatar=USER_ICON):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant", avatar=ASSISTANT_ICON):
        message_placeholder = st.empty()
        full_response = ""
        message_placeholder.markdown("Thinking... 🔄")
        assistant_response = call_agent(prompt)
        message_placeholder.markdown(assistant_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})