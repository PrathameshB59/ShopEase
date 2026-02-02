@echo off
title ShopEase Production Stack
color 0A

echo.
echo ========================================
echo   SHOPEASE PRODUCTION STARTUP
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit
)

REM Activate virtual environment
echo [1/7] Activating virtual environment...
call venv\Scripts\activate

REM Collect static files
echo [2/7] Collecting static files...
cd shopease
python manage.py collectstatic --noinput --clear
cd ..

REM Start customer server with Gunicorn
echo [3/7] Starting Customer Server (Port 8000)...
start "ShopEase Customer" cmd /k "call venv\Scripts\activate && cd shopease && gunicorn -c gunicorn_config.py config.wsgi_customer:application"

timeout /t 3

REM Start admin server with Gunicorn
echo [4/7] Starting Admin Server (Port 8080)...
start "ShopEase Admin" cmd /k "call venv\Scripts\activate && cd shopease && gunicorn -c gunicorn_config_admin.py config.wsgi_admin:application"

timeout /t 3

REM Start docs server with Gunicorn
echo [5/7] Starting Docs Server (Port 9000)...
start "ShopEase Docs" cmd /k "call venv\Scripts\activate && cd shopeasedocs && gunicorn -c gunicorn_config.py shopeasedocs.wsgi:application"

timeout /t 3

REM Start Celery worker
echo [6/7] Starting Celery Worker...
start "Celery Worker" cmd /k "call venv\Scripts\activate && cd shopease && celery -A config worker -l info -P solo"

timeout /t 3

REM Start Celery Beat (scheduler)
echo [7/7] Starting Celery Beat...
start "Celery Beat" cmd /k "call venv\Scripts\activate && cd shopease && celery -A config beat -l info"

echo.
echo ========================================
echo   ALL SERVICES STARTED!
echo ========================================
echo.
echo Customer: http://localhost:8000
echo Admin:    http://localhost:8080
echo Docs:     http://localhost:9000
echo.
echo Press any key to open Flower (Celery monitoring)...
pause
start "Celery Flower" cmd /k "call venv\Scripts\activate && cd shopease && celery -A config flower"

echo.
echo Flower: http://localhost:5555
echo.
pause
