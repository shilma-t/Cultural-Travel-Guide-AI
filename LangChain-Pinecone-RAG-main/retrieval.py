# import basics
import os
from dotenv import load_dotenv

# import pinecone
from pinecone import Pinecone, ServerlessSpec

# import langchain
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings  # Updated to match ingestion
from langchain_core.documents import Document

load_dotenv()

# Validate environment variables
if not os.environ.get("PINECONE_API_KEY"):
    raise ValueError("PINECONE_API_KEY environment variable is required")

print("🔑 Pinecone API key loaded successfully")

# initialize pinecone database
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# set the pinecone index
index_name = os.environ.get("PINECONE_INDEX_NAME", "sample-index")  # Default fallback
index = pc.Index(index_name)

# initialize embeddings model + vector store
print("🤗 Loading HuggingFace embeddings model...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
print("✅ Embeddings model loaded successfully")

vector_store = PineconeVectorStore(index=index, embedding=embeddings)

# retrieval
print("🔍 Testing retrieval with HuggingFace embeddings...")
retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 5, "score_threshold": 0.5},
)
results = retriever.invoke("what is retrieval augmented generation?")

# show results
print("RESULTS:")

for res in results:
    print(f"* {res.page_content} [{res.metadata}]")