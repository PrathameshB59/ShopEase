@echo off
echo ============================================================
echo Starting ShopEase Admin Server (Port 8080)
echo ============================================================
echo.
echo This server handles:
echo   - Admin dashboard and management
echo   - Auto-login via secure tokens from port 8000
echo   - Independent admin session (shopease_admin_sessionid)
echo.
echo NOTE: Admins should log in at http://127.0.0.1:8000/
echo       (they will be automatically redirected here with a token)
echo.
echo Direct access: http://127.0.0.1:8080/
echo.

cd /d %~dp0shopease
set DJANGO_SETTINGS_MODULE=config.settings.admin
python manage.py runserver 8080
