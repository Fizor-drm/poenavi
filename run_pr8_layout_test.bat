@echo off
chcp 65001 >nul
setlocal
pushd "%~dp0"

set "POENAVI_USER_DATA_DIR=%~dp0..\poenavi-dev-pr8-test\.prerelease-test-user-data"
set "VENV_DIR=%~dp0..\poenavi-dev-pr8-test\.venv-pr8-test"
set "PYTHON=%VENV_DIR%\Scripts\python.exe"

echo ============================================
echo   PoENavi PR #8 - Layout Polish Test
echo   Base: 3f80f76
echo ============================================
echo.
echo Existing PR #8 test data will be reused.
echo User data: %POENAVI_USER_DATA_DIR%
echo.

if not exist "%PYTHON%" (
    echo Creating an isolated Python environment...
    py -3 -m venv "%VENV_DIR%"
    if errorlevel 1 goto :error
)

echo Checking dependencies...
"%PYTHON%" -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 goto :error

echo Starting PoENavi...
"%PYTHON%" main.py
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" goto :error_with_code

popd
exit /b 0

:error_with_code
echo.
echo PoENavi exited with code %EXIT_CODE%.
goto :pause_error

:error
echo.
echo Failed to prepare the layout test environment.

:pause_error
echo Copy or screenshot the error shown above.
pause
popd
exit /b 1
