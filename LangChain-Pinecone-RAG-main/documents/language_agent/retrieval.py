# language_agent/retrieval.py
import os
from dotenv import load_dotenv
load_dotenv()

from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings

# type hints
from typing import List
from langchain_core.documents import Document

# NOTE: this matches your ingestion — it expects the Pinecone index already created & populated.

class VectorRetrieval:
    def __init__(self):
        api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX_NAME")
        if not api_key or not index_name:
            raise RuntimeError("PINECONE_API_KEY and PINECONE_INDEX_NAME must be set in env")

        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vs = PineconeVectorStore(index=self.index, embedding=self.embeddings)

    def retrieve(self, query: str, top_k: int = 4, score_threshold: float = 0.4) -> List[Document]:
        # as_retriever uses your provider wrapper — remain compatible with earlier code
        retriever = self.vs.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": top_k, "score_threshold": score_threshold},
        )
        # retriever.invoke returns a list of Documents in your previous code; keep same
        docs = retriever.invoke(query)
        return docs or []
