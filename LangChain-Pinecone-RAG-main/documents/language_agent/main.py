# language_agent/main.py
from fastapi import FastAPI, HTTPException, Request, Header, Depends
from pydantic import BaseModel
import uuid, os, datetime
from typing import Optional, Dict, Any, List

from retrieval import VectorRetrieval
from nlp import analyze_intent_entities, translate_text_if_needed
from llm_client import LLMClient
from safety import safety_check
from utils import build_rag_prompt, log_interaction

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("LANG_AGENT_API_KEY", "dev-api-key")  # simple api-key auth for demo

app = FastAPI(title="Language Agent - Culture Travel Guide", version="0.1")

# init components (singletons)
retriever = VectorRetrieval()         # wraps Pinecone + embeddings (uses your existing index)
llm = LLMClient()                     # ChatGroq preferred, OpenAI fallback


# ---------- Request / Response models ----------
class Payload(BaseModel):
    user_text: str
    user_locale: Optional[str] = "en-US"
    user_lang: Optional[str] = "en"
    context: Optional[Dict[str, Any]] = {}

class AgentRequest(BaseModel):
    session_id: str
    from_agent: str
    to_agent: str
    message_id: str
    timestamp: str
    payload: Payload

class AgentResponse(BaseModel):
    message_id: str
    in_reply_to: str
    payload: Dict[str, Any]


# ---------- Simple API Key Dependency ----------
def check_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="Missing API key")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return True


# ---------- Main message endpoint ----------
@app.post("/message", response_model=AgentResponse, dependencies=[Depends(check_api_key)])
async def handle_message(req: AgentRequest):
    # 1. basic metadata
    session_id = req.session_id or str(uuid.uuid4())
    in_msg_id = req.message_id
    user_text = req.payload.user_text
    user_lang = req.payload.user_lang or "en"
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"

    # 2. safety check (early)
    safe_result = safety_check(user_text)
    if not safe_result["allow"]:
        # log and return refusal with safe fallback
        log_interaction(session_id, in_msg_id, user_text, intent=None, entities=None,
                        retrieved_docs=[], answer="REFUSED BY SAFETY", provenance=[])
        return AgentResponse(
            message_id=str(uuid.uuid4()),
            in_reply_to=in_msg_id,
            payload={
                "reply_text": safe_result.get("message", "I can't assist with that request."),
                "metadata": {"safety": safe_result}
            }
        )

    # 3. intent & NER
    intent, entities = analyze_intent_entities(user_text, user_lang)

    # 4. retrieval from Pinecone vector store (RAG)
    docs = retriever.retrieve(user_text, top_k=4, score_threshold=0.45)
    retrieved_text = [d.page_content for d in docs] if docs else []

    # 5. Build prompt for LLM (includes provenance, doc excerpts)
    prompt = build_rag_prompt(user_text=user_text,
                              intent=intent,
                              entities=entities,
                              retrieved_docs=retrieved_text,
                              user_locale=req.payload.user_locale,
                              user_lang=user_lang,
                              context=req.payload.context)

    # 6. Call LLM
    try:
        llm_result, provenance = llm.generate(prompt, return_provenance=True)
    except Exception as e:
        # fallback error response
        raise HTTPException(status_code=500, detail=f"LLM call failed: {e}")

    # 7. Post-process: optional translation to user's language
    final_answer = translate_text_if_needed(llm_result, target_lang=user_lang)

    # 8. Log interaction (explainability)
    log_interaction(session_id, in_msg_id, user_text, intent, entities, retrieved_text, final_answer, provenance)

    # 9. Compose response including sources + actions
    response_payload = {
        "reply_text": final_answer,
        "sources": provenance,
        "metadata": {
            "intent": intent,
            "entities": entities,
            "safety": safe_result
        },
        "actions": [
            {"type": "ask_followup", "text": "Would you like more details, a translated phrase, or an itinerary suggestion?"}
        ]
    }
    return AgentResponse(message_id=str(uuid.uuid4()), in_reply_to=in_msg_id, payload=response_payload)


@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.datetime.utcnow().isoformat()}

