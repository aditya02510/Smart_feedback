import os
import io
import csv
import json
from flask import Flask, request, jsonify, render_template, send_file, Response

from engine.classifier import classifier_service
from database.db import (
    init_db, insert_feedback, insert_batch, get_feedbacks,
    get_escalations, update_status, get_dashboard_stats, get_connection
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "college_feedback_dataset.csv")

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload

# Pre-curated test cases for 1-click test drive in the UI
SAMPLE_PRESETS = [
    {
        "label": "Lab Computer Failure (Infrastructure / Negative)",
        "language": "English",
        "text": "The lab computer was not working and I couldn't complete my assignment."
    },
    {
        "label": "Portal Crash with Deadline (Technical / Hinglish)",
        "language": "Hinglish",
        "text": "Sir, portal open nahi ho raha hai aur kal assignment submission hai."
    },
    {
        "label": "Wi-Fi Down in Lab (Technical / Tanglish)",
        "language": "Tanglish",
        "text": "Lab lo Wi-Fi connection asalu ravatledu, speed chala slow undi."
    },
    {
        "label": "Exam Schedule Clash (Examination / English)",
        "language": "English",
        "text": "Mid-term exam schedule clashes with two core subject papers on same day."
    },
    {
        "label": "Exceptional Faculty Praise (Faculty / Positive)",
        "language": "English",
        "text": "Excellent teaching and lucid explanation of complex machine learning concepts."
    },
    {
        "label": "Course Syllabus Neutral (Course / English)",
        "language": "English",
        "text": "Course syllabus includes standard data structures and algorithmic complexity."
    },
    {
        "label": "Accounts Fine & Rude Admin (Administration / English)",
        "language": "English",
        "text": "Accounts department charged fine even though fees was paid before due date."
    },
    {
        "label": "Telugu Script Infrastructure Complaint (Infrastructure / Telugu)",
        "language": "Telugu",
        "text": "ల్యాబ్ లో కంప్యూటర్లు పనిచేయడం లేదు, అసైన్‌మెంట్ పూర్తి కాలేదు."
    }
]

