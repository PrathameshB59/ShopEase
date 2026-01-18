@echo off
echo Starting ShopEase Admin Server on port 8080...
echo.

cd /d %~dp0shopease
set DJANGO_SETTINGS_MODULE=config.settings.admin
python manage.py runserver 8080
