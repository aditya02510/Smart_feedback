import os
import joblib
import numpy as np
from typing import Dict, Any

from engine.preprocessor import clean_text, detect_language
from engine.escalation_engine import determine_priority_and_action
from engine.explainer import explain_sentiment

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
SENTIMENT_MODEL_PATH = os.path.join(MODELS_DIR, "sentiment_model.joblib")
CATEGORY_MODEL_PATH = os.path.join(MODELS_DIR, "category_model.joblib")

class FeedbackClassifier:
    def __init__(self):
        self.sentiment_bundle = None
        self.category_bundle = None
        self.load_models()

    def load_models(self):
        if os.path.exists(SENTIMENT_MODEL_PATH):
            self.sentiment_bundle = joblib.load(SENTIMENT_MODEL_PATH)
        if os.path.exists(CATEGORY_MODEL_PATH):
            self.category_bundle = joblib.load(CATEGORY_MODEL_PATH)

    def analyze(self, raw_text: str) -> Dict[str, Any]:
        cleaned = clean_text(raw_text)
        language = detect_language(raw_text)

        if not cleaned:
            return {
                "feedback_text": raw_text,
                "clean_text": "",
                "language": language,
                "sentiment": "Neutral",
                "confidence": 0.0,
                "sentiment_probabilities": {"Positive": 0.0, "Neutral": 1.0, "Negative": 0.0},
                "category": "Administration",
                "category_confidence": 0.0,
                "priority": "Low",
                "action": "Empty feedback",
                "department": "General Administration",
                "is_escalated": False,
                "explanation": {
                    "summary": "No content provided to analyze.",
                    "positive_indicators": [],
                    "negative_indicators": [],
                    "highlighted_html": ""
                }
            }

        # 1. Sentiment Inference
        sent_vec = self.sentiment_bundle["vectorizer"].transform([cleaned])
        sent_model = self.sentiment_bundle["model"]
        sent_classes = self.sentiment_bundle["classes"]
        
        if hasattr(sent_model, "predict_proba"):
            sent_probs = sent_model.predict_proba(sent_vec)[0]
        elif hasattr(sent_model, "decision_function"):
            df = sent_model.decision_function(sent_vec)[0]
            # Softmax approximation
            exp_df = np.exp(df - np.max(df))
            sent_probs = exp_df / np.sum(exp_df)
        else:
            sent_probs = [0.33, 0.33, 0.34]

        best_sent_idx = int(np.argmax(sent_probs))
        predicted_sentiment = sent_classes[best_sent_idx]
        sent_confidence = float(sent_probs[best_sent_idx])

        sent_prob_dict = {
            cls_name: round(float(prob), 4)
            for cls_name, prob in zip(sent_classes, sent_probs)
        }

        # 2. Category Inference
        cat_vec = self.category_bundle["vectorizer"].transform([cleaned])
        cat_model = self.category_bundle["model"]
        cat_classes = self.category_bundle["classes"]

        if hasattr(cat_model, "predict_proba"):
            cat_probs = cat_model.predict_proba(cat_vec)[0]
        else:
            cat_probs = np.ones(len(cat_classes)) / len(cat_classes)

        best_cat_idx = int(np.argmax(cat_probs))
        predicted_category = cat_classes[best_cat_idx]
        cat_confidence = float(cat_probs[best_cat_idx])

        # 3. Priority and Escalation
        priority, action, department, is_escalated = determine_priority_and_action(
            text=raw_text,
            sentiment=predicted_sentiment,
            sentiment_conf=sent_confidence,
            category=predicted_category
        )

        # 4. Explainability Analysis
        explanation = explain_sentiment(
            text=raw_text,
            sentiment=predicted_sentiment,
            vectorizer=self.sentiment_bundle["vectorizer"],
            model=sent_model
        )

        return {
            "feedback_text": raw_text,
            "clean_text": cleaned,
            "language": language,
            "sentiment": predicted_sentiment,
            "confidence": round(sent_confidence, 4),
            "sentiment_probabilities": sent_prob_dict,
            "category": predicted_category,
            "category_confidence": round(cat_confidence, 4),
            "priority": priority,
            "action": action,
            "department": department,
            "is_escalated": is_escalated,
            "explanation": explanation
        }

# Singleton instance
classifier_service = FeedbackClassifier()
