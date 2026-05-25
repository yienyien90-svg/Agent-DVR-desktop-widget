@echo off
cd /d "%~dp0dist\AgentDVR_Widget"
if not exist "AgentDVR_Widget.exe" (
    echo Executable introuvable. Lancez d'abord build.bat pour compiler le projet.
    pause
    exit /b 1
)
start "" "AgentDVR_Widget.exe"
