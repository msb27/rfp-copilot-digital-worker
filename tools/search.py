# tools/search.py
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import os

# Load environment variables from .env
load_dotenv()

# Load vectorstore
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
db = FAISS.load_local("rag/vectorstore", embeddings, allow_dangerous_deserialization=True)


@tool
def search_knowledge(query: str) -> str:
    """
    Search past proposals and compliance rules  for relevant content.
    Use for grounding responses in real data and regulations.
    """
    retriever = db.as_retriever(search_kwargs={"k": 5})
    docs = retriever.invoke(query)

    results = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        category = doc.metadata.get("category", "unknown")
        snippet = doc.page_content[:500]
        results.append(f"[{source} | {category}]\n{snippet}\n")

    return "\n---\n".join(results) if results else "No relevant knowledge found."