import os
import re
import time
import logging
import csv
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# NLP & embeddings
import spacy
from transformers import pipeline, Pipeline
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from googletrans import Translator

# -------------------------
# Load environment
# -------------------------
load_dotenv()

# -------------------------
# Configuration and logging
# -------------------------
API_KEY = os.environ.get(
    "sk-langbot-2f93b77f8a1c4e92a7f",
    "716c8936e30e4289421bb54a0cd1318635f0804994699059fa12989c93821059"
)

PINECONE_API_KEY = os.environ.get("pcsk_4CoUJw_FZjTGywY2Q9wn3qenNqhecELEBw55qabN1qiJSY3S2KKsg9Chbogs85t4HWdzh8")
PINECONE_INDEX = os.environ.get("ragmain")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("language_bot")

# -------------------------
# FastAPI app
# -------------------------
app = FastAPI(title="Language Agent for Hybrid RAG Chatbot")

# -------------------------
# Request / Response Models
# -------------------------
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


class CityRequest(BaseModel):
    city: str


class CityLanguageResponse(BaseModel):
    city: str
    language: str
    common_phrases: Dict[str, Dict[str, str]]


class TranslateRequest(BaseModel):
    text: str
    dest: str


class TranslateResponse(BaseModel):
    translated_text: str
    src: str
    dest: str


# -------------------------
# Load NLP / Embedding Models
# -------------------------
try:
    nlp_spacy = spacy.load("en_core_web_sm")
except Exception:
    logger.warning("spaCy model not found: en_core_web_sm. Run: python -m spacy download en_core_web_sm")
    raise

summarizer: Pipeline = pipeline(
    "summarization",
    model=os.environ.get("SUMMARIZATION_MODEL", "facebook/bart-large-cnn")
)

embed_model = SentenceTransformer(
    os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
)

pc = None
if PINECONE_API_KEY:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    if PINECONE_INDEX and PINECONE_INDEX not in [i["name"] for i in pc.list_indexes()]:
        logger.info(
            f"Pinecone index {PINECONE_INDEX} not found. "
            f"Create it or configure environment correctly."
        )

translator = Translator()

# -------------------------
# Utility & Security Helpers
# -------------------------
MAX_INPUT_LENGTH = int(os.environ.get("LANGUAGE_BOT_MAX_INPUT", 50000))  # characters

SUSPICIOUS_PATTERNS = [
    r"<script.*?>",
    r"javascript:",
    r"onerror\s*=",
    r"onload\s*=",
]

SAFETY_KEYWORDS = {"suicide", "self-harm", "illegal", "bomb", "exploit", "terrorist"}


def check_api_key(x_api_key: Optional[str]):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")


def sanitize_text(text: str) -> str:
    for pat in SUSPICIOUS_PATTERNS:
        text = re.sub(pat, "[removed]", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) > MAX_INPUT_LENGTH:
        raise HTTPException(
            status_code=413,
            detail=f"Input too large ({len(text)} > {MAX_INPUT_LENGTH})"
        )
    return text


def safety_filter(text: str) -> List[str]:
    lowered = text.lower()
    return [kw for kw in SAFETY_KEYWORDS if kw in lowered]


