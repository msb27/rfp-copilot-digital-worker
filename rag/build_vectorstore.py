# rag/build_vectorstore.py
import os
from dotenv import load_dotenv
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
from pathlib import Path

# Load environment variables from .env
load_dotenv()

# === CONFIG ===
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
VECTORSTORE_PATH = "rag/vectorstore"

# === LOAD ALL DOCS WITH METADATA ===
def load_knowledge_base():
    docs = []
    knowledge_dir = Path("knowledge")

    for file_path in knowledge_dir.rglob("*.txt"):
        loader = TextLoader(str(file_path), encoding="utf-8")
        raw_docs = loader.load()

        # Extract metadata
        category = file_path.parent.name
        source = file_path.name

        for doc in raw_docs:
            doc.metadata.update({
                "source": source,
                "category": category,
                "file_path": str(file_path)
            })
        docs.extend(raw_docs)

    return docs

# === BUILD VECTORSTORE ===
def build_faiss_index():
    print("Loading documents...")
    docs = load_knowledge_base()

    print(f"Loaded {len(docs)} documents. Splitting...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    splits = text_splitter.split_documents(docs)
    print(f"Created {len(splits)} chunks.")

    print("Embedding with OpenAI...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    print("Building FAISS index...")
    vectorstore = FAISS.from_documents(splits, embeddings)

    # Save
    os.makedirs(VECTORSTORE_PATH, exist_ok=True)
    vectorstore.save_local(VECTORSTORE_PATH)
    print(f"Vectorstore saved to {VECTORSTORE_PATH}")

if __name__ == "__main__":
    build_faiss_index()