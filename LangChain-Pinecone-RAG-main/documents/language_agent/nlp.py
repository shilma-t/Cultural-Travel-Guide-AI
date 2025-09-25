# language_agent/nlp.py
import spacy
import os
from typing import Tuple, List, Dict

# lazy-load spaCy small model (en_core_web_sm). Install or switch to multilingual model if needed.
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    # if not present, use blank model and warn
    nlp = spacy.blank("en")

def analyze_intent_entities(text: str, lang: str = "en") -> Tuple[str, List[str]]:
    """
    Very small intent + NER detector. Replace or expand with a classifier for production.
    Returns (intent, entities)
    """
    doc = nlp(text)
    entities = [ent.text for ent in doc.ents]
    # naive intent heuristics:
    text_l = text.lower()
    if any(w in text_l for w in ["translate", "how to say", "say in", "phrase"]):
        intent = "translate"
    elif any(w in text_l for w in ["etiquette", "norm", "custom", "tipping", "respect"]):
        intent = "cultural_tips"
    elif any(w in text_l for w in ["is it safe", "safe to", "dangerous", "risk"]):
        intent = "safety_query"
    elif any(w in text_l for w in ["recommend", "suggest", "places to visit", "what to do"]):
        intent = "recommendation"
    else:
        intent = "general_qa"
    return intent, entities

def translate_text_if_needed(text: str, target_lang: str = "en") -> str:
    # stub: integrate a real translator (Helsinki models, or external API).
    # For now just return text (assumes LLM produced correct language). Keep placeholder to plug in later.
    return text
