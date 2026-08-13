@echo off
setlocal
cd /d "%~dp0.."
title DD_Style - Project ZIP
python "%~dp0zip_project.py"
if errorlevel 1 (
    echo.
    echo [ERROR] ZIP creation failed.
    pause
    exit /b 1
)
echo.
echo [DONE] ZIP created under release\
pause
endlocal
