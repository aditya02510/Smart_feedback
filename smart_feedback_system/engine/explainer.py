import re
from typing import Dict, List, Any

# High-impact sentiment indicators across English, Hinglish, and Tanglish
DOMAIN_SENTIMENT_INDICATORS = {
    # Negative indicators
    "not working": -1.0,
    "couldn't complete": -0.9,
    "could not complete": -0.9,
    "dead": -0.85,
    "crashed": -0.9,
    "crash": -0.8,
    "broken": -0.9,
    "error": -0.7,
    "unhygienic": -0.85,
    "terrible": -0.9,
    "worst": -0.95,
    "horrible": -0.9,
    "unfair": -0.85,
    "biased": -0.8,
    "delayed": -0.75,
    "delay": -0.7,
    "leak": -0.8,
    "leaking": -0.8,
    "fails": -0.8,
    "failed": -0.8,
    "rudely": -0.85,
    "rude": -0.8,
    "outdated": -0.75,
    "unbearable": -0.85,
    "overcrowded": -0.8,
    "misbehave": -0.9,
    "disrupted": -0.75,
    "flickering": -0.7,
    "open nahi ho raha": -0.95,
    "nahi ho raha": -0.85,
    "nahi chal raha": -0.85,
    "bekaar": -0.9,
    "kharab": -0.85,
    "dikkat": -0.75,
    "pareshani": -0.75,
    "band hai": -0.75,
    "batameezi": -0.9,
    "asalu ravatledu": -0.95,
    "ravatledu": -0.85,
    "work avvatledu": -0.9,
    "avvatledu": -0.85,
    "kavatledu": -0.85,
    "pani cheyatledu": -0.9,
    "baga ledu": -0.85,
    "virigi poyi": -0.85,
    "kopadutunnaru": -0.8,
    "काम नहीं कर रहा": -0.95,
    "पूरी तरह खराब": -0.9,
    "పనిచేయడం లేదు": -0.95,

    # Positive indicators
    "excellent": 1.0,
    "great": 0.8,
    "superb": 0.9,
    "wonderfully": 0.85,
    "phenomenal": 0.95,
    "clean": 0.7,
    "smooth": 0.8,
    "fast": 0.75,
    "promptly": 0.8,
    "prompt": 0.75,
    "helpful": 0.8,
    "supportive": 0.85,
    "patient": 0.75,
    "inspiring": 0.9,
    "seamless": 0.85,
    "top-notch": 0.95,
    "transparent": 0.8,
    "kudos": 0.85,
    "thank you": 0.8,
    "thanks": 0.7,
    "bohot achha": 0.9,
    "achha": 0.75,
    "badhiya": 0.85,
    "mast": 0.85,
    "super": 0.8,
    "chala bagundi": 0.9,
    "bagundi": 0.8,
    "super ga": 0.85,
    "neat ga": 0.75,
    "quick ga": 0.75,
    "बहुत अच्छा": 0.9,
    "చాలా వేగంగా": 0.85,
    "చాలా బాగుంది": 0.9
}

def explain_sentiment(
    text: str,
    sentiment: str,
    vectorizer=None,
    model=None
) -> Dict[str, Any]:
    """
    Extracts contributing words/phrases and provides an explainability breakdown.
    Combines trained model feature coefficients with domain sentiment phrase matchers.
    """
    text_lower = text.lower()
    positive_phrases = []
    negative_phrases = []

    # 1. Check for domain phrase matches
    for phrase, score in DOMAIN_SENTIMENT_INDICATORS.items():
        if phrase in text_lower:
            if score > 0:
                positive_phrases.append((phrase, score))
            else:
                negative_phrases.append((phrase, score))

    # 2. If vectorizer and model are available, extract top model-weighted tokens
    if vectorizer is not None and model is not None:
        try:
            tokens = vectorizer.build_analyzer()(text)
            feature_names = vectorizer.get_feature_names_out()
            feature_index = {feat: idx for idx, feat in enumerate(feature_names)}
            
            # Identify class index
            classes = list(model.classes_)
            if sentiment in classes:
                class_idx = classes.index(sentiment)
                coefs = model.coef_[class_idx] if hasattr(model, "coef_") else None
                
                if coefs is not None:
                    for tok in set(tokens):
                        if tok in feature_index:
                            idx = feature_index[tok]
                            weight = float(coefs[idx])
                            if weight > 0.4 and tok not in [p[0] for p in positive_phrases]:
                                positive_phrases.append((tok, round(weight, 3)))
                            elif weight < -0.4 and tok not in [p[0] for p in negative_phrases]:
                                negative_phrases.append((tok, round(weight, 3)))
        except Exception:
            pass

    # Sort phrases by absolute impact
    positive_phrases = sorted(positive_phrases, key=lambda x: abs(x[1]), reverse=True)[:5]
    negative_phrases = sorted(negative_phrases, key=lambda x: abs(x[1]), reverse=True)[:5]

    # Generate explanatory summary text
    if sentiment == "Negative":
        if negative_phrases:
            top_words = ", ".join([f"'{p[0]}'" for p in negative_phrases[:3]])
            summary = f"Classified as Negative primarily because of issue-related words/phrases: {top_words}"
        else:
            summary = "Classified as Negative based on overall critical tonality and complaint context."
    elif sentiment == "Positive":
        if positive_phrases:
            top_words = ", ".join([f"'{p[0]}'" for p in positive_phrases[:3]])
            summary = f"Classified as Positive primarily because of appreciative terms: {top_words}"
        else:
            summary = "Classified as Positive based on constructive, encouraging tone."
    else:  # Neutral
        summary = "Classified as Neutral: Information is factual or balanced with no dominant polar phrases."

    # Highlight HTML generator
    highlighted_text = text
    # Wrap negative words in <mark class="badge-neg">
    for p, _ in negative_phrases:
        pattern = re.compile(re.escape(p), re.IGNORECASE)
        highlighted_text = pattern.sub(f'<span class="explain-token token-negative">{p}</span>', highlighted_text)
    # Wrap positive words in <mark class="badge-pos">
    for p, _ in positive_phrases:
        pattern = re.compile(re.escape(p), re.IGNORECASE)
        highlighted_text = pattern.sub(f'<span class="explain-token token-positive">{p}</span>', highlighted_text)

    return {
        "summary": summary,
        "positive_indicators": [p[0] for p in positive_phrases],
        "negative_indicators": [p[0] for p in negative_phrases],
        "highlighted_html": highlighted_text
    }
