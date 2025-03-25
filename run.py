import os
import subprocess

def find_python_scripts(base_dir):
    scripts = []
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if (
                file.endswith(".py")
                and not file.startswith("__")
                and file != "run.py"  # Exclude run.py here
            ):
                full_path = os.path.join(root, file)
                scripts.append(full_path)
    return scripts

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def main():
    base_dir = "."  # Start from current directory

    while True:
        clear_screen()
        print("📜 Available Python Programs:\n")

        scripts = find_python_scripts(base_dir)
        if not scripts:
            print("No Python scripts found.")
            return

        for i, path in enumerate(scripts, 1):
            display_path = os.path.relpath(path, base_dir)
            print(f"{i}. {display_path}")

        print("\n0. Exit")

        try:
            choice = int(input("\nSelect a script to run: "))
            if choice == 0:
                print("Goodbye!")
                break
            elif 1 <= choice <= len(scripts):
                selected = scripts[choice - 1]
                print(f"\n▶️ Running: {selected}\n")
                subprocess.run(["python3", selected])
                input("\n✅ Finished. Press Enter to return to the menu...")
            else:
                print("Invalid choice.")
        except ValueError:
            print("Please enter a valid number.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
