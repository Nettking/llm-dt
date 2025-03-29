import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.ollama import Ollama
from llm import LLM


def find_docs_folder(start_path="."):
    for root, dirs, _ in os.walk(start_path):
        if "docs" in dirs:
            return os.path.join(root, "docs")
    return None


def main():
    # Step 1: Locate the 'docs' folder anywhere in the project
    docs_path = find_docs_folder(os.path.dirname(__file__))

    if not docs_path or not os.path.exists(docs_path):
        print("❌ Could not find a 'docs' folder anywhere in the project.")
        return

    print(f"📄 Found and loading documents from: {docs_path}")
    documents = SimpleDirectoryReader(docs_path).load_data()

    # Step 2: Use your custom LLM wrapper to select or set a model
    core_llm = LLM()

    # Step 3: Wrap it with llama-index's Ollama-compatible interface
    index_llm = Ollama(model=core_llm.model)

    # Step 4: Build the vector index
    print("🔍 Building index...")
    index = VectorStoreIndex.from_documents(documents, embed_model="local")

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
