import requests
import json
import subprocess
import tempfile
import os

# === CONFIG ===
OLLAMA_HOST = "localhost:11435"
MODEL_NAME = "llama3:latest"  # or mistral, gemma:2b, etc.
FILE_TO_EDIT = "my_script.py"  # Change this to the file you want to edit


def send_prompt(code: str, instruction: str) -> str:
    prompt = f"""
You are an AI developer. You are given a Python script and an instruction.
Update the script to satisfy the instruction. Respond with ONLY the full, modified code.

--- Code ---
{code}

--- Instruction ---
{instruction}
"""

    response = requests.post(
        f"http://{OLLAMA_HOST}/api/chat",
        json={
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}]
        },
        stream=True
    )

    new_code = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            chunk = data.get("message", {}).get("content", "")
            print(chunk, end="", flush=True)
            new_code += chunk

    # 🧹 Remove markdown formatting (```python ... ```)
    if new_code.strip().startswith("```"):
        new_code = "\n".join(
            line for line in new_code.strip().splitlines()
            if not line.strip().startswith("```")
        )

    return new_code.strip()


def run_code(code: str):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(code)
        temp_filename = temp_file.name

    print(f"\n\n⚙️ Running updated code...\n{'-'*40}")
    try:
        subprocess.run(["python3", temp_filename], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running code:\n{e}")
    finally:
        os.remove(temp_filename)


def main():
    if not os.path.exists(FILE_TO_EDIT):
        print(f"❌ File not found: {FILE_TO_EDIT}")
        return

    with open(FILE_TO_EDIT, "r") as f:
        current_code = f.read()

    instruction = input("💬 What should I change or add in the code?\n> ")

    print("\n🧠 Sending code and instruction to model...\n")
    updated_code = send_prompt(current_code, instruction)

    confirm = input("\n\n💾 Overwrite original file with updated code? (y/n): ")
    if confirm.lower() == "y":
        with open(FILE_TO_EDIT, "w") as f:
            f.write(updated_code)
        print("✅ File updated.")

    run = input("\n🚀 Do you want to run the updated code now? (y/n): ")
    if run.lower() == "y":
        run_code(updated_code)


if __name__ == "__main__":
    main()
