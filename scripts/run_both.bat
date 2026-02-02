@echo off
echo ============================================================
echo Starting ShopEase Dual-Server Architecture
echo ============================================================
echo.
echo PORT 8000: Customer Server + Universal Login
echo   - All users (customers AND admins) log in here
echo   - Admins are auto-redirected to port 8080 via secure token
echo.
echo PORT 8080: Admin Dashboard Server
echo   - Admin management interface
echo   - Auto-login from port 8000 (no manual login needed)
echo.
echo ============================================================
echo.

REM Start Admin Server on port 8080
echo Starting Admin Server (8080)...
start "ShopEase Admin (8080)" cmd /k "cd /d %~dp0shopease && set DJANGO_SETTINGS_MODULE=config.settings.admin&& python manage.py runserver 8080"

timeout /t 2 /nobreak > nul

REM Start Customer Server on port 8000 (Universal Login)
echo Starting Customer Server (8000) - Universal Login...
start "ShopEase Customer (8000)" cmd /k "cd /d %~dp0shopease && set DJANGO_SETTINGS_MODULE=config.settings.customer&& python manage.py runserver 8000"

timeout /t 4 /nobreak > nul

REM Open browser to universal login page
echo.
echo Opening universal login page at http://localhost:8000/
echo.
echo IMPORTANT: ALL users should log in at port 8000
echo   - Customers: Will stay on port 8000
echo   - Admins: Will auto-redirect to port 8080 with secure token
echo.
start "" "http://localhost:8000/"

echo.
echo ============================================================
echo Servers started successfully!
echo ============================================================
echo.
echo Access points:
echo   Universal Login: http://127.0.0.1:8000/
echo   Admin Dashboard: http://127.0.0.1:8080/ (login at port 8000 first)
echo.
echo Press Ctrl+C in the server windows to stop the servers.
echo ============================================================
