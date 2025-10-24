"""
Base Agent Class for Multi-Agent Travel System
Provides common functionality for all specialized agents
"""

import os
import re
from typing import Any, Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
from dotenv import load_dotenv

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

try:
    from langchain_community.tools import DuckDuckGoSearchRun
except Exception:
    DuckDuckGoSearchRun = None

load_dotenv()


class BaseAgent(ABC):
    """Base class for all travel agents"""
    
    def __init__(
        self,
        agent_name: str,
        pinecone_api_key: Optional[str] = None,
        pinecone_index_name: Optional[str] = None,
        groq_api_key: Optional[str] = None,
        groq_model: str = "llama-3.3-70b-versatile",
        retriever_k: int = 5,
        retriever_score_threshold: float = 0.5,
    ):
        self.agent_name = agent_name
        self.pinecone_api_key = pinecone_api_key or os.environ.get("PINECONE_API_KEY")
        self.pinecone_index_name = pinecone_index_name or os.environ.get("PINECONE_INDEX_NAME")
        self.groq_api_key = groq_api_key or os.environ.get("GROQ_API_KEY")
        self.groq_model = groq_model
        self.retriever_k = retriever_k
        self.retriever_score_threshold = retriever_score_threshold
        
        # Initialize components
        self._setup_components()
        
        # Agent-specific keywords and capabilities
        self.keywords = self._get_keywords()
        self.system_prompt = self._get_system_prompt()
    
    def _setup_components(self):
        """Initialize Pinecone, embeddings, and LLM"""
        try:
            pc = Pinecone(api_key=self.pinecone_api_key)
            index = pc.Index(self.pinecone_index_name)
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            self.vector_store = PineconeVectorStore(index=index, embedding=embeddings)
            self.llm = ChatGroq(api_key=self.groq_api_key, model=self.groq_model, temperature=0.3)
            self.web_search_tool = DuckDuckGoSearchRun() if DuckDuckGoSearchRun else None
        except Exception as e:
            raise Exception(f"Failed to initialize {self.agent_name}: {e}")
    
    @abstractmethod
    def _get_keywords(self) -> List[str]:
        """Return keywords this agent handles"""
        pass
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Return system prompt for this agent"""
        pass
    
    def sanitize_input(self, text: str) -> str:
        """Clean and limit input text"""
        cleaned = re.sub(r"\s+", " ", text.strip())
        return cleaned[:2000]
    
    def extract_destination(self, text: str) -> Optional[str]:
        """Extract destination from user query"""
        patterns = [
            r"in\s+([A-Z][A-Za-z\-\s]+)$",
            r"to\s+([A-Z][A-Za-z\-\s]+)$",
            r"at\s+([A-Z][A-Za-z\-\s]+)$",
            r"(?:go(?:ing)?\s+to|visit(?:ing)?)\s+([A-Z][A-Za-z\-\s]+)",
        ]
        text_stripped = text.strip()
        for pat in patterns:
            m = re.search(pat, text_stripped, flags=re.IGNORECASE)
            if m:
                dest = m.group(1).strip(" .!?,")
                return dest
        
        # Fallback: look for last capitalized token sequence
        tokens = re.findall(r"[A-Z][A-Za-z\-]+(?:\s+[A-Z][A-Za-z\-]+)*", text_stripped)
        if tokens:
            return tokens[-1]
        return None
    
    def is_relevant_query(self, query: str) -> bool:
        """Check if query is relevant to this agent"""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.keywords)
    
    def retrieve_context(self, query: str) -> Dict[str, Any]:
        """Retrieve relevant context from vector store"""
        clean_query = self.sanitize_input(query)
        retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": self.retriever_k, "score_threshold": self.retriever_score_threshold}
        )
        
        try:
            docs = retriever.invoke(clean_query)
        except Exception:
            docs = []
        
        sources: List[str] = []
        for d in docs or []:
            meta = getattr(d, "metadata", {}) or {}
            src = meta.get("source") or meta.get("file_path") or meta.get("path") or "unknown"
            if src not in sources:
                sources.append(src)
        
        return {"docs": docs or [], "sources": sources, "retrieved_from": "docs"}
    
    def web_search(self, query: str) -> str:
        """Perform web search for additional context"""
        if not self.web_search_tool:
            return ""
        
        try:
            return self.web_search_tool.run(query)
        except Exception:
            return ""
    
    def generate_response(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None,
        collaboration_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate response using LLM"""
        
        # Build context
        local_context = ""
        sources = []
        
        if context:
            docs = context.get("docs", [])
            local_context = "\n\n".join(getattr(d, "page_content", "") for d in docs)[:4000]
            sources = context.get("sources", [])
        
        # Build prompt
        prompt_parts = [f"User query: {query}"]
        
        if local_context:
            prompt_parts.append(f"Local knowledge:\n{local_context}")
        
        if collaboration_context:
            prompt_parts.append(f"Collaboration context from other agents:\n{collaboration_context}")
        
        prompt = "\n\n".join(prompt_parts)
        
        # Generate response
        try:
            system_msg = SystemMessage(content=self.system_prompt)
            human_msg = HumanMessage(content=prompt)
            response = self.llm.invoke([system_msg, human_msg]).content
        except Exception as e:
            response = f"I'm sorry, I couldn't generate a proper response. Error: {e}"
        
        return {
            "agent": self.agent_name,
            "response": response.strip(),
            "sources": sources,
            "confidence": 0.8 if local_context else 0.6
        }
    
    def process_query(
        self, 
        query: str, 
        collaboration_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Main method to process a query"""
        
        # Check if query is relevant
        if not self.is_relevant_query(query):
            return {
                "agent": self.agent_name,
                "response": f"This query is not relevant to my expertise in {self.agent_name.lower()}.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Retrieve context
        context = self.retrieve_context(query)
        
        # Generate response
        return self.generate_response(query, context, collaboration_context)
