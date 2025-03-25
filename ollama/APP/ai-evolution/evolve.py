import requests
import json
import re
import subprocess
import tempfile
import os
from datetime import datetime

OLLAMA_HOST = "localhost:11434"
MODEL = "gemma3:1b"


def ollama_chat(prompt: str) -> str:
    response = requests.post(
        f"http://{OLLAMA_HOST}/api/chat",
        json={"model": MODEL, "messages": [{"role": "user", "content": prompt}]},
        stream=True
    )
    full_response = ""
    for line in response.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8"))
            full_response += data.get("message", {}).get("content", "")
    return full_response.strip()


def clean_code(response: str) -> str:
    code_blocks = re.findall(r"```(?:python)?\n(.*?)```", response, re.DOTALL)
    return code_blocks[0].strip() if code_blocks else response.strip()


def generate_initial_code(purpose: str) -> str:
    prompt = f"""Write a complete Python script that fulfills the following purpose:

"{purpose}"

Return only the full code."""
    return clean_code(ollama_chat(prompt))


def get_improvement_suggestions(code: str) -> list[str]:
    prompt = f"""Review this Python script and list up to 3 specific improvements or refactorings.

--- Code ---
{code}

If there are no improvements to suggest, say:
"No further improvements needed."
"""
    response = ollama_chat(prompt)
    suggestions = []
    for line in response.splitlines():
        if line.strip().startswith(("1.", "2.", "3.")):
            suggestions.append(line.strip())
        elif "no further" in line.lower():
            return []
    return suggestions


def apply_suggestion(code: str, suggestion: str) -> str:
    prompt = f"""Improve this Python code based on the following instruction:

{suggestion}

--- Code ---
{code}

Return the full updated code only."""
    return clean_code(ollama_chat(prompt))


def fix_code_error(code: str, error: str) -> str:
    prompt = f"""The following Python script causes an error when executed.

--- Code ---
{code}

--- Error ---
{error}

Fix the error so that the script runs correctly and fulfills the original intent. Return the full updated code only."""
    return clean_code(ollama_chat(prompt))


def try_run_code(code: str) -> tuple[bool, str, str]:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        path = f.name

    try:
        result = subprocess.run(["python3", path], capture_output=True, text=True, timeout=10)
        return (result.returncode == 0, result.stderr.strip(), result.stdout.strip())
    except Exception as e:
        return False, str(e), ""
    finally:
        os.remove(path)


def verify_output_fulfills_purpose(purpose: str, output: str) -> bool:
    prompt = f"""
The original goal is: "{purpose}"

The script produced this output:

--- Output ---
{output}

Does this output fulfill the goal? Answer with only "yes" or "no"."""
    response = ollama_chat(prompt).strip().lower()
    return response.startswith("yes")


def save_code(code: str, purpose: str, directory="evolved_scripts"):
    os.makedirs(directory, exist_ok=True)
    filename = f"{directory}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    with open(filename, "w") as f:
        f.write("# Purpose: " + purpose + "\n\n" + code)
    print(f"💾 Final script saved to: {filename}")


def evolve_script(purpose: str, max_iterations=10, max_fixes=3, save=True):
    print(f"🎯 Purpose: {purpose}")
    code = generate_initial_code(purpose)
    print("\n🧠 Initial Code:\n" + "-" * 40 + f"\n{code}\n" + "-" * 40)

    iteration = 0
    while iteration < max_iterations:
        print(f"\n🔁 Iteration {iteration + 1}")

        success, error, output = try_run_code(code)

        if not success:
            print("❌ Script failed. Attempting to fix...")
            for fix_attempt in range(max_fixes):
                code = fix_code_error(code, error)
                success, error, output = try_run_code(code)
                if success:
                    print(f"✅ Fixed and ran on attempt {fix_attempt + 1}")
                    break
            else:
                print("💥 Could not fix the script after multiple attempts.")
                return

        print("🔍 Verifying output against the goal...")
        if verify_output_fulfills_purpose(purpose, output):
            print("🎉 Success! The script fulfills its purpose.")
            break
        else:
            print("⚠️ Output does not fulfill the purpose.")

        suggestions = get_improvement_suggestions(code)
        if not suggestions:
            print("🤷 No more suggestions. Stopping.")
            break

        print(f"💡 Applying suggestion: {suggestions[0]}")
        code = apply_suggestion(code, suggestions[0])
        iteration += 1

    print(f"\n✅ Final Code after {iteration} iteration{'s' if iteration != 1 else ''}:\n" + "-" * 40)
    print(code)
    print("-" * 40)

    if save:
        save_code(code, purpose)

    run_final = input("\n🚀 Do you want to run the final version? (y/n): ")
    if run_final.lower() == "y":
        _, _, final_output = try_run_code(code)
        print(f"\n📤 Final Output:\n{final_output}")


# === RUN ===
if __name__ == "__main__":
    purpose = input("📝 What is the purpose of this script?\n> ")
    evolve_script(purpose)
