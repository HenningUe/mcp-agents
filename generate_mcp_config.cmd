@echo off
REM MCP Configuration Generator - Batch Script
REM Calls generate_mcp_config.py using the Python executable from .venv

echo.
echo ========================================
echo  MCP Configuration Generator
echo ========================================
echo.

REM Check if .venv directory exists
if not exist ".venv" (
    echo ERROR: Virtual environment not found!
    echo Please create a virtual environment first:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Check if Python executable exists in .venv
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Python executable not found in .venv!
    echo Please ensure the virtual environment is properly created.
    echo.
    pause
    exit /b 1
)

REM Check if generate_mcp_config.py exists
if not exist "generate_mcp_config.py" (
    echo ERROR: generate_mcp_config.py not found!
    echo Please ensure the script is in the current directory.
    echo.
    pause
    exit /b 1
)

REM Run the Python script using the virtual environment
echo Running MCP Configuration Generator...
echo.
".venv\Scripts\python.exe" "generate_mcp_config.py"

REM Check the exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo  Configuration generated successfully!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo  Configuration generation failed!
    echo ========================================
    echo Exit code: %ERRORLEVEL%
)

echo.
echo Press any key to exit...
pause >nul
