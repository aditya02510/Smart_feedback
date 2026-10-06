import re
from typing import Dict, Any, Tuple

# Urgency keywords triggering high priority
CRITICAL_KEYWORDS = {
    "urgent", "urgently", "emergency", "immediately", "crash", "crashed", "dead",
    "deadline", "tomorrow", "kal", "fail", "failed", "cut", "money", "stuck",
    "broken", "leak", "leaking", "fire", "danger", "dangerous", "unhygienic",
    "harassment", "abusive", "batameezi", "virigi", "pani cheyatledu", "nahi chal raha",
    "open nahi ho raha", "kavatledu", "asalu", "clash", "out of syllabus", "two months"
}

DEPARTMENT_MAP = {
    "Technical": "IT Infrastructure & Systems Support",
    "Infrastructure": "Campus Facilities & Maintenance Office",
    "Faculty": "Dean of Academics & Head of Department",
    "Examination": "Controller of Examinations (COE) Cell",
    "Course": "Academic Curriculum & Board of Studies",
    "Administration": "Registrar & Administrative Affairs Office"
}

def determine_priority_and_action(
    text: str,
    sentiment: str,
    sentiment_conf: float,
    category: str
) -> Tuple[str, str, str, bool]:
    """
    Computes priority, escalation action, assigned department, and escalation flag.
    Returns: (priority, action, target_department, is_escalated)
    """
    text_lower = text.lower()
    department = DEPARTMENT_MAP.get(category, "General Administration")
    
    # Check for presence of critical/urgent keywords
    urgency_detected = any(re.search(rf"\b{re.escape(kw)}\b", text_lower) for kw in CRITICAL_KEYWORDS)
    
    # Priority logic
    if sentiment == "Negative":
        if urgency_detected or sentiment_conf >= 0.75 or category in ["Technical", "Examination", "Infrastructure"]:
            priority = "High"
            action = f"🚨 Immediate Escalation: Dispatched alert to {department}"
            is_escalated = True
        else:
            priority = "Medium"
            action = f"⚠️ Escalated: Routed to {department} support queue"
            is_escalated = True
    elif sentiment == "Neutral":
        if urgency_detected:
            priority = "Medium"
            action = f"ℹ️ Routed inquiry to {department}"
            is_escalated = False
        else:
            priority = "Low"
            action = "📋 Standard Log: Stored for periodic departmental review"
            is_escalated = False
    else:  # Positive
        priority = "Low"
        action = f"⭐ Positive Record: Archived for faculty/department appreciation"
        is_escalated = False

    return priority, action, department, is_escalated
