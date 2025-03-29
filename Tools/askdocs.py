import os
import requests
from typing import List
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.ollama import Ollama
from llama_index.core.embeddings.base import BaseEmbedding
from llm import LLM


class CustomOllamaEmbedding(BaseEmbedding):
    def __init__(self, model_name="nomic-embed-text", host="http://localhost:11434"):
        self.model_name = model_name
        self.host = host

    def _embed(self, texts: List[str]) -> List[List[float]]:
        results = []
        for text in texts:
            response = requests.post(
                f"{self.host}/api/embeddings",
                json={"model": self.model_name, "prompt": text}
            )
            response.raise_for_status()
            embedding = response.json()["embedding"]
            results.append(embedding)
        return results

    def embed(self, texts: List[str]) -> List[List[float]]:
        return self._embed(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embed([text])[0]


def find_docs_folder(start_path="."):
    for root, dirs, _ in os.walk(start_path):
        if "docs" in dirs:
            return os.path.join(root, "docs")
    return None


def main():
    docs_path = find_docs_folder(os.path.dirname(__file__))

    if not docs_path or not os.path.exists(docs_path):
        print("❌ Could not find a 'docs' folder anywhere in the project.")
        return

    print(f"📄 Found and loading documents from: {docs_path}")
    documents = SimpleDirectoryReader(docs_path).load_data()

    # Step 2: Use your custom LLM wrapper to select or set a model
    core_llm = LLM()
    index_llm = Ollama(model=core_llm.model)

    # Step 3: Use CustomOllamaEmbedding for embedding
    embed_model = CustomOllamaEmbedding(model_name="nomic-embed-text")

    # Step 4: Build the vector index
    print("🔍 Building index...")
    index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)

    # Step 5: Create a query engine
    query_engine = index.as_query_engine(llm=index_llm)

    # Step 6: Interactive Q&A loop
    print("\n✅ Ready! Ask about your documents.")
    while True:
        query = input("\n❓ Ask a question (or type 'exit'): ")
        if query.lower() in {"exit", "quit"}:
            break
        response = query_engine.query(query)
        print("\n🤖 Answer:")
        print(response)


if __name__ == "__main__":
    main()
