@echo off
REM This script activates the Python virtual environment and runs the C5.1_Harvester main script.

REM Set the path to your project folder within My Documents
set "PROJECT_DIR=%USERPROFILE%\Documents\COUNTER_Harvester\C5.1_Harvester"

REM --- SCRIPT START ---

echo.
echo Locating project directory...

REM Check if the project directory actually exists
IF NOT EXIST "%PROJECT_DIR%" (
    echo ERROR: Project directory not found at "%PROJECT_DIR%"
    echo Please make sure the folder exists and the script is in the correct location.
    echo.
    pause
    exit /b 1
)

echo Project directory found.
echo.
echo Activating the Python virtual environment...

REM Activate the virtual environment. We use CALL to ensure the script continues after activation.
CALL "%PROJECT_DIR%\venv\Scripts\activate.bat"

REM Check if the venv was activated successfully (the _VENV_ACTIVATED flag is set by some venvs)
IF NOT DEFINED VIRTUAL_ENV (
    echo WARNING: The virtual environment may not have been activated correctly.
    echo Attempting to proceed anyway...
) else (
    echo Virtual environment activated.
)

echo.
echo Changing directory to the 'src' folder...

REM Change the current directory to the 'src' subfolder
cd /d "%PROJECT_DIR%\src"

echo Now in directory: %CD%
echo.
echo Running the main Python script (main.py)...
echo --------------------------------------------
echo.

REM Run the main Python script.
REM Using 'python' is often sufficient after venv activation, but 'python3' is used as requested.
python3 main.py

echo.
echo --------------------------------------------
echo Script finished.

REM The 'pause' command will keep the window open so you can see any output or errors.
pause