# -------------------------
# Load Maps from CSV
# -------------------------
def load_csv_to_dict(filepath: str, key_col: str, val_col: str) -> Dict[str, str]:
    data = {}
    if os.path.exists(filepath):
        with open(filepath, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                key = row[key_col].strip().lower()
                val = row[val_col].strip()
                data[key] = val
    else:
        logger.warning(f"CSV file not found: {filepath}")
    return data


CITY_LANG_MAP = load_csv_to_dict("cities.csv", "city", "language")
COUNTRY_LANG_MAP = load_csv_to_dict("countries.csv", "country", "language")

# -------------------------
# Language Code Map
# -------------------------
LANG_NAME_TO_CODE = {
    "english": "en",
    "french": "fr",
    "spanish": "es",
    "german": "de",
    "italian": "it",
    "japanese": "ja",
    "chinese": "zh-cn",
    "korean": "ko",
    "arabic": "ar",
    "hindi": "hi",
    "tamil": "ta",
    "sinhala": "si",
    "swahili": "sw",
    "portuguese": "pt",
    "russian": "ru",
    "turkish": "tr",
    "thai": "th",
    "nepali": "ne",
    "bengali": "bn",
    "urdu": "ur",
    "filipino": "tl",
    "indonesian": "id",
    "malay": "ms",
    "hebrew": "he",
    "persian": "fa",
    "burmese": "my",
    "vietnamese": "vi",
    "norwegian": "no",
    "swedish": "sv",
    "danish": "da",
    "finnish": "fi",
    "polish": "pl",
    "czech": "cs",
    "hungarian": "hu",
    "romanian": "ro",
    "bulgarian": "bg",
    "greek": "el",
    "serbian": "sr",
    "croatian": "hr",
    "bosnian": "bs",
    "albanian": "sq",
    "macedonian": "mk",
    "afrikaans": "af",
    "zulu": "zu",
    "amharic": "am",
    "fijian": "fj",
    "tok pisin": "tpi"
}

# -------------------------
# Endpoints
# -------------------------
@app.post("/v1/summary", response_model=SummaryResponse)
async def summarize(req: TextRequest, x_api_key: Optional[str] = Header(None)):
    check_api_key(x_api_key)

    text = sanitize_text(req.text) if req.sanitize else req.text
    flagged = safety_filter(text)

    if flagged:
        logger.info("Safety keywords flagged: %s", flagged)
        raise HTTPException(
            status_code=422,
            detail={"error": "Safety policy triggered", "flagged": flagged}
        )

    if not text.strip():
        raise HTTPException(status_code=400, detail="Empty text after sanitization.")

    max_len = 2000
    input_for_summary = text if len(text) <= max_len else text[:max_len] + " ... (truncated)"

    try:
        summary_out = summarizer(
            input_for_summary,
            max_length=req.max_summary_tokens,
            min_length=30,
            do_sample=False
        )
        summary_text = summary_out[0]["summary_text"]
    except Exception as e:
        logger.exception("Summarization failed")
        raise HTTPException(status_code=500, detail=f"Summarization model failure: {e}")

    return {"summary": summary_text}


@app.post("/v1/ner", response_model=NERResponse)
async def ner(req: TextRequest, x_api_key: Optional[str] = Header(None)):
    check_api_key(x_api_key)

    text = sanitize_text(req.text) if req.sanitize else req.text
    flagged = safety_filter(text)

    if flagged:
        logger.info("Safety keywords flagged on NER request: %s", flagged)
        raise HTTPException(
            status_code=422,
            detail={"error": "Safety policy triggered", "flagged": flagged}
        )

    doc = nlp_spacy(text)
    entities = [
        {"text": ent.text, "label": ent.label_, "start_char": ent.start_char, "end_char": ent.end_char}
        for ent in doc.ents
    ]

    return {"entities": entities}


@app.post("/v1/embed", response_model=EmbedResponse)
async def embed(req: TextRequest, x_api_key: Optional[str] = Header(None)):
    check_api_key(x_api_key)

    text = sanitize_text(req.text) if req.sanitize else req.text

    try:
        vector = embed_model.encode([text])[0].tolist()
    except Exception as e:
        logger.exception("Embedding generation failed")
        raise HTTPException(status_code=500, detail=f"Embedding failed: {e}")

    return {"vector": vector}


@app.post("/v1/city_language", response_model=CityLanguageResponse)
async def city_language(req: CityRequest, x_api_key: Optional[str] = Header(None)):
    check_api_key(x_api_key)

    city_name = req.city.strip().lower()
    language = CITY_LANG_MAP.get(city_name)

    if not language:
        language = COUNTRY_LANG_MAP.get(city_name)

    if not language:
        raise HTTPException(status_code=404, detail=f"No language info available for '{req.city}'")

    common_phrases = ["Hello", "Thank you", "How are you?", "Good morning", "Good night"]
    phrases_translated = {}

    lang_code = LANG_NAME_TO_CODE.get(language.lower())
    if not lang_code:
        phrases_translated = {p: {"translation": "(translation unavailable)", "pronunciation": "(N/A)"} for p in common_phrases}
    else:
        try:
            for phrase in common_phrases:
                result = translator.translate(phrase, dest=lang_code)
                phrases_translated[phrase] = {
                    "translation": result.text,
                    "pronunciation": result.pronunciation or result.text
                }
        except Exception as e:
            logger.warning(f"Translation failed: {e}")
            phrases_translated = {p: {"translation": "(translation unavailable)", "pronunciation": "(N/A)"} for p in common_phrases}

    return {
        "city": req.city,
        "language": language,
        "common_phrases": phrases_translated,
    }


@app.post("/v1/translate", response_model=TranslateResponse)
async def translate_text(req: TranslateRequest, x_api_key: Optional[str] = Header(None)):
    check_api_key(x_api_key)

    try:
        result = translator.translate(req.text, dest=req.dest)
    except Exception as e:
        logger.exception("Translation failed")
        raise HTTPException(status_code=500, detail=f"Translation failed: {e}")

    return {
        "translated_text": result.text,
        "src": result.src,
        "dest": result.dest,
    }
