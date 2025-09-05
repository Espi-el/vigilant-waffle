import streamlit as st
from openai import OpenAI
import os
import json

# Streamlit page configuration
st.set_page_config(
    page_title="Personal Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Set up OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

st.title("My Name Is Anna")

# Sidebar UI
with st.sidebar:
    st.title("Personal Assistant")
    st.markdown("""
    **Welcome!**
    This is my personal assistant powered by OpenAI.
    """)

    st.divider()
    st.subheader("Chat History (dict format)")
    st.divider()
    # Display chat history as a list of dicts
    st.json(st.session_state.messages)

# Main chat interface
user_input = st.chat_input("What's on your mind?")
role_icons = {
    "user": "♟️",
    "assistant": "🌹",
    "system": "⚙️"
}

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Prepare messages for OpenAI API
    messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    # Get assistant response from GPT-4o-mini
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    assistant_reply = response.choices[0].message.content

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

# Display conversation in main panel
for message in st.session_state.messages:
    avatar = role_icons.get(message["role"], "")
    with st.chat_message(message["role"], avatar=avatar):
        st.write(message["content"])