@echo off
setlocal
cd /d "%~dp0.."
title DD_Style - Folder To TXT
python "%~dp0folder_to_txt.py"
if errorlevel 1 (
    echo.
    echo [ERROR] Snapshot creation failed.
    pause
    exit /b 1
)
echo.
echo [DONE] ProjectSnapshot.txt created.
pause
endlocal
