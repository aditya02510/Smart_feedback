import os
import sys
import unittest
import json

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from engine.preprocessor import clean_text, detect_language
from engine.classifier import classifier_service
from engine.explainer import explain_sentiment
from engine.escalation_engine import determine_priority_and_action
from database.db import init_db, insert_feedback, get_feedbacks, get_dashboard_stats, update_status
from app import app

class TestSmartFeedbackPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()

    def test_preprocessor_language_detection(self):
        self.assertEqual(detect_language("The computer is not working."), "English")
        self.assertEqual(detect_language("Sir portal open nahi ho raha hai."), "Hinglish")
        self.assertEqual(detect_language("Lab lo computers work avvatledu."), "Tanglish")
        self.assertEqual(detect_language("पोर्टल काम नहीं कर रहा है।"), "Hindi")
        self.assertEqual(detect_language("క్యాంపస్ వైఫై చాలా వేగంగా పనిచేస్తోంది."), "Telugu")

    def test_english_negative_escalation(self):
        text = "The lab computer was not working and I couldn't complete my assignment."
        res = classifier_service.analyze(text)
        self.assertEqual(res["sentiment"], "Negative")
        self.assertEqual(res["language"], "English")
        self.assertIn(res["category"], ["Infrastructure", "Technical"])
        self.assertEqual(res["priority"], "High")
        self.assertTrue(res["is_escalated"])
        self.assertIn("not working", res["explanation"]["negative_indicators"])

    def test_hinglish_negative_escalation(self):
        text = "Sir, portal open nahi ho raha hai aur kal assignment submission hai."
        res = classifier_service.analyze(text)
        self.assertEqual(res["sentiment"], "Negative")
        self.assertEqual(res["language"], "Hinglish")
        self.assertEqual(res["category"], "Technical")
        self.assertEqual(res["priority"], "High")
        self.assertTrue(res["is_escalated"])

    def test_tanglish_negative_escalation(self):
        text = "Lab lo Wi-Fi connection asalu ravatledu, speed chala slow undi."
        res = classifier_service.analyze(text)
        self.assertEqual(res["sentiment"], "Negative")
        self.assertEqual(res["language"], "Tanglish")
        self.assertEqual(res["category"], "Technical")
        self.assertEqual(res["priority"], "High")
        self.assertTrue(res["is_escalated"])

    def test_positive_faculty_feedback(self):
        text = "Excellent teaching and lucid explanation of complex machine learning concepts."
        res = classifier_service.analyze(text)
        self.assertEqual(res["sentiment"], "Positive")
        self.assertEqual(res["category"], "Faculty")
        self.assertEqual(res["priority"], "Low")
        self.assertFalse(res["is_escalated"])
        self.assertIn("excellent", res["explanation"]["positive_indicators"])

    def test_database_and_stats(self):
        record_id = insert_feedback(
            feedback_text="Test test feedback for database check",
            clean_text="Test test feedback for database check",
            language="English",
            sentiment="Negative",
            confidence=0.95,
            category="Technical",
            priority="High",
            action="Immediate Escalation",
            department="IT Support",
            is_escalated=True
        )
        self.assertGreater(record_id, 0)

        # Update status
        updated = update_status(record_id, "Resolved")
        self.assertTrue(updated)

        # Dashboard stats check
        stats = get_dashboard_stats()
        self.assertGreater(stats["total"], 0)
        self.assertIn("Positive", stats["sentiment_percentages"])

    def test_flask_endpoints(self):
        client = app.test_client()

        # 1. Test index page
        res = client.get("/")
        self.assertEqual(res.status_code, 200)

        # 2. Test analyze endpoint
        res = client.post("/api/analyze", json={
            "text": "The portal is dead again."
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["sentiment"], "Negative")
        self.assertEqual(data["category"], "Technical")

        # 3. Test presets
        res = client.get("/api/sample-presets")
        self.assertEqual(res.status_code, 200)

        # 4. Test dashboard stats
        res = client.get("/api/dashboard-stats")
        self.assertEqual(res.status_code, 200)

        # 5. Test model metrics
        res = client.get("/api/model-metrics")
        self.assertEqual(res.status_code, 200)

if __name__ == "__main__":
    unittest.main()
