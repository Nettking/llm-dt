from llm import LLM

if __name__ == "__main__":
    user_input = input("You: ")
    llm = LLM()
    print("Ollama: " + llm._chat(user_input))
