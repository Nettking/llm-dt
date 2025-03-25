import time
import requests

OLLAMA_HOST = "http://localhost:11434"

print("⏳ Waiting for Ollama to be ready...")
for _ in range(30):
    try:
        res = requests.get(f"{OLLAMA_HOST}/api/tags")
        if res.status_code == 200:
            print("✅ Ollama is ready.")
            break
    except Exception:
        pass
    time.sleep(1)
else:
    raise RuntimeError("❌ Ollama did not start in time.")
