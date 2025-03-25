from llm import LLM

llm = LLM()

try:
    result = 1 / 0
except Exception as e:
    llm.explain_exception(e)
