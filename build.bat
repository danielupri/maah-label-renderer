@echo off
setlocal EnableExtensions

REM ============================================================================
REM MAAH LABEL RENDERER
REM PRODUCTION BUILD
REM ============================================================================


REM ============================================================================
REM PATHS
REM ============================================================================

set "PROJECT_DIR=%~dp0"

set "VENV_PYTHON=%PROJECT_DIR%.venv\Scripts\python.exe"

set "BUILD_DIR=%PROJECT_DIR%build"
set "DIST_DIR=%PROJECT_DIR%dist"

set "APP_NAME=MAAH Label Renderer"
set "APP_DIST=%DIST_DIR%\%APP_NAME%"

set "BACKUP_DIR=%PROJECT_DIR%_build_backup"

set "ICON_FILE=%PROJECT_DIR%maah.ico"


REM ============================================================================
REM DEFAULT BUILD MODES
REM ============================================================================

set "INPUT_MODE=PROJECT"
set "TEMPLATES_MODE=PROJECT"


REM ============================================================================
REM HEADER
REM ============================================================================

echo.
echo ============================================================
echo MAAH LABEL RENDERER - PRODUCTION BUILD
echo ============================================================
echo.


REM ============================================================================
REM CHECK PYTHON ENVIRONMENT
REM ============================================================================

if not exist "%VENV_PYTHON%" (

    echo ERROR:
    echo Python virtual environment was not found.
    echo.
    echo Expected:
    echo %VENV_PYTHON%
    echo.

    pause
    exit /b 1
)


REM ============================================================================
REM CHECK REQUIRED PROJECT FILES
REM ============================================================================

if not exist "%PROJECT_DIR%app.py" (
    echo ERROR: app.py not found.
    pause
    exit /b 1
)

if not exist "%PROJECT_DIR%config.json" (
    echo ERROR: config.json not found.
    pause
    exit /b 1
)

if not exist "%PROJECT_DIR%label_formats.json" (
    echo ERROR: label_formats.json not found.
    pause
    exit /b 1
)

if not exist "%PROJECT_DIR%label_formats.default.json" (
    echo ERROR: label_formats.default.json not found.
    pause
    exit /b 1
)

if not exist "%PROJECT_DIR%mappings.json" (
    echo ERROR: mappings.json not found.
    pause
    exit /b 1
)

if not exist "%PROJECT_DIR%template_settings.json" (
    echo ERROR: template_settings.json not found.
    pause
    exit /b 1
)

if not exist "%PROJECT_DIR%template_settings.default.json" (
    echo ERROR: template_settings.default.json not found.
    pause
    exit /b 1
)

if not exist "%ICON_FILE%" (
    echo ERROR: maah.ico not found.
    pause
    exit /b 1
)


REM ============================================================================
REM ASK HOW TO HANDLE EXISTING PRODUCTION INPUT
REM ============================================================================

if exist "%APP_DIST%\input" (

    echo Existing production input folder detected.
    echo.
    echo [K] Keep current production input
    echo [R] Restore input from project folder
    echo.

    choice /C KR /N /M "Input folder [K/R]: "

    if errorlevel 2 (
        set "INPUT_MODE=PROJECT"
    ) else (
        set "INPUT_MODE=KEEP"
    )

    echo.
)


REM ============================================================================
REM ASK HOW TO HANDLE EXISTING PRODUCTION TEMPLATES
REM ============================================================================

if exist "%APP_DIST%\templates" (

    echo Existing production templates folder detected.
    echo.
    echo [K] Keep current production templates
    echo [R] Restore templates from project folder
    echo.

    choice /C KR /N /M "Templates folder [K/R]: "

    if errorlevel 2 (
        set "TEMPLATES_MODE=PROJECT"
    ) else (
        set "TEMPLATES_MODE=KEEP"
    )

    echo.
)


REM ============================================================================
REM CLEAR OLD TEMPORARY BACKUP
REM ============================================================================

if exist "%BACKUP_DIR%" (

    rmdir /s /q "%BACKUP_DIR%"
)


mkdir "%BACKUP_DIR%" >nul 2>&1


REM ============================================================================
REM BACK UP PRODUCTION MAPPINGS
REM ============================================================================

if exist "%APP_DIST%\mappings.json" (

    echo Preserving production mappings.json...

    copy /y ^
        "%APP_DIST%\mappings.json" ^
        "%BACKUP_DIR%\mappings.json" ^
        >nul
)


