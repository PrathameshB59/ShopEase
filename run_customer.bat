@echo off
echo Starting ShopEase Customer Server on port 8000...
echo.

cd /d %~dp0shopease
set DJANGO_SETTINGS_MODULE=config.settings.customer
python manage.py runserver 8000
