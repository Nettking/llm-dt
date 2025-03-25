import requests
import json
import subprocess
import tempfile
import os
import re

# === CONFIG ===
OLLAMA_HOST = "localhost:11435"
MODEL_NAME = "llama3:latest"
FILE_TO_EDIT = "my_script.py"


def ollama_chat(prompt: str) -> str:
    """Send a prompt to the model and return its response."""
    response = requests.post(
        f"http://{OLLAMA_HOST}/api/chat",
        json={
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}]
        },
        stream=True
    )

    full_response = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            chunk = data.get("message", {}).get("content", "")
            print(chunk, end="", flush=True)
            full_response += chunk

    return full_response.strip()


def clean_code(response: str) -> str:
    """
    Extracts the first Python code block from a model response,
    or returns the cleaned response if no block is found.
    """
    # Extract code inside triple backticks
    code_blocks = re.findall(r"```(?:python)?\n(.*?)```", response, re.DOTALL)

    if code_blocks:
        return code_blocks[0].strip()

    # Fallback: filter for lines that look like actual code
    lines = response.strip().splitlines()
    cleaned = []
    for line in lines:
        if (
            line.strip().startswith("#")
            or line.strip().startswith("import")
            or "=" in line
            or line.strip().startswith("def ")
            or line.strip().startswith("print(")
        ):
            cleaned.append(line)
    return "\n".join(cleaned).strip()


def get_suggestions(code: str) -> list[str]:
    prompt = f"""
You are an experienced Python developer. Given the following code:

--- CODE ---
{code}

Suggest 3 improvements or refactorings. Keep them short and numbered.
"""

    response = ollama_chat(prompt)
    suggestions = []

    for line in response.splitlines():
        if line.strip().startswith(("1.", "2.", "3.")):
            suggestions.append(line.strip())

    return suggestions


def apply_suggestion(code: str, suggestion: str) -> str:
    prompt = f"""
You're a Python coding assistant. Update the code below according to the instruction.

--- INSTRUCTION ---
{suggestion}

--- ORIGINAL CODE ---
{code}

Respond with the updated code only.
"""

    updated_code = ollama_chat(prompt)
    return clean_code(updated_code)


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

    print("\n🧠 Asking the model for suggestions...\n")
    suggestions = get_suggestions(current_code)

    if not suggestions:
        print("🤔 No suggestions received.")
        return

    print("\n💡 Suggested improvements:")
    for i, s in enumerate(suggestions, 1):
        print(f"{i}. {s}")

    choice = input("\n👉 Choose a suggestion (1-3), or type 'n' to cancel: ")
    if choice.lower() == 'n':
        print("🚫 No changes made.")
        return

    try:
        selected = suggestions[int(choice) - 1]
    except (ValueError, IndexError):
        print("⚠️ Invalid choice.")
        return

    print(f"\n✅ Applying suggestion: {selected}")
    updated_code = apply_suggestion(current_code, selected)

    confirm = input("\n💾 Overwrite original file with updated code? (y/n): ")
    if confirm.lower() == "y":
        with open(FILE_TO_EDIT, "w") as f:
            f.write(updated_code)
        print("✅ File updated.")

    run = input("\n🚀 Run the updated code? (y/n): ")
    if run.lower() == "y":
        run_code(updated_code)


if __name__ == "__main__":
    main()
