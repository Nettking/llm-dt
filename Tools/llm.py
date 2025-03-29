import os
import re
import time
import json
import tempfile
import traceback
import subprocess
import requests
from datetime import datetime


class LLM:
    def __init__(self, host="localhost:11434", model="llama3.1:latest"):
        self.host = host
        self.model = model

    def _chat(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"http://{self.host}/api/chat",
                json={"model": self.model, "messages": [{"role": "user", "content": prompt}]},
                stream=True
            )

            if response.status_code != 200:
                print(f"❌ Error {response.status_code}: {response.text}")
                return ""

            full_response = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    content = data.get("message", {}).get("content", "")
                    full_response += content
            
            if not full_response:
                print("⚠️ Warning: Ollama returned an empty response.")

            return full_response.strip()

        except requests.exceptions.RequestException as e:
            print("❌ Failed to contact Ollama:", e)
            return ""


    def clean_code(self, response: str) -> str:
        code_blocks = re.findall(r"```(?:python)?\n(.*?)```", response, re.DOTALL)
        return code_blocks[0].strip() if code_blocks else response.strip()

    def generate_code(self, purpose: str) -> str:
        prompt = f"""Write a complete Python script that fulfills the following purpose:\n\n"{purpose}"\n\nReturn only the full code."""
        return self.clean_code(self._chat(prompt))

    def get_suggestions(self, code: str) -> list[str]:
        prompt = f"""You are an experienced Python developer. Given the following code:\n\n--- CODE ---\n{code}\n\nSuggest 3 improvements or refactorings. Keep them short and numbered."""
        response = self._chat(prompt)
        suggestions = [line.strip() for line in response.splitlines() if line.strip().startswith(("1.", "2.", "3."))]
        return suggestions

    def apply_suggestion(self, code: str, suggestion: str) -> str:
        prompt = f"""You're a Python coding assistant. Update the code below according to the instruction.\n\n--- INSTRUCTION ---\n{suggestion}\n\n--- ORIGINAL CODE ---\n{code}\n\nRespond with the updated code only."""
        return self.clean_code(self._chat(prompt))

    def fix_code_error(self, code: str, error: str) -> str:
        prompt = f"""The following Python script causes an error when executed.\n\n--- Code ---\n{code}\n\n--- Error ---\n{error}\n\nFix the error so that the script runs correctly and fulfills the original intent. Return the full updated code only."""
        return self.clean_code(self._chat(prompt))

    def explain_exception(self, exc: Exception):
        error_details = traceback.format_exc()
        prompt = f"I got this Python exception:\n\n{error_details}\n\nCan you explain what it means, and suggest some possible fixes?"
        try:
            response = requests.post(
                f"http://{self.host}/api/chat",
                json={"model": self.model, "messages": [{"role": "user", "content": prompt}]},
                stream=True
            )
            print("\n🤖 Ollama says:\n")
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode("utf-8"))
                    print(data.get("message", {}).get("content", ""), end="", flush=True)
            print()
        except Exception as e:
            print("Error contacting Ollama:", e)

    def try_run_code(self, code: str) -> tuple[bool, str, str]:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            path = f.name
        try:
            result = subprocess.run(["python3", path], capture_output=True, text=True, timeout=10)
            return result.returncode == 0, result.stderr.strip(), result.stdout.strip()
        except Exception as e:
            return False, str(e), ""
        finally:
            os.remove(path)

    def run_code(self, code: str):
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

    def evolve_script(self, purpose: str, max_iterations=10, max_fixes=3, save=True):
        print(f"🎯 Purpose: {purpose}")
        code = self.generate_code(purpose)
        print("\n🧠 Initial Code:\n" + "-" * 40 + f"\n{code}\n" + "-" * 40)

        iteration = 0
        while iteration < max_iterations:
            print(f"\n🔁 Iteration {iteration + 1}")
            success, error, output = self.try_run_code(code)
            if not success:
                print("❌ Script failed. Attempting to fix...")
                for fix_attempt in range(max_fixes):
                    code = self.fix_code_error(code, error)
                    success, error, output = self.try_run_code(code)
                    if success:
                        print(f"✅ Fixed and ran on attempt {fix_attempt + 1}")
                        break
                else:
                    print("💥 Could not fix the script after multiple attempts.")
                    return
            if self.verify_output_fulfills_purpose(purpose, output):
                print("🎉 Success! The script fulfills its purpose.")
                break
            suggestions = self.get_suggestions(code)
            if not suggestions:
                print("🤷 No more suggestions. Stopping.")
                break
            print(f"💡 Applying suggestion: {suggestions[0]}")
            code = self.apply_suggestion(code, suggestions[0])
            iteration += 1

        print(f"\n✅ Final Code after {iteration} iteration{'s' if iteration != 1 else ''}:")
        print("-" * 40 + f"\n{code}\n" + "-" * 40)

        if save:
            self.save_code(code, purpose)

        run_final = input("\n🚀 Do you want to run the final version? (y/n): ")
        if run_final.lower() == "y":
            _, _, final_output = self.try_run_code(code)
            print(f"\n📤 Final Output:\n{final_output}")

    def verify_output_fulfills_purpose(self, purpose: str, output: str) -> bool:
        prompt = f"""The original goal is: \"{purpose}\"\n\nThe script produced this output:\n\n--- Output ---\n{output}\n\nDoes this output fulfill the goal? Answer with only \"yes\" or \"no\"."""
        response = self._chat(prompt).strip().lower()
        return response.startswith("yes")

    def save_code(self, code: str, purpose: str, directory="evolved_scripts"):
        os.makedirs(directory, exist_ok=True)
        filename = f"{directory}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        with open(filename, "w") as f:
            f.write("# Purpose: " + purpose + "\n\n" + code)
        print(f"💾 Final script saved to: {filename}")

    def wait_for_ready(self, max_attempts=30):
        print("⏳ Waiting for Ollama to be ready...")
        for _ in range(max_attempts):
            try:
                res = requests.get(f"http://{self.host}/api/tags")
                if res.status_code == 200:
                    print("✅ Ollama is ready.")
                    return True
            except Exception:
                pass
            time.sleep(1)
        raise RuntimeError("❌ Ollama did not start in time.")

    def model_exists(self, model_name: str) -> bool:
        tags = self.wait_for_tags()
        models = [m["name"] for m in tags.get("models", [])]
        print("Available models:", models)
        return any(model_name in m for m in models)

    def wait_for_tags(self, max_attempts=10):
        for attempt in range(max_attempts):
            try:
                res = requests.get(f"http://{self.host}/api/tags")
                if res.status_code == 200:
                    return res.json()
            except:
                pass
            print(f"⏳ Waiting for Ollama model registry... ({attempt + 1}/{max_attempts})")
            time.sleep(1)
        raise RuntimeError("❌ Timed out waiting for /api/tags")

    def pull_model(self, model_name: str):
        if self.model_exists(model_name):
            print(f"✅ Model '{model_name}' already present.")
            return
        print(f"⬇️ Pulling model '{model_name}' from Ollama...")
        response = requests.post(f"http://{self.host}/api/pull", json={"name": model_name}, stream=True)
        for line in response.iter_lines():
            if line:
                print(line.decode("utf-8"))
        print("✅ Model pull complete.")

        def list_available_models(self):
    print("📦 Fetching list of available models from Ollama...")
    try:
        response = requests.get(f"http://{self.host}/api/tags")
        if response.status_code != 200:
            print(f"❌ Error fetching models: {response.status_code} - {response.text}")
            return

        tags_data = response.json()
        models = tags_data.get("models", [])
        if not models:
            print("⚠️ No models found.")
            return

        print("✅ Available models:")
        for model in models:
            print(f" - {model.get('name')}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to Ollama: {e}")

