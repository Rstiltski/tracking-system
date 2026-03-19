@echo off
echo Starting Veryfyn Tracking System...
echo ===================================
echo [1/3] Starting Streamlit App (Core UI)...
start cmd /k "cd /d c:\Users\Rstiltki\.gemini\antigravity\scratch\tracking-system && .\.venv\Scripts\activate.bat && streamlit run tracking_app\app.py"

echo [2/3] Starting FastAPI Backend (API)...
start cmd /k "cd /d c:\Users\Rstiltki\.gemini\antigravity\scratch\tracking-system && .\.venv\Scripts\activate.bat && set PYTHONPATH=. && uvicorn backend.main:app --reload --port 8000"

echo [3/3] Starting React Frontend...
start cmd /k "cd /d c:\Users\Rstiltki\.gemini\antigravity\scratch\tracking-system\frontend && set PATH=c:\Users\Rstiltki\.gemini\antigravity\scratch\tracking-system\frontend\node-v20.11.1-win-x64;%PATH% && npm run dev"

echo All services have been launched in separate windows!
echo It is safe to close this small launcher window now.
