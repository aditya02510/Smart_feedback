# Smart Feedback Sentiment Analysis and Escalation System

An intelligent, web-based Machine Learning and NLP platform designed to analyze student, customer, and academic feedback in real time. The system classifies sentiments, categorizes issues across campus departments, assigns urgency priorities, triggers automated escalations, and offers **Explainable AI (XAI)** token-level feature attribution.

It features robust support for domain-specific vocabulary and code-mixed Indian dialects (**English, Hinglish, Tanglish, Hindi, Telugu**).

---

## 🌟 Key Features

1. **Multi-Dialect & Code-Mixed NLP**:
   - Detects standard **English**, **Hinglish** (*"Sir portal open nahi ho raha hai"*), **Tanglish** (*"Lab lo Wi-Fi connection asalu ravatledu"*), **Hindi** (Devanagari), and **Telugu** script.
   - Character and word n-gram feature extraction provides high resilience against phonetic transliterations and typos.

2. **Accurate Sentiment Classification**:
   - Classifies feedback into **Positive 😊**, **Neutral 😐**, and **Negative 😡** with calibrated probability scores.
   - Evaluated across multiple classifiers (Linear SVM, Logistic Regression, Naive Bayes, Random Forest) achieving **~90.2% F1-score**.

3. **Domain Issue Categorization**:
   - Automatically maps issues to 6 institutional categories:
     - `Faculty` (Teaching pace, explanations, doubt clarification)
     - `Infrastructure` (Lab equipment, AC, restrooms, projectors, mess food)
     - `Course` (Curriculum relevance, assignment workload, syllabus)
     - `Examination` (Timetable clash, hall tickets, grading, result delays)
     - `Technical` (ERP, LMS, portal crashes, hostel Wi-Fi, login errors)
     - `Administration` (Scholarships, bus transport, fee fines, certificates)

4. **Automated Escalation & Priority Engine**:
   - Automatically detects urgency indicators (*emergency*, *deadline*, *tomorrow*, *harassment*, *failed*, *unhygienic*).
   - Generates priority levels: **High 🚨**, **Medium ⚠️**, **Low 📋**.
   - Dispatches actionable routing directly to the relevant campus authority (IT Support, Exam Cell, Facilities Office, Dean of Academics, Registrar).

5. **Explainable AI (XAI)**:
   - Visualizes exact driving tokens that led to the classification (e.g., *"Negative because of words/phrases: 'not working', 'couldn't complete'"*).
   - Color-coded token pills with attribution scores.

6. **Interactive Management & Escalation Desk**:
   - View, search, and filter escalated complaints by department and status.
   - Update ticket lifecycle: `Open` ➔ `In Progress` ➔ `Resolved`.

7. **Bulk CSV Processing & Export**:
   - Drag-and-drop batch upload of feedback files.
   - One-click export of analyzed records with assigned priorities and department tags.

8. **Live Analytics Dashboard**:
   - Interactive charts powered by Chart.js (Sentiment doughnut, category stacked bars, language distribution, urgency breakdown).

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)

### Windows:
Simply double-click `run.bat` or run:
```powershell
# 1. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate dataset and train models
python dataset\generate_dataset.py
python models\train_models.py

# 4. Start the application
python app.py
```

### Linux / macOS:
```bash
chmod +x run.sh
./run.sh
```

Then open your browser at:
👉 **`http://127.0.0.1:5000`**

---

## 📊 Model Evaluation Benchmark

Trained and cross-validated on domain-specific college feedback:

| Algorithm | Sentiment Accuracy | Sentiment F1 (Weighted) | Category Accuracy | Category F1 (Weighted) | Inference Latency |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Linear SVM (Calibrated)** | **90.3%** | **90.2%** | **93.8%** | **93.9%** | `0.02 ms` |
| **Logistic Regression** | 89.4% | 89.3% | **93.8%** | **93.9%** | `0.01 ms` |
| **Multinomial Naive Bayes** | 90.3% | 90.0% | 90.3% | 90.4% | `<0.01 ms` |
| **Random Forest** | 86.7% | 86.2% | 92.9% | 93.0% | `0.05 ms` |

---

## 📁 Project Structure

```text
smart_feedback_system/
├── app.py                      # Flask backend REST API & Web routes
├── requirements.txt            # Python dependencies
├── run.bat                     # 1-click Windows runner script
├── run.sh                      # 1-click Linux/Mac runner script
├── README.md                   # Complete documentation
├── dataset/
│   ├── generate_dataset.py     # Domain dataset generation script
│   ├── college_feedback_dataset.csv # 560+ curated domain examples
│   └── sample_bulk_test.csv    # Ready-to-use CSV for bulk upload test
├── engine/
│   ├── preprocessor.py         # Language detection & text normalization
│   ├── classifier.py           # Unified inference service
│   ├── explainer.py            # Token-level Explainable AI engine
│   └── escalation_engine.py    # Urgency scoring & departmental routing
├── models/
│   ├── train_models.py         # Multi-classifier training & benchmark
│   ├── sentiment_model.joblib  # Trained Sentiment model
│   ├── category_model.joblib   # Trained Category model
│   └── model_metrics.json      # Benchmark performance statistics
├── database/
│   ├── db.py                   # SQLite schema, CRUD & stats aggregation
│   └── feedback_system.db      # SQLite database file
├── static/
│   ├── css/style.css           # Modern custom styles & badge themes
│   └── js/
│       ├── app.js              # Analyzer, presets, bulk upload & escalation desk
│       └── dashboard.js        # Chart.js visualization engine
└── tests/
    ├── test_pipeline.py        # Pipeline & endpoint integration tests
    └── test_bulk_upload.py     # CSV batch processing test
```

---

## 🔌 REST API Endpoints

- `POST /api/analyze` - Analyze single feedback text (returns sentiment, category, priority, action, XAI tokens).
- `POST /api/upload-csv` - Process a CSV file containing bulk feedback submissions.
- `GET /api/export-csv` - Export enriched feedback dataset as CSV.
- `GET /api/dashboard-stats` - Aggregate metrics, chart matrices, and KPI counters.
- `GET /api/escalations` - Query escalated tickets with status and department filters.
- `POST /api/escalations/<id>/status` - Update ticket status (`Open`, `In Progress`, `Resolved`).
- `GET /api/sample-presets` - Retrieve curated 1-click test examples across languages.
- `GET /api/model-metrics` - Model evaluation and comparison benchmark data.

---

## 🧪 Running Automated Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover tests
```
All unit and integration tests execute in <0.3s.
