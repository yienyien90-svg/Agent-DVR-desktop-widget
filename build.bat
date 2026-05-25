@echo off
setlocal
cd /d "%~dp0"

echo Installation des dependances...
python -m pip install -r requirements.txt -q

echo.
echo Generation de l'icone...
python create_icon.py

echo.
echo Compilation en cours (peut prendre plusieurs minutes)...
python -m PyInstaller --noconfirm --clean agent_dvr_widget.spec

if errorlevel 1 (
    echo.
    echo ERREUR : la compilation a echoue.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Compilation terminee !
echo  Lancez : dist\AgentDVR_Widget\AgentDVR_Widget.exe
echo ========================================
pause
