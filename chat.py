import ollama

def chat_response(chat: dict) -> str:
    response = ollama.chat(
        model="llama3.2:latest",
        messages=chat,
    )
    return response["message"]["content"]