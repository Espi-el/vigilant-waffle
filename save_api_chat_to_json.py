import json
from openai import OpenAI
from supabase import create_client
import os

client = OpenAI()
supabase = create_client(
    url=os.environ.get("SUPABASE_URL", ""),
    key=os.environ.get("SUPABASE_KEY", "")
)

def ask_chatgpt(prompt):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    reply = response.choices[0].message.content

    # Save prompt/response
    log_entry = {"prompt": prompt, "response": reply}
    with open("chat_log.json", "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return reply

# The string "chat_logs" is the name of the table where the information will be saved
def save_chat_log(prompt, response):
    supabase.table("chat_logs").insert({"prompt": prompt, "response": response}).execute()