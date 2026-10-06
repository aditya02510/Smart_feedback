@echo off
echo ========================================================
echo  Smart Feedback Sentiment Analysis & Escalation System
echo ========================================================
echo.

IF NOT EXIST ".venv\Scripts\python.exe" (
    echo [INFO] Virtual environment not found. Setting up .venv...
    python -m venv .venv
    echo [INFO] Installing requirements...
    .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    echo [INFO] Training ML models...
    .\.venv\Scripts\python.exe dataset\generate_dataset.py
    .\.venv\Scripts\python.exe models\train_models.py
)

echo [INFO] Starting Flask Server on http://127.0.0.1:5000...
echo Open your browser and navigate to http://127.0.0.1:5000
echo.
.\.venv\Scripts\python.exe app.py
pause
