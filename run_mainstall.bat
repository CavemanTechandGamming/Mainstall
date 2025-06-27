@echo off
REM Mainstall Launcher
REM This batch file launches the Mainstall application

echo Starting Mainstall...
echo.

REM Check if executable exists
if not exist "dist\Mainstall.exe" (
    echo ERROR: Mainstall.exe not found in dist folder!
    echo Please build the application first using: pyinstaller mainstall.spec
    pause
    exit /b 1
)

REM Launch the application
start "" "dist\Mainstall.exe"

echo Mainstall launched successfully!
timeout /t 2 >nul 