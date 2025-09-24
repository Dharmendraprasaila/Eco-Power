@echo off
echo ========================================
echo   Solar Energy Management System
echo   5-Hour Hackathon Production Setup
echo ========================================
echo.

echo [1/5] Setting up Python environment...
cd backend
python -m pip install -r requirements.txt
echo.

echo [2/5] Setting up database...
python ..\database\init_db.py
echo.

echo [3/5] Starting Flask backend...
start "Flask Backend" python app.py
echo Backend started on http://localhost:5000
echo.

echo [4/5] Setting up React frontend...
cd ..\frontend
call npm install
echo.

echo [5/5] Starting React frontend...
start "React Frontend" npm run dev
echo Frontend will start on http://localhost:3000
echo.

echo ========================================
echo   System Setup Complete!
echo ========================================
echo.
echo Backend API: http://localhost:5000
echo Frontend UI: http://localhost:3000
echo.
echo Next steps:
echo 1. Configure API keys in backend/.env
echo 2. Run data simulator: python backend/data_simulator.py
echo 3. Open http://localhost:3000 in browser
echo.
pause