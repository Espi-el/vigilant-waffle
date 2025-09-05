
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

# exported_conversations = flatten_conversations("conversations.json")

memory = DiffMemory("./assistant/", "anna", os.getenv('OPENAI_API_KEY'))
