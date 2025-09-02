# import basics
import os
import time
from dotenv import load_dotenv

# import pinecone
from pinecone import Pinecone, ServerlessSpec

# import langchain
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# documents
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.document_loaders import PyPDFLoader

load_dotenv() 

# initialize pinecone client
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# initialize pinecone database
index_name = os.environ.get("PINECONE_INDEX_NAME")  # change if desired

# check whether index exists, and create if not
existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

if index_name not in existing_indexes:
    pc.create_index(
        name=index_name,
        dimension=384,   
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)

index = pc.Index(index_name)

# initialize embeddings model + vector store (Hugging Face)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vector_store = PineconeVectorStore(index=index, embedding=embeddings)

# loading the PDF document
print("📚 Loading PDF documents from documents/ directory...")
try:
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    documents_dir = os.path.join(script_dir, "documents")
    
    print(f"📁 Script directory: {script_dir}")
    print(f"📁 Documents directory: {documents_dir}")
    
    # List all PDF files in the documents directory
    pdf_files = [f for f in os.listdir(documents_dir) if f.endswith('.pdf')]
    print(f"📁 Found PDF files: {pdf_files}")
    
    if not pdf_files:
        raise ValueError("No PDF files found in documents/ directory")
    
    raw_documents = []
    for pdf_file in pdf_files:
        pdf_path = os.path.join(documents_dir, pdf_file)
        print(f"📖 Loading: {pdf_file}")
        loader = PyPDFLoader(pdf_path)
        documents_from_file = loader.load()
        raw_documents.extend(documents_from_file)
        print(f"✅ Loaded {len(documents_from_file)} pages from {pdf_file}")
    
    print(f"✅ Total raw documents loaded: {len(raw_documents)}")
    
except Exception as e:
    print(f"❌ Error loading documents: {e}")
    raise

# splitting the document
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=400,
    length_function=len,
    is_separator_regex=False,
)

# creating the chunks
documents = text_splitter.split_documents(raw_documents)

# generate unique ids
uuids = [f"id{i}" for i in range(len(documents))]

# add to database
vector_store.add_documents(documents=documents, ids=uuids)
