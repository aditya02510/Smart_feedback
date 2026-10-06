#!/usr/bin/env bash
echo "========================================================"
echo " Smart Feedback Sentiment Analysis & Escalation System"
echo "========================================================"
echo ""

if [ ! -d ".venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv .venv
    echo "[INFO] Installing requirements..."
    .venv/bin/pip install -r requirements.txt
    echo "[INFO] Generating dataset and training models..."
    .venv/bin/python dataset/generate_dataset.py
    .venv/bin/python models/train_models.py
fi

echo "[INFO] Starting Flask Server on http://127.0.0.1:5000..."
.venv/bin/python app.py
