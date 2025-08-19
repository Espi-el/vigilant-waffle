
import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from mem0 import Memory

# Load environment variables from .env file
load_dotenv()


# Check for required environment variables
if 'DATABASE_URL' not in os.environ:
    raise RuntimeError("DATABASE_URL environment variable is required. Please set it in your .env file.")
if 'OPENAI_API_KEY' not in os.environ:
    raise RuntimeError("OPENAI_API_KEY environment variable is required. Please set it in your .env file.")

# Model selection
model = os.getenv('MODEL_CHOICE', 'gpt-4o-mini')

# Streamlit page configuration
st.set_page_config(
    page_title="Mem0 Chat Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Cache OpenAI client and Memory instance
@st.cache_resource
def get_openai_client():
    return OpenAI()

@st.cache_resource
def get_memory():
    config = {
        "llm": {
            "provider": "openai",
            "config": {
                "model": model
            }
        },
        "vector_store": {
            "provider": "supabase",
            "config": {
                "connection_string": os.environ['DATABASE_URL'],
                "collection_name": "memories"
            }
        }
    }
    return Memory.from_config(config)

openai_client = get_openai_client()
memory = get_memory()

# Chat function with memory

# Chat function with memory
def chat_with_memories(message, user_id):
    # Retrieve relevant memories
    relevant_memories = memory.search(query=message, user_id=user_id, limit=3)
    memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])

    # Generate Assistant response
    system_prompt = f"You are a helpful AI assistant with memory. Answer the question based on the query and user's memories.\nUser Memories:\n{memories_str}"
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}]

    with st.spinner("Thinking..."):
        response = openai_client.chat.completions.create(model=model, messages=messages)
        assistant_response = response.choices[0].message.content

    # Create new memories from the conversation
    messages.append({"role": "assistant", "content": assistant_response})
    memory.add(messages, user_id=user_id)

    return assistant_response


# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Use a static user_id for single-user mode
user_id = "default_user"


# Sidebar UI
with st.sidebar:
    st.title("🧠 Mem0 Chat Assistant")
    st.markdown("""
    **Welcome!**
    
    - Chat with your memory-powered AI assistant.
    - All conversations are private to you.
    - [Streamlit Docs](https://docs.streamlit.io/)
    """)
    st.divider()
    st.info("Your data is stored securely in Supabase.")

# Main chat interface
st.title("New Chat")
st.write("All conversations saved in table1 in supabase.")

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

    # Get AI response
    ai_response = chat_with_memories(user_input, user_id)

    # Add AI response to chat history
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

    # Display AI response
    with st.chat_message("assistant"):
        st.write(ai_response)
