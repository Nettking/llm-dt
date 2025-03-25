import os
import requests
import json

def chat_with_ollama(message, model="llama3:latest"):
    ollama_host = os.environ.get("OLLAMA_HOST", "localhost:11435")
    url = f"http://{ollama_host}/api/chat"

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": message}
        ]
    }

    with requests.post(url, json=payload, stream=True) as response:
        response.raise_for_status()
        print("Ollama: ", end="", flush=True)
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                content = data.get("message", {}).get("content", "")
                print(content, end="", flush=True)
        print()

# Run
if __name__ == "__main__":
    user_input = input("You: ")
    chat_with_ollama(user_input)
