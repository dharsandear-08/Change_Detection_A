@echo off
setlocal
cd /d "%~dp0.."
title DD_Style - TXT To Folder
python "%~dp0txt_to_folder.py"
if errorlevel 1 (
    echo.
    echo [ERROR] Project restore failed.
    pause
    exit /b 1
)
echo.
echo [DONE] Project restored successfully.
pause
endlocal
