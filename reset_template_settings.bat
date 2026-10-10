@echo off
setlocal

REM ============================================================================
REM MAAH LABEL RENDERER
REM RESET ARTWORK SETTINGS
REM ============================================================================

set "PROJECT_DIR=%~dp0"

set "DEFAULT_FILE=%PROJECT_DIR%template_settings.default.json"
set "TARGET_FILE=%PROJECT_DIR%template_settings.json"

set "VENV_PYTHON=%PROJECT_DIR%.venv\Scripts\python.exe"


REM ============================================================================
REM HEADER
REM ============================================================================

echo.
echo ============================================================
echo MAAH LABEL RENDERER - RESET ARTWORK SETTINGS
echo ============================================================
echo.
echo This will restore:
echo.
echo   template_settings.json
echo.
echo to the original factory configuration.
echo.
echo This will remove:
echo.
echo   - Custom global artwork defaults
echo   - All artwork-specific defaults
echo.


REM ============================================================================
REM CHECK REQUIRED FILES
REM ============================================================================

if not exist "%DEFAULT_FILE%" (
    echo ERROR:
    echo template_settings.default.json was not found.
    echo.
    pause
    exit /b 1
)


if not exist "%VENV_PYTHON%" (
    echo ERROR:
    echo Project Python environment was not found.
    echo.
    pause
    exit /b 1
)


REM ============================================================================
REM CONFIRM
REM ============================================================================

choice /C YN /N /M "Continue? [Y/N]: "

if errorlevel 2 (
    echo.
    echo Reset cancelled.
    echo.
    pause
    exit /b 0
)


REM ============================================================================
REM VALIDATE DEFAULT FILE BEFORE RESTORE
REM ============================================================================

"%VENV_PYTHON%" -c "from template_settings_store import load_template_settings_store; load_template_settings_store(r'%DEFAULT_FILE%'); print('Default artwork settings validation: OK')"

if errorlevel 1 (
    echo.
    echo ============================================================
    echo RESET ABORTED
    echo ============================================================
    echo.
    echo template_settings.default.json failed validation.
    echo template_settings.json was NOT modified.
    echo.
    pause
    exit /b 1
)


REM ============================================================================
REM RESTORE DEFAULT FILE
REM ============================================================================

copy /y ^
    "%DEFAULT_FILE%" ^
    "%TARGET_FILE%" ^
    >nul

if errorlevel 1 (
    echo.
    echo ERROR:
    echo Could not restore template_settings.json.
    echo.
    pause
    exit /b 1
)


REM ============================================================================
REM VALIDATE RESTORED FILE
REM ============================================================================

"%VENV_PYTHON%" -c "from template_settings_store import load_template_settings_store; load_template_settings_store(r'%TARGET_FILE%'); print('Restored artwork settings validation: OK')"

if errorlevel 1 (
    echo.
    echo ============================================================
    echo RESET FAILED
    echo ============================================================
    echo.
    echo The file was restored but failed validation.
    echo.
    pause
    exit /b 1
)


REM ============================================================================
REM DONE
REM ============================================================================

echo.
echo ============================================================
echo ARTWORK SETTINGS RESTORED
echo ============================================================
echo.
echo Global defaults:
echo.
echo   Scale      : 95.0%%
echo   Background : #FFFFFF
echo   Bleed      : 1.0 mm
echo.
echo Artwork-specific defaults:
echo.
echo   None
echo.

pause

endlocal