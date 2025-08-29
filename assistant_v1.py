
import os, inspect
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
#from mem0 import Memory
#from supabase import create_client
#from langchain.vectorstores import SupabaseVectorStore
#from langchain.embeddings.openai import OpenAIEmbeddings
from json_convert import flatten_conversations
from memory_api import DiffMemory


# Load environment variables from .env file
load_dotenv()

# Check for required environment variables
# if 'DATABASE_URL' not in os.environ:
#     raise RuntimeError("DATABASE_URL environment variable is required. Please set it in your .env file.")
if 'OPENAI_API_KEY' not in os.environ:
    raise RuntimeError("OPENAI_API_KEY environment variable is required. Please set it in your .env file.")

# Model selection
model = os.getenv('MODEL_CHOICE', 'gpt-4o-mini')

# Use the same embedding model you used for storage
# embeddings = OpenAIEmbeddings()

#### This function caused connection limit with supabase database
# supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

conversations = flatten_conversations("conversations.json")

# Streamlit page configuration
st.set_page_config(
    page_title="Personal Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Cache OpenAI client and Memory instance
@st.cache_resource
def get_openai_client():
    return OpenAI()

# @st.cache_resource
# def get_memory():
#     config = {
#         "llm": {
#             "provider": "openai",
#             "config": {
#                 "model": model
#             }
#         },
#         "vector_store": {
#             "provider": "supabase",
#             "config": {
#                 "connection_string": os.environ['DATABASE_URL'],
#                 "collection_name": "memories"
#             }
#         }
#     }
#     return Memory.from_config(config)

openai_client = get_openai_client()
# memory = get_memory()

# # Delete memories function
# def delete_memories(user_id):
#     Memory().delete_all(user_id=user_id)

# # Chat function with memory
# def chat_with_memories(message, user_id):
#     # Retrieve relevant memories
#     relevant_memories = memory.search(query=message, user_id=user_id, limit=3) #This works as my retrieval agent as well
#     memories_str = "\n".join(f"- {entry['memory']}" for entry in relevant_memories["results"])

#     # Generate Assistant response - Make Better!!
#     system_prompt = f"You are a helpful AI assistant with memory. Answer the question based on the query and user's memories.\nUser Memories:\n{memories_str}"
#     messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}]

#     with st.spinner("Thinking..."):
#         response = openai_client.chat.completions.create(model=model, messages=messages)
#         assistant_response = response.choices[0].message.content

#     # Create new memories from the conversation
#     messages.append({"role": "assistant", "content": assistant_response})
#     memory.add(messages, user_id=user_id)

#     return assistant_response


# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Use a static user_id for single-user mode
user_id = "default_user"

# # Try to initialize vectorstore and run similarity search, catch missing table error
# try:
#     vectorstore = SupabaseVectorStore(
#         client=supabase,
#         table_name="memories",   # your existing table
#         embedding=embeddings
#     )
#     # Vector store initialized successfully.
# except Exception as e:
#     import psycopg2
#     from psycopg2 import sql
#     if (
#         hasattr(e, 'args') and e.args and isinstance(e.args[0], dict)
#         and 'message' in e.args[0] and 'relation "memories" does not exist' in e.args[0]['message']
#     ) or (
#         'relation "memories" does not exist' in str(e)
#     ):
#         st.error("The 'memories' table does not exist in your database. Please create it in Supabase/Postgres to enable memory features.")
#         # Try to list available tables
#         try:
#             conn = psycopg2.connect(os.environ['DATABASE_URL'])
#             cur = conn.cursor()
#             cur.execute("""
#                 SELECT table_schema, table_name
#                 FROM information_schema.tables
#                 WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema')
#                 ORDER BY table_schema, table_name;
#             """)
#             tables = cur.fetchall()
#             if tables:
#                 st.info("Available tables in your database:")
#                 for schema, table in tables:
#                     st.write(f"{schema}.{table}")
#             else:
#                 st.info("No user tables found in your database.")
#             cur.close()
#             conn.close()
#         except Exception as db_e:
#             st.warning(f"Could not list tables: {db_e}")
#         vectorstore = None
#         results = []
#     else:
#         raise

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

    # Mem0 collections display
    # mem0_client = Memory()
    # try:
    #     collections = mem0_client.list_collections()
    #     st.subheader("Mem0 Collections")
    #     st.write(collections)
    # except Exception as e:
    #     st.warning(f"Could not fetch Mem0 collections: {e}")
    # if st.button("Delete All Memories", type="primary"):
    #     delete_memories(user_id)
    #     st.session_state.messages = []
    #     st.success("All memories deleted!")
    
    # Similarity search UI
    # st.subheader("Search Memories")
    # search_query = st.text_input("Enter search query", key="memory_search")
    # if search_query:
    #     # Run similarity search using the vector store
    #     results = memory.vector_store.similarity_search(search_query, k=3)
    #     st.write("Top results:")
    #     for r in results:
    #         st.write(r)

# Main chat interface

st.title("New Chat")
# st.write("All conversations saved in table1 in supabase.")
# st.write(inspect.signature(Memory.delete_all))

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
    # ai_response = chat_with_memories(user_input, user_id)

    # Add AI response to chat history
    # st.session_state.messages.append({"role": "assistant", "content": ai_response}) # Needed Git Version

    # Display AI response
    # with st.chat_message("assistant"):
    #     st.write(ai_response) # Need Git Version
