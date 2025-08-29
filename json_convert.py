import json

def flatten_conversations(input_file: str, output_file: str):
    """
    Reads a conversation JSON file (list of conversations), flattens each, and writes a simplified list to output_file.
    Keeps only: title, create_time, update_time, messages (author, role, create_time, content).
    """
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    flattened_list = []
    for conv in data:
        flattened = {
            "title": conv.get("title"),
            "conversation_id": conv.get("conversation_id"),
            "create_time": conv.get("create_time"),
            "update_time": conv.get("update_time"),
            "messages": []
        }

        for msg_id, msg_data in conv.get("mapping", {}).items():
            message = msg_data.get("message")
            if message:
                author_info = message.get("author", {})
                content_info = message.get("content", {})
                parts = content_info.get("parts", [""])
                content_text = " ".join(
                    p if isinstance(p, str) else p.get("text", str(p)) for p in parts)
                if content_text.strip() != "":
                    flattened["messages"].append({
                        "author": author_info.get("name", author_info.get("role", "unknown")),
                        "role": author_info.get("role", "unknown"),
                        "create_time": message.get("create_time"),
                        "content": content_text
                    })

        flattened["messages"].sort(key=lambda x: (x["create_time"] or 0))
        flattened_list.append(flattened)

    return flattened_list