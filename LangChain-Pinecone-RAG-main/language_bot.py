import os
import re
import time
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# NLP & embeddings
import spacy
from transformers import pipeline, Pipeline
from sentence_transformers import SentenceTransformer

from pinecone import Pinecone

load_dotenv()

# -------------------------
# Configuration and logging
# -------------------------
API_KEY = os.environ.get("sk-langbot-2f93b77f8a1c4e92a7f", "716c8936e30e4289421bb54a0cd1318635f0804994699059fa12989c93821059")  # set a strong key in prod
PINECONE_API_KEY = os.environ.get("pcsk_4CoUJw_FZjTGywY2Q9wn3qenNqhecELEBw55qabN1qiJSY3S2KKsg9Chbogs85t4HWdzh8")
PINECONE_INDEX = os.environ.get("ragmain")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("language_bot")

# -------------------------
# FastAPI app & models
# -------------------------
app = FastAPI(title="Language Agent for Hybrid RAG Chatbot")

class TextRequest(BaseModel):
    text: str
    max_summary_tokens: Optional[int] = 150
    sanitize: Optional[bool] = True

class NERResponse(BaseModel):
    entities: List[Dict[str, Any]]

class SummaryResponse(BaseModel):
    summary: str

class EmbedResponse(BaseModel):
    vector: List[float]

class AgentMessage(BaseModel):
    sender: str
    recipient: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: Optional[float] = None

# -------------------------
# City language models
# -------------------------
class CityRequest(BaseModel):
    city: str

class CityLanguageResponse(BaseModel):
    city: str
    language: str

# -------------------------
# Load models (cached globally)
# -------------------------
try:
    nlp_spacy = spacy.load("en_core_web_sm")
except Exception as e:
    logger.warning("spaCy model not found: en_core_web_sm. Run: python -m spacy download en_core_web_sm")
    raise

summarizer: Pipeline = pipeline("summarization", model=os.environ.get("SUMMARIZATION_MODEL", "facebook/bart-large-cnn"))

embed_model = SentenceTransformer(os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))

pc = None
if PINECONE_API_KEY:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    if PINECONE_INDEX and PINECONE_INDEX not in [i["name"] for i in pc.list_indexes()]:
        logger.info(f"Pinecone index {PINECONE_INDEX} not found. Create it or configure environment correctly.")

# -------------------------
# Utility & security helpers
# -------------------------
MAX_INPUT_LENGTH = int(os.environ.get("LANGUAGE_BOT_MAX_INPUT", 50000))  # characters
SUSPICIOUS_PATTERNS = [
    r"<script.*?>", r"javascript:", r"onerror\s*=", r"onload\s*=",
]
SAFETY_KEYWORDS = {"suicide", "self-harm", "illegal", "bomb", "exploit", "terrorist"}

def check_api_key(x_api_key: Optional[str]):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")

def sanitize_text(text: str) -> str:
    for pat in SUSPICIOUS_PATTERNS:
        text = re.sub(pat, "[removed]", text, flags=re.IGNORECASE|re.DOTALL)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > MAX_INPUT_LENGTH:
        raise HTTPException(status_code=413, detail=f"Input too large ({len(text)} > {MAX_INPUT_LENGTH})")
    return text

def safety_filter(text: str) -> List[str]:
    lowered = text.lower()
    flagged = [kw for kw in SAFETY_KEYWORDS if kw in lowered]
    return flagged

