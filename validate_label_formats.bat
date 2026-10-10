@echo off
setlocal

REM ============================================================================
REM MAAH LABEL RENDERER
REM LABEL FORMAT VALIDATION
REM ============================================================================

set "PROJECT_DIR=%~dp0"
set "VENV_PYTHON=%PROJECT_DIR%.venv\Scripts\python.exe"
set "VALIDATOR=%PROJECT_DIR%validate_label_formats.py"


echo.
echo ============================================================
echo MAAH LABEL RENDERER - LABEL FORMAT VALIDATION
echo ============================================================
echo.


REM ============================================================================
REM CHECK PYTHON ENVIRONMENT
REM ============================================================================

if not exist "%VENV_PYTHON%" (
    echo ERROR:
    echo Virtual environment Python was not found:
    echo.
    echo %VENV_PYTHON%
    echo.
    pause
    exit /b 1
)


REM ============================================================================
REM CHECK VALIDATOR
REM ============================================================================

if not exist "%VALIDATOR%" (
    echo ERROR:
    echo Validator was not found:
    echo.
    echo %VALIDATOR%
    echo.
    pause
    exit /b 1
)


REM ============================================================================
REM RUN VALIDATION
REM ============================================================================

"%VENV_PYTHON%" "%VALIDATOR%"

set "VALIDATION_RESULT=%ERRORLEVEL%"


REM ============================================================================
REM RESULT
REM ============================================================================

if not "%VALIDATION_RESULT%"=="0" (

    echo.
    echo ============================================================
    echo VALIDATION FAILED
    echo ============================================================
    echo.

    pause

    exit /b %VALIDATION_RESULT%
)


echo.
echo ============================================================
echo VALIDATION COMPLETE
echo ============================================================
echo.


pause

endlocal