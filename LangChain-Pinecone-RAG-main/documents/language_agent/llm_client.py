# language_agent/llm_client.py
import os
from typing import Tuple, List, Dict

# Prefer Groq if available (your earlier code used ChatGroq). Provide OpenAI fallback.
try:
    from langchain_groq import ChatGroq
    HAS_GROQ = True
except Exception:
    HAS_GROQ = False

try:
    import openai
    HAS_OPENAI = True
except Exception:
    HAS_OPENAI = False

class LLMClient:
    def __init__(self):
        # try groq first
        if HAS_GROQ and os.getenv("GROQ_API_KEY"):
            self.backend = "groq"
            self.model = os.getenv("GROQ_MODEL", "llama3-70b-8192")
            self.client = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model=self.model, temperature=0.2)
        elif HAS_OPENAI and os.getenv("OPENAI_API_KEY"):
            self.backend = "openai"
            openai.api_key = os.getenv("OPENAI_API_KEY")
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o")  # or gpt-4o-mini, etc.
            self.client = openai
        else:
            raise RuntimeError("No LLM backend configured (set GROQ_API_KEY or OPENAI_API_KEY)")

    def generate(self, prompt: str, return_provenance: bool = True) -> Tuple[str, List[Dict]]:
        if self.backend == "groq":
            # ChatGroq expects messages list (langchain_core.messages)
            from langchain_core.messages import SystemMessage
            message = SystemMessage(prompt)
            res = self.client.invoke([message])
            text = res.content if hasattr(res, "content") else str(res)
            # Groq wrapper may not return provenance — build simple provenance stub
            provenance = [{"title": "local_docs_and_web", "confidence": 0.9}]
            return text, provenance
        else:
            # OpenAI completion
            resp = self.client.ChatCompletion.create(
                model=self.model,
                messages=[{"role":"system","content":prompt}],
                temperature=0.2,
                max_tokens=800
            )
            text = resp["choices"][0]["message"]["content"]
            provenance = [{"title": "openai_generated", "confidence": 0.9}]
            return text, provenance