def seed_initial_data_if_empty():
    """Seeds the database with representative initial feedback if empty."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM feedbacks")
    count = cursor.fetchone()[0]
    conn.close()

    if count == 0 and os.path.exists(DATASET_PATH):
        print("Seeding initial dataset into database...")
        records = []
        with open(DATASET_PATH, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= 60:  # Seed first 60 rows for vivid starter charts
                    break
                text = row["feedback"]
                analysis = classifier_service.analyze(text)
                records.append({
                    "feedback_text": text,
                    "clean_text": analysis["clean_text"],
                    "language": analysis["language"],
                    "sentiment": analysis["sentiment"],
                    "confidence": analysis["confidence"],
                    "category": analysis["category"],
                    "priority": analysis["priority"],
                    "action": analysis["action"],
                    "department": analysis["department"],
                    "is_escalated": analysis["is_escalated"],
                    "status": "Open" if analysis["is_escalated"] else "Resolved",
                    "explanation_summary": analysis["explanation"]["summary"],
                    "positive_indicators": analysis["explanation"]["positive_indicators"],
                    "negative_indicators": analysis["explanation"]["negative_indicators"]
                })
        if records:
            insert_batch(records)
            print(f"Successfully seeded {len(records)} starter records.")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/sample-presets", methods=["GET"])
def get_presets():
    return jsonify({"presets": SAMPLE_PRESETS})

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "") or data.get("feedback", "")
    
    if not text or not text.strip():
        return jsonify({"error": "Please provide feedback text to analyze."}), 400

    result = classifier_service.analyze(text)

    # Save to SQLite database
    record_id = insert_feedback(
        feedback_text=result["feedback_text"],
        clean_text=result["clean_text"],
        language=result["language"],
        sentiment=result["sentiment"],
        confidence=result["confidence"],
        category=result["category"],
        priority=result["priority"],
        action=result["action"],
        department=result["department"],
        is_escalated=result["is_escalated"],
        explanation_summary=result["explanation"]["summary"],
        positive_indicators=result["explanation"]["positive_indicators"],
        negative_indicators=result["explanation"]["negative_indicators"]
    )
    result["id"] = record_id
    return jsonify(result)

@app.route("/api/upload-csv", methods=["POST"])
def upload_csv():
    if "file" not in request.files:
        return jsonify({"error": "No CSV file uploaded."}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    try:
        stream = io.StringIO(file.stream.read().decode("utf-8-sig"), newline=None)
        reader = csv.reader(stream)
        rows = list(reader)
        if not rows:
            return jsonify({"error": "CSV file is empty."}), 400

        # Find feedback column
        header = [col.strip().lower() for col in rows[0]]
        feedback_idx = 0
        for possible in ["feedback", "text", "comment", "review", "complaint"]:
            if possible in header:
                feedback_idx = header.index(possible)
                break

        # Process each row (skip header if detected)
        start_idx = 1 if any(h in ["feedback", "text", "sentiment", "comment"] for h in header) else 0
        analyzed_results = []
        db_records = []

        for row in rows[start_idx:]:
            if not row or len(row) <= feedback_idx:
                continue
            text = row[feedback_idx].strip()
            if not text:
                continue
            
            res = classifier_service.analyze(text)
            analyzed_results.append(res)
            db_records.append({
                "feedback_text": res["feedback_text"],
                "clean_text": res["clean_text"],
                "language": res["language"],
                "sentiment": res["sentiment"],
                "confidence": res["confidence"],
                "category": res["category"],
                "priority": res["priority"],
                "action": res["action"],
                "department": res["department"],
                "is_escalated": res["is_escalated"],
                "status": "Open" if res["is_escalated"] else "Resolved",
                "explanation_summary": res["explanation"]["summary"],
                "positive_indicators": res["explanation"]["positive_indicators"],
                "negative_indicators": res["explanation"]["negative_indicators"]
            })

        if db_records:
            insert_batch(db_records)

        summary = {
            "total_processed": len(analyzed_results),
            "positive": sum(1 for r in analyzed_results if r["sentiment"] == "Positive"),
            "neutral": sum(1 for r in analyzed_results if r["sentiment"] == "Neutral"),
            "negative": sum(1 for r in analyzed_results if r["sentiment"] == "Negative"),
            "escalated": sum(1 for r in analyzed_results if r["is_escalated"])
        }

        return jsonify({
            "summary": summary,
            "results": analyzed_results[:100]  # Return first 100 for fast preview
        })

    except Exception as e:
        return jsonify({"error": f"Failed to process CSV: {str(e)}"}), 500

@app.route("/api/export-csv", methods=["GET"])
def export_csv():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, feedback_text, language, sentiment, confidence, category, priority,
               action, department, is_escalated, status, created_at
        FROM feedbacks
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Feedback", "Language", "Sentiment", "Confidence", "Category",
        "Priority", "Action", "Department", "Is Escalated", "Status", "Created At"
    ])
    for r in rows:
        writer.writerow(list(r))

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=feedback_analysis_export.csv"}
    )

@app.route("/api/dashboard-stats", methods=["GET"])
def dashboard_stats():
    stats = get_dashboard_stats()
    return jsonify(stats)

@app.route("/api/escalations", methods=["GET"])
def escalations():
    status = request.args.get("status", "All")
    dept = request.args.get("department", "All")
    records = get_escalations(status=status, department=dept)
    return jsonify({"escalations": records})

@app.route("/api/escalations/<int:ticket_id>/status", methods=["POST"])
def update_escalation_status(ticket_id):
    data = request.get_json(force=True, silent=True) or {}
    new_status = data.get("status", "Resolved")
    if new_status not in ["Open", "In Progress", "Resolved"]:
        return jsonify({"error": "Invalid status."}), 400
    
    success = update_status(ticket_id, new_status)
    if success:
        return jsonify({"success": True, "id": ticket_id, "status": new_status})
    return jsonify({"error": "Ticket not found."}), 404

@app.route("/api/model-metrics", methods=["GET"])
def model_metrics():
    metrics_file = os.path.join(BASE_DIR, "models", "model_metrics.json")
    if os.path.exists(metrics_file):
        with open(metrics_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify({"error": "Metrics not found. Please train models."}), 404

if __name__ == "__main__":
    init_db()
    seed_initial_data_if_empty()
    print("Starting Smart Feedback System on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
