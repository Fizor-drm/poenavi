@echo off
chcp 65001 >nul
set "POENAVI_USER_DATA_DIR=%~dp0.dev-user-data"
echo ============================================
echo   PoENavi - Dev Run
echo ============================================
echo User data: %POENAVI_USER_DATA_DIR%
echo.
python main.py
echo.
pause
