@echo off
setlocal
title Gayab Hojao Jutsu Cam

cd /d "%~dp0"

echo ========================================================
echo             GAYAB HOJAO JUTSU CAM (गायब हो जाओ)
echo ========================================================
echo.
echo Launching AI Webcam Suite...
echo.

python gayab_cam.py %*

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application exited with error code %errorlevel%.
    pause
)
