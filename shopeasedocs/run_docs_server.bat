@echo off
REM ShopEase Documentation Server
REM This script runs the documentation project on port 9000

echo ====================================
echo ShopEase Documentation Server
echo Running on http://127.0.0.1:9000
echo ====================================
echo.

python manage.py runserver 9000
