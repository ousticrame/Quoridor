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
    st.session_state.messages = [{"role": "assistant", "content": "Hey, I'm an AI assistant specialized in mapping students to groups. Let's start chatting! 👇"}]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=USER_ICON if message["role"] == "user" else ASSISTANT_ICON):
        if "content" in message:
            st.markdown(message["content"])
        if "image" in message:
            st.image(message["image"])

# Accept user input
if prompt := st.chat_input("Type here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt, "avatar": USER_ICON})
    # Display user message in chat message container
    with st.chat_message("user", avatar=USER_ICON):
        st.markdown(prompt)

    # Display assistant response in chat message container

    # Spinner to indicate processing
    with st.spinner("Cooking in progress...💫", show_time=True):
        assistant_response = call_agent(prompt)

    # Process the assistant response if it contains an image
    if assistant_response["image"]:
        with st.chat_message("assistant", avatar=ASSISTANT_ICON):
            image = assistant_response["image"]
            print("found image")
            st.image(image)
            st.session_state.messages.append({"role": "assistant", "image": assistant_response["image"]})

    # Process the assistant response
    with st.chat_message("assistant", avatar=ASSISTANT_ICON):
        assistant_response = assistant_response["final_output"]
        st.markdown(assistant_response)    
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
