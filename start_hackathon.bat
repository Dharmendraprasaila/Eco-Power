@echo off
echo Killing processes on ports 3000 and 5000...

REM Kill processes on port 3000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do (
    taskkill /PID %%a /F >nul 2>&1
)

REM Kill processes on port 5000  
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo Ports cleared!
echo.

echo Starting Backend on port 5000...
cd backend
start "Solar Backend" python simple_app.py

echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak >nul

echo Starting Frontend on port 3000...
cd ..\frontend
start "Solar Frontend" npm run dev

echo.
echo ========================================
echo   Solar Energy System Started!
echo ========================================
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo Reports: http://localhost:3000/reports
echo ========================================
echo.
pause