REM ============================================================================
REM BACK UP PRODUCTION ARTWORK SETTINGS
REM ============================================================================

if exist "%APP_DIST%\template_settings.json" (

    echo Preserving production template_settings.json...

    copy /y ^
        "%APP_DIST%\template_settings.json" ^
        "%BACKUP_DIR%\template_settings.json" ^
        >nul
)


REM ============================================================================
REM BACK UP PRODUCTION OUTPUT
REM ============================================================================

if exist "%APP_DIST%\output" (

    echo Preserving production output...

    mkdir "%BACKUP_DIR%\output" >nul 2>&1

    xcopy ^
        "%APP_DIST%\output\*" ^
        "%BACKUP_DIR%\output\" ^
        /E /I /Y /Q ^
        >nul
)


REM ============================================================================
REM BACK UP INPUT IF USER SELECTED KEEP
REM ============================================================================

if /I "%INPUT_MODE%"=="KEEP" (

    if exist "%APP_DIST%\input" (

        echo Preserving production input...

        mkdir "%BACKUP_DIR%\input" >nul 2>&1

        xcopy ^
            "%APP_DIST%\input\*" ^
            "%BACKUP_DIR%\input\" ^
            /E /I /Y /Q ^
            >nul
    )
)


REM ============================================================================
REM BACK UP TEMPLATES IF USER SELECTED KEEP
REM ============================================================================

if /I "%TEMPLATES_MODE%"=="KEEP" (

    if exist "%APP_DIST%\templates" (

        echo Preserving production templates...

        mkdir "%BACKUP_DIR%\templates" >nul 2>&1

        xcopy ^
            "%APP_DIST%\templates\*" ^
            "%BACKUP_DIR%\templates\" ^
            /E /I /Y /Q ^
            >nul
    )
)


REM ============================================================================
REM CLEAN OLD BUILD
REM ============================================================================

echo.
echo Cleaning previous build...
echo.

if exist "%BUILD_DIR%" (

    rmdir /s /q "%BUILD_DIR%"
)


if exist "%DIST_DIR%" (

    rmdir /s /q "%DIST_DIR%"
)


REM ============================================================================
REM BUILD APPLICATION
REM ============================================================================

echo ============================================================
echo BUILDING APPLICATION
echo ============================================================
echo.

"%VENV_PYTHON%" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --windowed ^
    --onedir ^
    --name "%APP_NAME%" ^
    --icon "%ICON_FILE%" ^
    "%PROJECT_DIR%app.py"


if errorlevel 1 (

    echo.
    echo ============================================================
    echo BUILD FAILED
    echo ============================================================
    echo.
    echo Production data backup was NOT deleted.
    echo.
    echo Backup location:
    echo %BACKUP_DIR%
    echo.

    pause
    exit /b 1
)


REM ============================================================================
REM VERIFY BUILD OUTPUT
REM ============================================================================

if not exist "%APP_DIST%\%APP_NAME%.exe" (

    echo.
    echo ERROR:
    echo PyInstaller finished but the application EXE was not found.
    echo.
    echo Expected:
    echo %APP_DIST%\%APP_NAME%.exe
    echo.

    pause
    exit /b 1
)


REM ============================================================================
REM COPY CORE CONFIGURATION
REM ============================================================================

echo.
echo Copying application configuration...
echo.

copy /y ^
    "%PROJECT_DIR%config.json" ^
    "%APP_DIST%\config.json" ^
    >nul


copy /y ^
    "%PROJECT_DIR%label_formats.json" ^
    "%APP_DIST%\label_formats.json" ^
    >nul


copy /y ^
    "%PROJECT_DIR%label_formats.default.json" ^
    "%APP_DIST%\label_formats.default.json" ^
    >nul


copy /y ^
    "%PROJECT_DIR%template_settings.default.json" ^
    "%APP_DIST%\template_settings.default.json" ^
    >nul


copy /y ^
    "%ICON_FILE%" ^
    "%APP_DIST%\maah.ico" ^
    >nul


REM ============================================================================
REM COPY DOCUMENTATION
REM ============================================================================

if exist "%PROJECT_DIR%MAAH_Label_Renderer_Documentation.html" (

    copy /y ^
        "%PROJECT_DIR%MAAH_Label_Renderer_Documentation.html" ^
        "%APP_DIST%\MAAH_Label_Renderer_Documentation.html" ^
        >nul
)


