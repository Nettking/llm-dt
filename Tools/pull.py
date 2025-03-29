from llm import LLM

if __name__ == "__main__":
    llm = LLM()
    llm.list_available_models()
    MODEL = input("Modell name to pull: ")
    llm.pull_model(MODEL)