#city language map
CITY_LANG_MAP: Dict[str, str] = {
    "new york": "English",
    "los angeles": "English",
    "chicago": "English",
    "houston": "English",
    "phoenix": "English",
    "philadelphia": "English",
    "san antonio": "English",
    "san diego": "English",
    "dallas": "English",
    "san jose": "English",
    "london": "English",
    "manchester": "English",
    "birmingham": "English",
    "glasgow": "English",
    "liverpool": "English",
    "paris": "French",
    "marseille": "French",
    "lyon": "French",
    "toulouse": "French",
    "nice": "French",
    "berlin": "German",
    "hamburg": "German",
    "munich": "German",
    "cologne": "German",
    "frankfurt": "German",
    "madrid": "Spanish",
    "barcelona": "Spanish",
    "valencia": "Spanish",
    "seville": "Spanish",
    "zaragoza": "Spanish",
    "rome": "Italian",
    "milan": "Italian",
    "naples": "Italian",
    "turin": "Italian",
    "palermo": "Italian",
    "tokyo": "Japanese",
    "osaka": "Japanese",
    "nagoya": "Japanese",
    "sapporo": "Japanese",
    "fukuoka": "Japanese",
    "seoul": "Korean",
    "busan": "Korean",
    "incheon": "Korean",
    "daegu": "Korean",
    "daejeon": "Korean",
    "beijing": "Chinese",
    "shanghai": "Chinese",
    "guangzhou": "Chinese",
    "shenzhen": "Chinese",
    "tianjin": "Chinese",
    "mumbai": "Hindi",
    "delhi": "Hindi",
    "bangalore": "Kannada",
    "hyderabad": "Telugu",
    "ahmedabad": "Gujarati",
    "bangkok": "Thai",
    "chiang mai": "Thai",
    "phuket": "Thai",
    "singapore": "English",
    "dubai": "Arabic",
    "abu dhabi": "Arabic",
    "cairo": "Arabic",
    "alexandria": "Arabic",
    "casablanca": "Arabic",
    "sydney": "English",
    "melbourne": "English",
    "brisbane": "English",
    "perth": "English",
    "adelaide": "English",
    "toronto": "English",
    "vancouver": "English",
    "montreal": "French",
    "calgary": "English",
    "ottawa": "English",
    "rio de janeiro": "Portuguese",
    "sao paulo": "Portuguese",
    "salvador": "Portuguese",
    "brasilia": "Portuguese",
    "fortaleza": "Portuguese",
    "moscow": "Russian",
    "saint petersburg": "Russian",
    "novosibirsk": "Russian",
    "yekaterinburg": "Russian",
    "kazan": "Russian",
    "istanbul": "Turkish",
    "ankara": "Turkish",
    "izmir": "Turkish",
    "bursa": "Turkish",
    "antalya": "Turkish",
    "jakarta": "Indonesian",
    "surabaya": "Indonesian",
    "bandung": "Indonesian",
    "medan": "Indonesian",
    "bekasi": "Indonesian",
    "lagos": "Yoruba",
    "abuja": "Hausa",
    "kano": "Hausa",
    "ibadan": "Yoruba",
    "port harcourt": "Igbo",
    "nairobi": "Swahili",
    "mombasa": "Swahili",
    "kampala": "English",
    "dar es salaam": "Swahili",
    "kigali": "Kinyarwanda",
    "buenos aires": "Spanish",
    "lima": "Spanish",
    "bogota": "Spanish",
    "caracas": "Spanish",
    "santiago": "Spanish",
    "montevideo": "Spanish",
    "asuncion": "Spanish",
    "la paz": "Spanish",
    "sucre": "Spanish",
    "havana": "Spanish",
    "kingston": "English",
    "helsinki": "Finnish",
    "oslo": "Norwegian",
    "stockholm": "Swedish",
    "copenhagen": "Danish",
    "reykjavik": "Icelandic",
    "warsaw": "Polish",
    "prague": "Czech",
    "vienna": "German",
    "athens": "Greek",
    "budapest": "Hungarian",
    "belgrade": "Serbian",
    "zagreb": "Croatian",
    "sarajevo": "Bosnian",
    "paris": "French",
    "ljubljana": "Slovenian",
    "colombo": "Sinhala",
    "kandy": "Sinhala",
    "galle": "Sinhala",
    "jaffna": "Tamil",
    "trincomalee": "Tamil",
    "negombo": "Sinhala",
    "batticaloa": "Tamil",
    "matara": "Sinhala",
    "kurunegala": "Sinhala",
    "anuradhapura": "Sinhala"
}

