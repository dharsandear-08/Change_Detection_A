@echo off
setlocal
cd /d "%~dp0.."
title DD_Style - Universal Project Tools

echo ============================================================
echo DD_STYLE UNIVERSAL PROJECT TOOLS
echo ============================================================
echo Project Root: %CD%
echo.

echo [1/2] Creating project snapshot...
python "%~dp0folder_to_txt.py"
if errorlevel 1 (
    echo.
    echo [ERROR] Snapshot creation failed. ZIP will not be created.
    pause
    exit /b 1
)

echo.
echo [2/2] Creating project ZIP...
python "%~dp0zip_project.py"
if errorlevel 1 (
    echo.
    echo [ERROR] ZIP creation failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo DD_STYLE RUN COMPLETE
echo ============================================================
echo Snapshot: ProjectSnapshot.txt
echo Release : release\
echo.
pause
endlocal
