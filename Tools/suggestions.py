import os
from llm import LLM

FILE_TO_EDIT = "my_script.py"

def main():
    if not os.path.exists(FILE_TO_EDIT):
        print(f"❌ File not found: {FILE_TO_EDIT}")
        return

    with open(FILE_TO_EDIT, "r") as f:
        current_code = f.read()

    llm = LLM()
    suggestions = llm.get_suggestions(current_code)

    if not suggestions:
        print("🤔 No suggestions received.")
        return

    print("\n💡 Suggested improvements:")
    for i, s in enumerate(suggestions, 1):
        print(f"{i}. {s}")

    choice = input("\n👉 Choose a suggestion (1-3), or type 'n' to cancel: ")
    if choice.lower() == 'n':
        return

    try:
        selected = suggestions[int(choice) - 1]
    except (ValueError, IndexError):
        print("⚠️ Invalid choice.")
        return

    updated_code = llm.apply_suggestion(current_code, selected)

    confirm = input("\n💾 Overwrite original file with updated code? (y/n): ")
    if confirm.lower() == "y":
        with open(FILE_TO_EDIT, "w") as f:
            f.write(updated_code)

    run = input("\n🚀 Run the updated code? (y/n): ")
    if run.lower() == "y":
        llm.run_code(updated_code)

if __name__ == "__main__":
    main()
