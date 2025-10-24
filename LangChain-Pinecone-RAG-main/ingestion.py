# ingestion.py

import os
import time
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# LangChain imports
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

# -------------------- Pinecone Setup --------------------
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
index_name = os.environ.get("PINECONE_INDEX_NAME")

existing_indexes = [idx["name"] for idx in pc.list_indexes()]
if index_name not in existing_indexes:
    print(f"Creating Pinecone index '{index_name}'...")
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    # Wait until ready
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)

index = pc.Index(index_name)

# -------------------- Embeddings --------------------
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = PineconeVectorStore(index=index, embedding=embeddings)

# -------------------- Load PDFs --------------------
documents_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "documents")
pdf_files = [f for f in os.listdir(documents_dir) if f.endswith(".pdf")]

if not pdf_files:
    raise ValueError("No PDF files found in the documents/ directory")

raw_documents = []
for pdf_file in pdf_files:
    pdf_path = os.path.join(documents_dir, pdf_file)
    print(f"Loading {pdf_file}...")
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    for d in docs:
        # attach source metadata
        d.metadata["source"] = pdf_file
    raw_documents.extend(docs)
print(f"✅ Loaded {len(raw_documents)} pages from {len(pdf_files)} PDF files")

# -------------------- Split Documents --------------------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=400,
    length_function=len,
)
documents = text_splitter.split_documents(raw_documents)
print(f"✅ Split into {len(documents)} chunks")

# -------------------- Add to Pinecone --------------------
uuids = [f"id{i}" for i in range(len(documents))]
vector_store.add_documents(documents=documents, ids=uuids)
print(f"✅ Added {len(documents)} chunks to Pinecone index '{index_name}'")
