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
        """Retrieve relevant context from vector store with fallback"""
        clean_query = self.sanitize_input(query)
        
        # Try with strict threshold first
        retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": self.retriever_k, "score_threshold": self.retriever_score_threshold}
        )
        
        try:
            docs = retriever.invoke(clean_query)
        except Exception as e:
            print(f"Error with strict threshold: {e}")
            docs = []
        
        # If no docs found, try with lower threshold
        if not docs:
            try:
                retriever_fallback = self.vector_store.as_retriever(
                    search_type="similarity_score_threshold",
                    search_kwargs={"k": self.retriever_k, "score_threshold": 0.3}
                )
                docs = retriever_fallback.invoke(clean_query)
            except Exception as e:
                print(f"Error with fallback threshold: {e}")
                docs = []
        
        # If still no docs, try simple similarity search
        if not docs:
            try:
                retriever_simple = self.vector_store.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": self.retriever_k}
                )
                docs = retriever_simple.invoke(clean_query)
            except Exception as e:
                print(f"Error with simple search: {e}")
                docs = []
        
        sources: List[str] = []
        for d in docs or []:
            meta = getattr(d, "metadata", {}) or {}
            src = meta.get("source") or meta.get("file_path") or meta.get("path") or "unknown"
            if src not in sources:
                sources.append(src)
        
        return {"docs": docs or [], "sources": sources, "retrieved_from": "docs"}
    
    def web_search(self, query: str) -> str:
        """Perform web search for additional context with enhanced queries"""
        if not self.web_search_tool:
            return ""
        
        try:
            # Enhanced web search with more specific queries
            enhanced_query = self._enhance_search_query(query)
            return self.web_search_tool.run(enhanced_query)
        except Exception as e:
            print(f"Web search error: {e}")
            return ""
    
    def _enhance_search_query(self, query: str) -> str:
        """Enhance search query for better web search results"""
        # Add context-specific terms based on agent type
        if self.agent_name.lower() == "culture":
            return f"{query} cultural traditions customs etiquette"
        elif self.agent_name.lower() == "activity":
            return f"{query} attractions activities things to do tourist"
        elif self.agent_name.lower() == "food":
            return f"{query} restaurants food dining cuisine local"
        elif self.agent_name.lower() == "language":
            return f"{query} phrases language translation communication"
        else:
            return query
    
    def generate_response(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None,
        collaboration_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate response using LLM with enhanced collaboration support"""
        
        # Build context
        local_context = ""
        sources = []
        web_context = ""
        
        if context:
            docs = context.get("docs", [])
            local_context = "\n\n".join(getattr(d, "page_content", "") for d in docs)[:4000]
            sources = context.get("sources", [])
        
        # Use web search if local context is limited
        if not local_context or len(local_context) < 500:
            print(f"🔍 Limited local context, using web search for {self.agent_name} agent...")
            web_context = self.web_search(query)
            if web_context:
                sources.append("Web Search Results")
        
        # Enhanced system prompt for collaboration
        enhanced_system_prompt = self.system_prompt
        if collaboration_context:
            enhanced_system_prompt += f"""

IMPORTANT: You are collaborating with other specialized agents. Consider the following context from other agents:
{collaboration_context}

When responding:
- Build upon insights from other agents when relevant
- Avoid duplicating information already provided by other agents
- Focus on your specialized expertise while acknowledging other perspectives
- If other agents have covered aspects of your expertise, provide additional depth or different angles
- Ensure your response complements rather than conflicts with other agents' responses
- For itinerary queries: provide specific, actionable recommendations that work well with other agents' suggestions
- Include practical details like timing, location, and cultural context
- Make your response specific to the destination mentioned in the query
"""
        
        # Add fallback guidance when no local context is available
        if not local_context:
            enhanced_system_prompt += f"""

NOTE: No specific local knowledge was found in the knowledge base. Please provide general expert advice based on your specialized knowledge in {self.agent_name.lower()}. 
Use your training knowledge to provide helpful, accurate information while being clear that this is general guidance.
"""
        
        # Build prompt
        prompt_parts = [f"User query: {query}"]
        
        if local_context:
            prompt_parts.append(f"Local knowledge:\n{local_context}")
        
        if web_context:
            prompt_parts.append(f"Web search results:\n{web_context[:2000]}")
        
        if not local_context and not web_context:
            prompt_parts.append("No specific knowledge available - provide general expert guidance based on your training")
        
        prompt = "\n\n".join(prompt_parts)
        
        # Generate response
        try:
            system_msg = SystemMessage(content=enhanced_system_prompt)
            human_msg = HumanMessage(content=prompt)
            response = self.llm.invoke([system_msg, human_msg]).content
        except Exception as e:
            # Fallback response if LLM fails
            response = self._get_fallback_response(query)
        
        # Calculate confidence based on context and collaboration
        confidence = 0.6  # Base confidence
        if local_context:
            confidence += 0.2  # Higher confidence with local knowledge
        if collaboration_context:
            confidence += 0.1  # Slight boost for collaboration context
        
        return {
            "agent": self.agent_name,
            "response": response.strip(),
            "sources": sources,
            "confidence": min(confidence, 0.95)  # Cap at 95%
        }
    
    def _get_fallback_response(self, query: str) -> str:
        """Provide fallback response when LLM fails"""
        if self.agent_name.lower() == "culture":
            return f"I'd be happy to help with cultural information about your destination. While I don't have specific local knowledge in my database, I can provide general cultural guidance. Could you please specify which destination you're interested in?"
        elif self.agent_name.lower() == "activity":
            return f"I can help you find activities and attractions. To provide the best recommendations, could you tell me which destination you're planning to visit?"
        elif self.agent_name.lower() == "food":
            return f"I'd love to help with food recommendations! To give you the best dining suggestions, could you specify which city or region you're interested in?"
        elif self.agent_name.lower() == "language":
            return f"I can help with language assistance and essential phrases. Which destination are you planning to visit so I can provide relevant language guidance?"
        else:
            return f"I'm here to help with {self.agent_name.lower()} guidance. Could you please specify your destination so I can provide more targeted assistance?"
    
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
