@echo off
cd /d "C:\Users\admin\Desktop\ai-resume-screening\src"

echo Starting AI Resume Screening System...
echo.

py -m uvicorn app.main:app --reload

pause