import os
import difflib
import datetime
from llm import LLM

BACKUP_DIR = "backups"
LOG_FILE = "update_log.txt"

def list_python_files(base_dir="."):
    python_files = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                full_path = os.path.join(root, file)
                python_files.append(full_path)
    return python_files

def select_file(files):
    print("\n📄 Available Python files:\n")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    print("0. Cancel")

    while True:
        try:
            choice = int(input("\n👉 Select a file by number: "))
            if choice == 0:
                return None
            elif 1 <= choice <= len(files):
                return files[choice - 1]
            else:
                print("❌ Invalid number.")
        except ValueError:
            print("❌ Please enter a valid number.")

def show_diff(before, after):
    print("\n🔍 Diff (Original → Updated):\n" + "-" * 40)
    diff = difflib.unified_diff(
        before.splitlines(),
        after.splitlines(),
        lineterm="",
        fromfile="original",
        tofile="updated"
    )
    for line in diff:
        print(line)
    print("-" * 40)

def backup_file(path, content):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = os.path.basename(path)
    backup_path = os.path.join(BACKUP_DIR, f"{timestamp}_{name}")
    with open(backup_path, "w") as f:
        f.write(content)
    print(f"🛡️  Backup saved to: {backup_path}")
    return backup_path

def log_update(filename, instruction, backup_path):
    with open(LOG_FILE, "a") as log:
        timestamp = datetime.datetime.now().isoformat()
        log.write(f"[{timestamp}] Updated {filename} based on instruction: '{instruction}'\n")
        log.write(f"Backup: {backup_path}\n\n")

def main():
    python_files = list_python_files()
    if not python_files:
        print("No Python files found.")
        return

    selected_file = select_file(python_files)
    if not selected_file:
        print("Operation cancelled.")
        return

    with open(selected_file, "r") as f:
        current_code = f.read()

    instruction = input("💬 What should I change or add in the code?\n> ")

    llm = LLM()
    updated_code = llm.apply_suggestion(current_code, instruction)

    show_diff(current_code, updated_code)

    confirm = input("\n💾 Overwrite original file with updated code? (y/n): ")
    if confirm.lower() == "y":
        backup_path = backup_file(selected_file, current_code)
        with open(selected_file, "w") as f:
            f.write(updated_code)
        print("✅ File updated.")
        log_update(selected_file, instruction, backup_path)

    run = input("\n🚀 Do you want to run the updated code now? (y/n): ")
    if run.lower() == "y":
        llm.run_code(updated_code)

main()