if exist "%PROJECT_DIR%README_LABEL_FORMATS.txt" (

    copy /y ^
        "%PROJECT_DIR%README_LABEL_FORMATS.txt" ^
        "%APP_DIST%\README_LABEL_FORMATS.txt" ^
        >nul
)


REM ============================================================================
REM RESTORE / INITIALIZE MAPPINGS
REM ============================================================================

if exist "%BACKUP_DIR%\mappings.json" (

    echo Restoring production mappings.json...

    copy /y ^
        "%BACKUP_DIR%\mappings.json" ^
        "%APP_DIST%\mappings.json" ^
        >nul

) else (

    echo Installing project mappings.json...

    copy /y ^
        "%PROJECT_DIR%mappings.json" ^
        "%APP_DIST%\mappings.json" ^
        >nul
)


REM ============================================================================
REM RESTORE / INITIALIZE ARTWORK SETTINGS
REM ============================================================================

if exist "%BACKUP_DIR%\template_settings.json" (

    echo Restoring production template_settings.json...

    copy /y ^
        "%BACKUP_DIR%\template_settings.json" ^
        "%APP_DIST%\template_settings.json" ^
        >nul

) else (

    echo Installing project template_settings.json...

    copy /y ^
        "%PROJECT_DIR%template_settings.json" ^
        "%APP_DIST%\template_settings.json" ^
        >nul
)


REM ============================================================================
REM RESTORE OUTPUT
REM ============================================================================

mkdir "%APP_DIST%\output" >nul 2>&1


if exist "%BACKUP_DIR%\output" (

    echo Restoring production output...

    xcopy ^
        "%BACKUP_DIR%\output\*" ^
        "%APP_DIST%\output\" ^
        /E /I /Y /Q ^
        >nul
)


REM ============================================================================
REM RESTORE / INSTALL INPUT
REM ============================================================================

mkdir "%APP_DIST%\input" >nul 2>&1


if /I "%INPUT_MODE%"=="KEEP" (

    if exist "%BACKUP_DIR%\input" (

        echo Restoring production input...

        xcopy ^
            "%BACKUP_DIR%\input\*" ^
            "%APP_DIST%\input\" ^
            /E /I /Y /Q ^
            >nul
    )

) else (

    if exist "%PROJECT_DIR%input" (

        echo Installing project input...

        xcopy ^
            "%PROJECT_DIR%input\*" ^
            "%APP_DIST%\input\" ^
            /E /I /Y /Q ^
            >nul
    )
)


REM ============================================================================
REM RESTORE / INSTALL TEMPLATES
REM ============================================================================

mkdir "%APP_DIST%\templates" >nul 2>&1


if /I "%TEMPLATES_MODE%"=="KEEP" (

    if exist "%BACKUP_DIR%\templates" (

        echo Restoring production templates...

        xcopy ^
            "%BACKUP_DIR%\templates\*" ^
            "%APP_DIST%\templates\" ^
            /E /I /Y /Q ^
            >nul
    )

) else (

    if exist "%PROJECT_DIR%templates" (

        echo Installing project templates...

        xcopy ^
            "%PROJECT_DIR%templates\*" ^
            "%APP_DIST%\templates\" ^
            /E /I /Y /Q ^
            >nul
    )
)


REM ============================================================================
REM DELETE TEMPORARY BACKUP
REM ============================================================================

if exist "%BACKUP_DIR%" (

    rmdir /s /q "%BACKUP_DIR%"
)


REM ============================================================================
REM DONE
REM ============================================================================

echo.
echo ============================================================
echo BUILD COMPLETE
echo ============================================================
echo.
echo Application:
echo %APP_DIST%\%APP_NAME%.exe
echo.
echo Preserved:
echo   mappings.json
echo   template_settings.json
echo   output\
echo.
echo Configurable during build:
echo   input\
echo   templates\
echo.
echo Replaced from project:
echo   config.json
echo   label_formats.json
echo   label_formats.default.json
echo   template_settings.default.json
echo   maah.ico
echo   documentation
echo.
echo IMPORTANT:
echo The complete "%APP_NAME%" folder must be distributed.
echo Do not move only the EXE.
echo.
echo Inkscape must be installed on the target computer
echo for PDF export.
echo.


REM ============================================================================
REM OPEN FINAL DISTRIBUTION FOLDER
REM ============================================================================

start "" "%APP_DIST%"


pause

endlocal