
import os, inspect
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from json_convert import flatten_conversations
from memory_api import DiffMemory
from pathlib import Path


# Load environment variables from .env file
load_dotenv()


if 'OPENAI_API_KEY' not in os.environ:
    raise RuntimeError("OPENAI_API_KEY environment variable is required. Please set it in your .env file.")


model = os.getenv('MODEL_CHOICE', 'gpt-4o-mini')

conversations = flatten_conversations("conversations.json")
# memory = DiffMemory("/path/to/repo", "sean", "your-openai-key")
memory = DiffMemory("./assistant/users/anna", "anna", os.getenv('OPENAI_API_KEY'))
# Streamlit page configuration
st.set_page_config(
    page_title="Personal Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)
@st.cache_resource
def get_openai_client():
    return OpenAI()

# openai_client = get_openai_client()


# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Use a static user_id for single-user mode
REPO_PATH = "./memory"  
USER_ID = "sean"

# Sidebar UI
with st.sidebar:
    st.title("Personal Assistant")
    st.markdown("""
    **Welcome!**
    This is your personal assistant powered by OpenAI and Mem0.
    """)
    st.divider()
    st.info("Your data is stored securely in Supabase.")
    st.divider()
    st.sidebar.subheader("Raw Chat History")
    st.divider()
    st.sidebar.json(st.session_state.messages)

# Main chat interface

st.title("New Chat")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
