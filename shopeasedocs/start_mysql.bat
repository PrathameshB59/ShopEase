@echo off
echo ====================================
echo Starting MySQL Service
echo ====================================
echo.

net start MySQL80

if %errorlevel% == 0 (
    echo.
    echo ====================================
    echo MySQL Started Successfully!
    echo ====================================
    echo.
    echo Your documentation server should now connect automatically.
    echo Server is running at: http://127.0.0.1:9000
    echo.
) else (
    echo.
    echo ====================================
    echo ERROR: Failed to start MySQL
    echo ====================================
    echo.
    echo Please run this script as Administrator:
    echo   1. Right-click on start_mysql.bat
    echo   2. Select "Run as administrator"
    echo.
)

pause