# Endpoints
#text summerization additional feature
@app.post("/v1/summary", response_model=SummaryResponse)
async def summarize(req: TextRequest, x_api_key: Optional[str] = Header(None)):
    check_api_key(x_api_key)
    text = req.text
    if req.sanitize:
        text = sanitize_text(text)
    flagged = safety_filter(text)
    if flagged:
        logger.info("Safety keywords flagged: %s", flagged)
        raise HTTPException(status_code=422, detail={"error":"Safety policy triggered", "flagged": flagged})
    if len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Empty text after sanitization.")
    max_len = 2000
    input_for_summary = text if len(text) <= max_len else text[:max_len] + " ... (truncated)"
    try:
        summary_out = summarizer(input_for_summary, max_length=req.max_summary_tokens, min_length=30, do_sample=False)
        summary_text = summary_out[0]["summary_text"]
    except Exception as e:
        logger.exception("Summarization failed")
        raise HTTPException(status_code=500, detail=f"Summarization model failure: {e}")
    return {"summary": summary_text}

@app.post("/v1/ner", response_model=NERResponse)
async def ner(req: TextRequest, x_api_key: Optional[str] = Header(None)):
    check_api_key(x_api_key)
    text = req.text
    if req.sanitize:
        text = sanitize_text(text)
    flagged = safety_filter(text)
    if flagged:
        logger.info("Safety keywords flagged on NER request: %s", flagged)
        raise HTTPException(status_code=422, detail={"error":"Safety policy triggered", "flagged": flagged})
    doc = nlp_spacy(text)
    entities = []
    for ent in doc.ents:
        entities.append({"text": ent.text, "label": ent.label_, "start_char": ent.start_char, "end_char": ent.end_char})
    return {"entities": entities}

@app.post("/v1/embed", response_model=EmbedResponse)
async def embed(req: TextRequest, x_api_key: Optional[str] = Header(None)):
    check_api_key(x_api_key)
    text = req.text
    if req.sanitize:
        text = sanitize_text(text)
    try:
        vector = embed_model.encode([text])[0].tolist()
    except Exception as e:
        logger.exception("Embedding generation failed")
        raise HTTPException(status_code=500, detail=f"Embedding failed: {e}")
    return {"vector": vector}

# New city language endpoint
@app.post("/v1/city_language", response_model=CityLanguageResponse)
async def city_language(req: CityRequest, x_api_key: Optional[str] = Header(None)):
    check_api_key(x_api_key)
    city_name = req.city.strip().lower()
    language = CITY_LANG_MAP.get(city_name)
    if not language:
        raise HTTPException(status_code=404, detail=f"No language info available for city '{req.city}'")
    return {"city": req.city, "language": language}

#agent message which will send a message to the backend agent
@app.post("/v1/agent_message")
async def agent_message(msg: AgentMessage, x_api_key: Optional[str] = Header(None)):
    check_api_key(x_api_key)
    msg.timestamp = msg.timestamp or time.time()
    logger.info("Agent message from %s to %s: %s", msg.sender, msg.recipient, msg.message_type)
    if msg.message_type == "request_summary":
        text = msg.payload.get("text", "")
        summary_resp = await summarize(TextRequest(text=text), x_api_key=x_api_key)
        return {"status":"ok", "action":"summary", "result": summary_resp}
    elif msg.message_type == "request_language":
        city = msg.payload.get("city", "")
        lang_resp = await city_language(CityRequest(city=city), x_api_key=x_api_key)
        return {"status":"ok", "action":"language", "result": lang_resp}
    return {"status":"ok", "action":"ack", "received_at": time.time()}
#health check used to check if the api is running or not
@app.get("/health")
async def health():
    return {"status":"ok", "models_loaded": True, "time": time.time()}
