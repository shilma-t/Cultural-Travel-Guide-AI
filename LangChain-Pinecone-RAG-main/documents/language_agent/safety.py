# language_agent/safety.py
import re
from typing import Dict

PROHIBITED_PATTERNS = [
    r"how to make a bomb",
    r"evade customs",
    r"(how to|ways to).*(kill|murder|harm)",
    r"(illicit|illegal).*(buy|sell)",
]

def safety_check(text: str) -> Dict:
    t = text.lower()
    for pat in PROHIBITED_PATTERNS:
        if re.search(pat, t):
            return {"allow": False, "reason": "disallowed_content", "message": "I can't assist with that request."}
    # Basic sanitization: strip control characters
    cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)
    return {"allow": True, "reason": None, "cleaned": cleaned}
