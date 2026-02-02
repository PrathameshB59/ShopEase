@echo off
echo Stopping ShopEase services...

REM Kill Gunicorn processes
taskkill /FI "WindowTitle eq ShopEase Customer*" /F
taskkill /FI "WindowTitle eq ShopEase Admin*" /F
taskkill /FI "WindowTitle eq ShopEase Docs*" /F

REM Kill Celery processes
taskkill /FI "WindowTitle eq Celery Worker*" /F
taskkill /FI "WindowTitle eq Celery Beat*" /F
taskkill /FI "WindowTitle eq Celery Flower*" /F

echo All services stopped!
pause
