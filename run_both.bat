@echo off
echo Starting ShopEase Servers...
echo.

REM Start Admin Server on port 8080
start "ShopEase Admin (8080)" cmd /k "cd /d %~dp0shopease && set DJANGO_SETTINGS_MODULE=config.settings.admin&& python manage.py runserver 8080"

timeout /t 2 /nobreak > nul

REM Start Customer Server on port 8000
start "ShopEase Customer (8000)" cmd /k "cd /d %~dp0shopease && set DJANGO_SETTINGS_MODULE=config.settings.customer&& python manage.py runserver 8000"

timeout /t 4 /nobreak > nul

REM Open browsers
start "" "http://localhost:8000/accounts/auth/"
start "" "http://localhost:8080"

echo.
echo Servers started! Browser windows should open automatically.
