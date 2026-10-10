@echo off
setlocal

REM ============================================================================
REM MAAH LABEL RENDERER
REM RESET LABEL FORMATS
REM ============================================================================

set "PROJECT_DIR=%~dp0"
set "DEFAULT_FILE=%PROJECT_DIR%label_formats.default.json"
set "TARGET_FILE=%PROJECT_DIR%label_formats.json"
set "VALIDATOR=%PROJECT_DIR%validate_label_formats.bat"


echo.
echo ============================================================
echo MAAH LABEL RENDERER - RESET LABEL FORMATS
echo ============================================================
echo.
echo This will replace:
echo.
echo   label_formats.json
echo.
echo with the original default configuration.
echo.
echo Any custom formats or calibration changes will be lost.
echo.

choice /C YN /N /M "Continue? [Y/N]: "

if errorlevel 2 (
    echo.
    echo Reset cancelled.
    echo.
    pause
    exit /b 0
)


REM ============================================================================
REM CHECK DEFAULT FILE
REM ============================================================================

if not exist "%DEFAULT_FILE%" (
    echo.
    echo ERROR:
    echo Default label format file was not found:
    echo.
    echo %DEFAULT_FILE%
    echo.
    pause
    exit /b 1
)


REM ============================================================================
REM RESTORE DEFAULT
REM ============================================================================

copy /y "%DEFAULT_FILE%" "%TARGET_FILE%" >nul

if errorlevel 1 (
    echo.
    echo ERROR:
    echo Could not restore label_formats.json.
    echo.
    pause
    exit /b 1
)


echo.
echo label_formats.json restored successfully.
echo.


REM ============================================================================
REM VALIDATE RESTORED FILE
REM ============================================================================

if exist "%VALIDATOR%" (

    echo Running validation...
    echo.

    call "%VALIDATOR%"

    if errorlevel 1 (
        echo.
        echo ============================================================
        echo RESET COMPLETED BUT VALIDATION FAILED
        echo ============================================================
        echo.
        pause
        exit /b 1
    )

) else (

    echo WARNING:
    echo validate_label_formats.bat was not found.
    echo Validation was skipped.
    echo.

)


REM ============================================================================
REM DONE
REM ============================================================================

echo.
echo ============================================================
echo LABEL FORMATS RESTORED
echo ============================================================
echo.
echo label_formats.json is back to the original configuration.
echo.

pause

endlocal