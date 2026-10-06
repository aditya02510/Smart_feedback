import re
import unicodedata

# Keyword dictionaries for romanized code-mixed dialects
HINGLISH_KEYWORDS = {
    "nahi", "raha", "rahi", "rahe", "hai", "hain", "karo", "karna", "bohot", "bahut",
    "achha", "accha", "kharab", "bekaar", "hoga", "hogi", "bhai", "kuch", "sab",
    "padhate", "samajh", "aata", "waqt", "dikkat", "pareshani", "chal", "badhiya",
    "daant", "gussa", "chhod", "chakkar", "batameezi", "purane", "paani", "theek", "mast"
}

TANGLISH_KEYWORDS = {
    "avvatledu", "kavatledu", "undi", "unnayi", "chala", "bagundi", "baga", "ledu",
    "chesaru", "cheyandi", "cheptunnaru", "adigi", "kooda", "virigi", "poyi", "pani",
    "ayindi", "ayyindi", "vachayi", "assalu", "asalu", "vallu", "nerpistunnaru", "ivvakunda",
    "ravatledu", "kurchovadaniki", "ibbandi", "babu", "garu", "cheyaleka", "potunnam", "kosam"
}

def detect_language(text: str) -> str:
    """
    Detects language among English, Hinglish, Tanglish, Hindi, and Telugu.
    Uses Unicode script checks and lexical code-mix marker frequency.
    """
    if not text or not text.strip():
        return "English"

    # Check for Devanagari script (Hindi)
    if re.search(r"[\u0900-\u097F]", text):
        return "Hindi"

    # Check for Telugu script
    if re.search(r"[\u0C00-\u0C7F]", text):
        return "Telugu"

    # Lowercase token set for Romanized text
    tokens = set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))

    hinglish_matches = tokens.intersection(HINGLISH_KEYWORDS)
    tanglish_matches = tokens.intersection(TANGLISH_KEYWORDS)

    if len(tanglish_matches) > 0 and len(tanglish_matches) >= len(hinglish_matches):
        return "Tanglish"
    if len(hinglish_matches) > 0:
        return "Hinglish"

    return "English"

def clean_text(text: str) -> str:
    """
    Cleans and standardizes input text while preserving meaningful context.
    """
    if not text:
        return ""
    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)
    # Remove excessive blank lines and spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text
