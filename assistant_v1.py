
import os, json, time
from dotenv import load_dotenv
from openai import OpenAI
from json_convert import flatten_conversations
from memory_api import DiffMemory
from datetime import datetime
from textwrap import wrap

def chunk_text(text, max_chars=80000):
    """
    Splits large text into chunks of ~max_chars length
    to stay under token limits. (80000 chars ≈ 20000 tokens)
    """
    return wrap(text, max_chars, break_long_words=False, replace_whitespace=False)

def summarize_text(text, client):
    """Calls GPT to summarize a block of conversation as a diary-style memory entry."""
    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a personal assistant that summarizes conversations into diary-style memory entries. "
                      "Write in a personable, and engaging tone, capturing the user's voice and the assistant's responses. "
                    "Highlight important ideas, questions, decisions, reactions, and recurring topics. "
                    "Make it feel like a natural journal entry that someone could read later to remember the day."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Here is a conversation snippet:\n\n{text}\n\n"
                    "Please summarize it as a diary-style entry. Keep it detailed, readable, and engaging. "
                    "Include key points, questions, and notable reactions. "
                    "Do not worry about word count; focus on capturing the richness of the conversation."
                )
            }
        ],
        temperature=1  # Slightly higher for liveliness
    )
    return response.choices[0].message.content

def load_and_flatten_conversations(input_path):
    return flatten_conversations(input_path)

def group_conversations_by_date(conversations):
    daily_conversations = {}
    for conv in conversations:
        ts = conv.get("create_time")
        date = str(datetime.fromisoformat(ts).date())
        if date not in daily_conversations:
            daily_conversations[date] = {
                "title": conv.get("title", f"Session {date}"),
                "messages": []
            }
        for idx, msg in enumerate(conv.get("messages", [])):
            role = "user" if idx % 2 == 0 else "assistant"
            formatted_msg = dict(msg)
            formatted_msg["role"] = role
            daily_conversations[date]["messages"].append(formatted_msg)
    return daily_conversations

def summarize_conversations(daily_conversations, client, progress_filename):
    daily_summaries = {}
    print(f"Total dates to summarize: {len(daily_conversations)}")
    for date_idx, (date, data) in enumerate(daily_conversations.items()):
        print(f"Summarizing date {date_idx+1}/{len(daily_conversations)}: {date}")
        raw_text = "\n".join([f"{m['role']}: {m['content']}" for m in data["messages"]])
        chunks = chunk_text(raw_text)
        partial_summaries = [summarize_text(chunk, client) for chunk in chunks]
        combined_summary_text = "\n".join(partial_summaries)
        final_summary = summarize_text(combined_summary_text, client)
        daily_summaries[date] = {
            "title": data["title"],
            "summary": final_summary
        }
        with open(progress_filename, "w", encoding="utf-8") as f:
            json.dump(daily_summaries, f, indent=2, ensure_ascii=False)
    return daily_summaries

def main():
    # Load environment variables from .env file
    load_dotenv()
    if 'OPENAI_API_KEY' not in os.environ:
        raise RuntimeError("OPENAI_API_KEY environment variable is required. Please set it in your .env file.")
    model = os.getenv('MODEL_CHOICE', 'gpt-5-nano')
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    # conversations = load_and_flatten_conversations("./test/conversations.json")
    # daily_conversations = group_conversations_by_date(conversations)
    # progress_filename = f"daily_summaries_progress_{int(time.time())}.json"
    # summarize_conversations(daily_conversations, client, progress_filename)

if __name__ == "__main__":
    main()
# Load environment variables from .env file
load_dotenv()


if 'OPENAI_API_KEY' not in os.environ:
    raise RuntimeError("OPENAI_API_KEY environment variable is required. Please set it in your .env file.")


model = os.getenv('MODEL_CHOICE', 'gpt-5-nano')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
memory = DiffMemory("./assistant/", "anna", os.getenv('OPENAI_API_KEY'))

# exported_conversations = flatten_conversations("conversations.json")

# memory = DiffMemory("./assistant/", "anna", os.getenv('OPENAI_API_KEY'))

# Purpose of this file is to run the streamlit command normally run in the tuerminal
# among other potential future uses
# like generating memory block entities from exports

# conversations = flatten_conversations("./test/conversations.json")
# daily_conversations = group_conversations_by_date(conversations)

# progress_filename = f"daily_summaries_progress_{int(time.time())}.json"
# daily_summaries = summarize_conversations(daily_conversations, client, progress_filename)

# print(f"Total dates to summarize: {len(daily_conversations)}")

json_summaries = "daily_summaries_progress_1758074506.json"
with open(json_summaries, "r", encoding="utf-8") as f:
    new_entities = json.load(f)

for session_date, session_data in new_entities.items():
    session_transcript = session_data["summary"]
    session_title = session_data["title"]
    session_id = f"{session_date}-{session_title}"
    memory.process_session(session_transcript, session_id)
print("Session processed and staged.")