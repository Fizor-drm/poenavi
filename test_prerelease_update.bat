@echo off
chcp 65001 >nul
setlocal

set "TEST_CLIENT=%~dp0dist\PoENaviold\PoENavi.exe"

if not exist "%TEST_CLIENT%" (
    echo ERROR: dist\PoENaviold\PoENavi.exe がありません。
    echo テスト用v2.4.0クライアントを dist\PoENaviold に配置してください。
    pause
    exit /b 1
)

set "POENAVI_UPDATE_TEST_TAG=v2.5.0"
echo Pre-release v2.5.0 を参照するテストモードでPoENaviを起動します。
start "" "%TEST_CLIENT%"
