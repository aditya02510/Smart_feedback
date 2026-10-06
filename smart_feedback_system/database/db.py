import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "feedback_system.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feedback_text TEXT NOT NULL,
            clean_text TEXT,
            language TEXT,
            sentiment TEXT,
            confidence REAL,
            category TEXT,
            priority TEXT,
            action TEXT,
            department TEXT,
            is_escalated INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Open',
            explanation_summary TEXT,
            positive_indicators TEXT,
            negative_indicators TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

def insert_feedback(
    feedback_text: str,
    clean_text: str,
    language: str,
    sentiment: str,
    confidence: float,
    category: str,
    priority: str,
    action: str,
    department: str,
    is_escalated: bool,
    explanation_summary: str = "",
    positive_indicators: list = None,
    negative_indicators: list = None,
    status: str = "Open"
) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO feedbacks (
            feedback_text, clean_text, language, sentiment, confidence,
            category, priority, action, department, is_escalated, status,
            explanation_summary, positive_indicators, negative_indicators
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        feedback_text,
        clean_text,
        language,
        sentiment,
        float(confidence),
        category,
        priority,
        action,
        department,
        1 if is_escalated else 0,
        status,
        explanation_summary,
        json.dumps(positive_indicators or []),
        json.dumps(negative_indicators or [])
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id

def insert_batch(records: List[Dict[str, Any]]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO feedbacks (
            feedback_text, clean_text, language, sentiment, confidence,
            category, priority, action, department, is_escalated, status,
            explanation_summary, positive_indicators, negative_indicators
        ) VALUES (
            :feedback_text, :clean_text, :language, :sentiment, :confidence,
            :category, :priority, :action, :department, :is_escalated, :status,
            :explanation_summary, :positive_indicators, :negative_indicators
        )
    """, [
        {
            "feedback_text": r["feedback_text"],
            "clean_text": r.get("clean_text", r["feedback_text"]),
            "language": r.get("language", "English"),
            "sentiment": r["sentiment"],
            "confidence": float(r.get("confidence", 0.9)),
            "category": r["category"],
            "priority": r.get("priority", "Medium"),
            "action": r.get("action", "Standard Log"),
            "department": r.get("department", "General"),
            "is_escalated": 1 if r.get("is_escalated", False) else 0,
            "status": r.get("status", "Open"),
            "explanation_summary": r.get("explanation_summary", ""),
            "positive_indicators": json.dumps(r.get("positive_indicators", [])),
            "negative_indicators": json.dumps(r.get("negative_indicators", []))
        }
        for r in records
    ])
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return count

def get_feedbacks(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM feedbacks
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        d = dict(row)
        d["positive_indicators"] = json.loads(d["positive_indicators"] or "[]")
        d["negative_indicators"] = json.loads(d["negative_indicators"] or "[]")
        result.append(d)
    return result

def get_escalations(status: Optional[str] = None, department: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM feedbacks WHERE is_escalated = 1"
    params = []
    if status and status != "All":
        query += " AND status = ?"
        params.append(status)
    if department and department != "All":
        query += " AND department = ?"
        params.append(department)
    query += " ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        d = dict(row)
        d["positive_indicators"] = json.loads(d["positive_indicators"] or "[]")
        d["negative_indicators"] = json.loads(d["negative_indicators"] or "[]")
        result.append(d)
    return result

def update_status(record_id: int, new_status: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE feedbacks SET status = ? WHERE id = ?", (new_status, record_id))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def get_dashboard_stats() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()

    # Total
    cursor.execute("SELECT COUNT(*) FROM feedbacks")
    total = cursor.fetchone()[0]

    # Sentiments
    cursor.execute("SELECT sentiment, COUNT(*) FROM feedbacks GROUP BY sentiment")
    sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
    for row in cursor.fetchall():
        sentiment_counts[row[0]] = row[1]

    # Categories
    cursor.execute("SELECT category, COUNT(*) FROM feedbacks GROUP BY category")
    category_counts = {}
    for row in cursor.fetchall():
        category_counts[row[0]] = row[1]

    # Category x Sentiment matrix
    cursor.execute("SELECT category, sentiment, COUNT(*) FROM feedbacks GROUP BY category, sentiment")
    category_matrix = {}
    for cat, sent, count in cursor.fetchall():
        if cat not in category_matrix:
            category_matrix[cat] = {"Positive": 0, "Neutral": 0, "Negative": 0}
        category_matrix[cat][sent] = count

    # Priorities
    cursor.execute("SELECT priority, COUNT(*) FROM feedbacks GROUP BY priority")
    priority_counts = {"High": 0, "Medium": 0, "Low": 0}
    for row in cursor.fetchall():
        priority_counts[row[0]] = row[1]

    # Languages
    cursor.execute("SELECT language, COUNT(*) FROM feedbacks GROUP BY language")
    language_counts = {}
    for row in cursor.fetchall():
        language_counts[row[0]] = row[1]

    # Escalations & Status
    cursor.execute("SELECT COUNT(*) FROM feedbacks WHERE is_escalated = 1")
    total_escalated = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedbacks WHERE is_escalated = 1 AND status = 'Open'")
    open_escalated = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedbacks WHERE is_escalated = 1 AND status = 'In Progress'")
    in_progress_escalated = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM feedbacks WHERE is_escalated = 1 AND status = 'Resolved'")
    resolved_escalated = cursor.fetchone()[0]

    # Recent escalations
    cursor.execute("""
        SELECT id, feedback_text, category, priority, department, status, created_at
        FROM feedbacks
        WHERE is_escalated = 1
        ORDER BY id DESC
        LIMIT 5
    """)
    recent_escalations = [dict(r) for r in cursor.fetchall()]

    conn.close()

    pct_pos = round((sentiment_counts["Positive"] / total * 100), 1) if total > 0 else 0
    pct_neu = round((sentiment_counts["Neutral"] / total * 100), 1) if total > 0 else 0
    pct_neg = round((sentiment_counts["Negative"] / total * 100), 1) if total > 0 else 0

    return {
        "total": total,
        "sentiment_counts": sentiment_counts,
        "sentiment_percentages": {
            "Positive": pct_pos,
            "Neutral": pct_neu,
            "Negative": pct_neg
        },
        "category_counts": category_counts,
        "category_matrix": category_matrix,
        "priority_counts": priority_counts,
        "language_counts": language_counts,
        "escalation_summary": {
            "total_escalated": total_escalated,
            "open": open_escalated,
            "in_progress": in_progress_escalated,
            "resolved": resolved_escalated
        },
        "recent_escalations": recent_escalations
    }
