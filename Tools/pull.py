from llm import LLM

if __name__ == "__main__":
    MODEL = input("Modell name to pull: ")
    llm = LLM()
    llm.pull_model(MODEL)
