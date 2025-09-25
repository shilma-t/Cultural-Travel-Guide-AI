# language_agent/utils.py
import json, os, datetime

def build_rag_prompt(user_text: str, intent: str, entities: list, retrieved_docs: list,
                     user_locale: str = "en-US", user_lang: str = "en", context: dict = None) -> str:
    """
    Build a clear RAG prompt that asks the LLM to use provided doc snippets and cite sources.
    """
    header = (
        "You are a concise travel culture assistant. Use the following local documents and web search excerpts "
        "to answer the user's question. Provide 3 short tips or a short paragraph depending on the user's intent. "
        "If the information is sensitive or uncertain, say so and provide provenance.\n\n"
    )
    ctx = f"User locale: {user_locale}\nUser language: {user_lang}\nIntent: {intent}\nEntities: {entities}\n\n"
    docs_section = "Local / Retrieved Documents:\n"
    for i, d in enumerate(retrieved_docs):
        docs_section += f"[DOC {i+1}]: {d}\n\n"
    docs_section = docs_section if retrieved_docs else "No local documents found.\n\n"
    footer = f"\nUser question: {user_text}\n\nAnswer concisely and include 'Sources:' with short citations."
    prompt = header + ctx + docs_section + footer
    return prompt

def log_interaction(session_id, message_id, user_text, intent, entities, retrieved_docs, answer, provenance=None):
    # Simple append log. In production push to a secure log store with retention policy.
    logs_dir = os.getenv("LANG_AGENT_LOG_DIR", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    fname = os.path.join(logs_dir, f"session_{session_id}.log")
    entry = {
        "time": datetime.datetime.utcnow().isoformat() + "Z",
        "message_id": message_id,
        "user_text": user_text,
        "intent": intent,
        "entities": entities,
        "retrieved_docs_count": len(retrieved_docs) if retrieved_docs else 0,
        "answer_preview": (answer[:200] if isinstance(answer, str) else str(answer)),
        "provenance": provenance
    }
    with open(fname, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
