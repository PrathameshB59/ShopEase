@echo off
echo ============================================================
echo Starting ShopEase Customer Server (Port 8000)
echo ============================================================
echo.
echo This server handles:
echo   - Customer login and shopping
echo   - Universal login page for ALL users (customers + admins)
echo   - Automatic token-based redirect for admin users to port 8080
echo.
echo Access at: http://127.0.0.1:8000/
echo.

cd /d %~dp0shopease
set DJANGO_SETTINGS_MODULE=config.settings.customer
python manage.py runserver 8000
