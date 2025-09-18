import streamlit as st
from openai import OpenAI
import os
import json
from memory_api import DiffMemory
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

if 'OPENAI_API_KEY' not in os.environ:
    raise RuntimeError("OPENAI_API_KEY environment variable is required. Please set it in your .env file.")
model = os.getenv('MODEL_CHOICE', 'gpt-5-nano')

# exported_conversations = flatten_conversations("conversations.json")
memory = DiffMemory("./assistant/", "anna", os.getenv('OPENAI_API_KEY'))
repo_status = memory.get_repo_status()
anna_entity = memory.get_user_entity()
timeline = memory.get_recent_timeline()
context = memory.get_context(anna_entity)
git_memory = memory.orchestrated_search(context)

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
print(os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=openai_api_key)

st.title("My Name Is Anna")

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

# Sidebar UI
with st.sidebar:
    st.title("Personal Assistant")
    st.markdown("""
    **Welcome!**
    This is my personal assistant powered by OpenAI.
    """)
    # st.write(repo_status) #add optional show button
    # st.write(anna_entity)
    # st.write(timeline)
    st.write(context)
    st.write(git_memory)
    
    st.divider()
    # st.subheader("Chat History (dict format)")
    st.divider()
    # Display chat history as a list of dicts
    # if user_input:
    #     for idx in st.json(st.session_state.messages):
    #         st.json(st.session_state.