@echo off
chcp 65001 >nul
setlocal

set "TEST_CLIENT=%~dp0dist\PoENaviold\PoENavi.exe"
set "POENAVI_USER_DATA_DIR=%~dp0.prerelease-test-user-data"

if not exist "%TEST_CLIENT%" (
    echo ERROR: dist\PoENaviold\PoENavi.exe was not found.
    echo Put the v2.4.0 test client in dist\PoENaviold.
    pause
    exit /b 1
)

set "POENAVI_UPDATE_TEST_TAG=v2.5.0"
if exist "%POENAVI_USER_DATA_DIR%" rmdir /s /q "%POENAVI_USER_DATA_DIR%"
echo Starting PoENavi in pre-release update test mode for v2.5.0.
echo Test user data: %POENAVI_USER_DATA_DIR%
start "" "%TEST_CLIENT%"
