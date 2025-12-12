@echo off
cd /d "%~dp0"
call .venv\Scripts\activate
echo Starting Django Server on 0.0.0.0:8010...
python manage.py runserver 0.0.0.0:8010
if errorlevel 1 (
    echo.
    echo Server crashed!
    pause
)
