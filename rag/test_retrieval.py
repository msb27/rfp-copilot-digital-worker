# test_retrieval.py
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# Load environment variables from .env
load_dotenv()

embeddings = OpenAIEmbeddings()
db = FAISS.load_local("rag/vectorstore", embeddings, allow_dangerous_deserialization=True)
retriever = db.as_retriever(search_kwargs={"k": 3})

docs = retriever.invoke("What are Veeva guidelines?")
for d in docs:
    print(f"[{d.metadata['source']}] {d.page_content[:200]}...\n")