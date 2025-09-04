# ui.py
import streamlit as st
from assistant_v1 import MemoryAgent

# Initialize only once
if "agent" not in st.session_state:
    st.session_state.agent = MemoryAgent()

st.title("My Personal AI Assistant")

user_input = st.text_input("Say something:")

if st.button("Send") and user_input:
    st.session_state.agent.add_message("user", user_input)
    st.write("Conversation so far:")
    for msg in st.session_state.agent.get_context():
        st.write(f"{msg['role']}: {msg['content']}")