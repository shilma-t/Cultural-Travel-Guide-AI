import os
import re
from typing import Any, Dict, List, Optional

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

class CultureAgent:
    def __init__(
        self,
        pinecone_api_key: Optional[str] = None,
        pinecone_index_name: Optional[str] = None,
        groq_api_key: Optional[str] = None,
        groq_model: str = "llama-3.3-70b-versatile",
        retriever_k: int = 5,
        retriever_score_threshold: float = 0.5,
    ):
        self.pinecone_api_key = pinecone_api_key or os.environ.get("PINECONE_API_KEY")
        self.pinecone_index_name = pinecone_index_name or os.environ.get("PINECONE_INDEX_NAME")
        self.groq_api_key = groq_api_key or os.environ.get("GROQ_API_KEY")
        self.groq_model = groq_model
        self.retriever_k = retriever_k
        self.retriever_score_threshold = retriever_score_threshold

        pc = Pinecone(api_key=self.pinecone_api_key)
        index = pc.Index(self.pinecone_index_name)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.vector_store = PineconeVectorStore(index=index, embedding=embeddings)
        self.llm = ChatGroq(api_key=self.groq_api_key, model=self.groq_model, temperature=0.3)
        self.web_search_tool = DuckDuckGoSearchRun() if DuckDuckGoSearchRun else None

        # Keywords to detect culturally relevant queries
        self.allowed_keywords = [
            "culture", "tradition", "customs", "etiquette", "ceremony",
            "festival", "heritage", "cultural", "travel", "wedding",
            "ritual", "local", "regional"
        ]
        # Commands allowed in context
        self.context_commands = ["summarize", "elaborate", "explain", "clarify", "hi", "hello", "hey"]

    def sanitize_input(self, text: str) -> str:
        cleaned = re.sub(r"\s+", " ", text.strip())
        return cleaned[:2000]

    def retrieve_context(self, query: str) -> Dict[str, Any]:
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

    def generate_answer(self, query: str, previous_answer: Optional[str] = None) -> Dict[str, Any]:
        query_lower = query.lower()
        is_context_command = previous_answer and any(cmd in query_lower for cmd in self.context_commands)
        is_cultural = any(keyword in query_lower for keyword in self.allowed_keywords)

        # --- Step 1: Context commands (summarize/elaborate/greetings) ---
        if is_context_command and previous_answer:
            prompt = f"Use the previous answer as context and respond accordingly:\n{previous_answer}\nUser query: {query}"
        # --- Step 2: New culturally relevant topic (topic switching) ---
        elif is_cultural:
            previous_answer = None  # reset previous context for new topic
            context = self.retrieve_context(query)
            docs = context["docs"]
            sources = context["sources"]
            retrieved_from = context["retrieved_from"]
            local_context = "\n\n".join(getattr(d, "page_content", "") for d in docs)[:6000]
            prompt = f"User query: {query}\nContext:\n{local_context}\nAnswer strictly on cultural topics, avoid bias."
        # --- Step 3: Off-topic queries ---
        else:
            return {
                "answer": "I'm sorry, I can only answer questions related to culture, traditions, and travel guidance.",
                "sources": [],
                "retrieved_from": None
            }

        # --- Step 4: System instructions ---
        system_msg = SystemMessage(content="""
You are CultureAgent, a cultural travel guide.
- Only answer questions about culture, traditions, etiquette, festivals, and travel guidance.
- Do not provide information outside cultural context unless elaborating on previous answer.
- Avoid biased, stereotypical, or offensive statements.
- Politely refuse if question is off-topic and there is no prior cultural context.
- Summarize, clarify, or elaborate only based on prior answers.
- Respond to greetings in a culturally aware manner.
- Cite sources if retrieved from web or documents.
""")

        # --- Step 5: Generate answer using LLM ---
        try:
            answer = self.llm.invoke([system_msg, HumanMessage(content=prompt)]).content
        except Exception:
            answer = "I'm sorry, I couldn't generate a proper answer."

        # --- Step 6: Optional web fallback for new cultural topics ---
        if (not previous_answer or not is_context_command) and self.web_search_tool:
            try:
                web_result = self.web_search_tool.run(query)
                sources.append("web")
                answer = self.llm.invoke([
                    system_msg,
                    HumanMessage(content=f"Query: {query}\nWeb info: {web_result}\nStay strictly on cultural topics.")
                ]).content
                retrieved_from = "web"
            except Exception:
                pass

        return {
            "answer": answer.strip(),
            "sources": sources if 'retrieved_from' in locals() and retrieved_from == "web" else [],
            "retrieved_from": retrieved_from if 'retrieved_from' in locals() else None
        }
