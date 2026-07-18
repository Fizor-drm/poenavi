@echo off
chcp 65001 >nul
setlocal

set "TEST_CLIENT=%~dp0dist\PoENaviold\PoENavi.exe"

if not exist "%TEST_CLIENT%" (
    echo ERROR: dist\PoENaviold\PoENavi.exe was not found.
    echo Put the v2.4.0 test client in dist\PoENaviold.
    pause
    exit /b 1
)

set "POENAVI_UPDATE_TEST_TAG=v2.5.0"
echo Starting PoENavi in pre-release update test mode for v2.5.0.
start "" "%TEST_CLIENT%"
