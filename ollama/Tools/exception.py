import traceback
import requests
import json

OLLAMA_HOST = "localhost:11435"
MODEL_NAME = "llama3:latest"  # Use exact name from `ollama list` or `pull`

def explain_exception(exc: Exception):
    error_details = traceback.format_exc()
    prompt = f"""I got this Python exception:\n\n{error_details}\n\nCan you explain what it means, and suggest some possible fixes?"""

    url = f"http://{OLLAMA_HOST}/api/chat"
    headers = {"Content-Type": "application/json"}

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()

        print("\n🤖 Ollama says:\n")
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                content = data.get("message", {}).get("content", "")
                print(content, end="", flush=True)
        print()

    except Exception as e:
        print("Error contacting Ollama:", e)

# -------------------------------
# 🔥 DEMO: Simulated error
# -------------------------------
try:
    # 👇 Replace this with any buggy code you want to debug
    result = 1 / 0

except Exception as e:
    explain_exception(e)
