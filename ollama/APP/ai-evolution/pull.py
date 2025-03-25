import time
import requests

OLLAMA_HOST = "http://localhost:11434"
MODEL = "gemma3:1b"

def wait_for_tags(max_attempts=10):
    for attempt in range(max_attempts):
        try:
            res = requests.get(f"{OLLAMA_HOST}/api/tags")
            if res.status_code == 200:
                return res.json()
        except:
            pass
        print(f"⏳ Waiting for Ollama model registry... ({attempt + 1}/{max_attempts})")
        time.sleep(1)
    raise RuntimeError("❌ Timed out waiting for /api/tags")

def model_exists(model_name: str) -> bool:
    data = wait_for_tags()
    models = [m["name"] for m in data.get("models", [])]
    print("Available models:", models)

    return any(model_name in m for m in models)

if model_exists(MODEL):
    print(f"✅ Model '{MODEL}' already present.")
else:
    print(f"⬇️ Pulling model '{MODEL}' from Ollama...")
    response = requests.post(f"{OLLAMA_HOST}/api/pull", json={"name": MODEL}, stream=True)
    for line in response.iter_lines():
        if line:
            print(line.decode("utf-8"))
    print("✅ Model pull complete.")
