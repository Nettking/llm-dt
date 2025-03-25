from llm import LLM  # assuming LLM class is in llm.py

if __name__ == "__main__":
    purpose = input("📝 What is the purpose of this script?\n> ")
    llm = LLM()
    llm.evolve_script(purpose)
