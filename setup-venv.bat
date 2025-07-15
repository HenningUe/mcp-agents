@echo off
REM MCP Virtual Environment Setup - Batch Script
REM Calls setup-venv.ps1 PowerShell script to create .venv

echo.
echo ========================================
echo  MCP Virtual Environment Setup
echo ========================================
echo.

REM Check if setup-venv.ps1 exists
if not exist "setup-venv.ps1" (
    echo ERROR: setup-venv.ps1 not found!
    echo Please ensure the PowerShell script is in the current directory.
    echo.
    pause
    exit /b 1
)

REM Check if PowerShell is available
where powershell.exe >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PowerShell not found!
    echo Please ensure PowerShell is installed and available in PATH.
    echo.
    pause
    exit /b 1
)

REM Check PowerShell execution policy
echo Checking PowerShell execution policy...
powershell.exe -Command "Get-ExecutionPolicy" | findstr /i "restricted" >nul
if %ERRORLEVEL% EQU 0 (
    echo.
    echo WARNING: PowerShell execution policy is restricted!
    echo This may prevent the script from running.
    echo.
    echo To fix this, run PowerShell as Administrator and execute:
    echo   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    echo.
    echo Do you want to continue anyway? (y/N)
    set /p continue=
    if /i not "%continue%"=="y" (
        echo Operation cancelled.
        pause
        exit /b 1
    )
)

REM Run the PowerShell script
echo Running PowerShell setup script...
echo.
powershell.exe -ExecutionPolicy Bypass -File "setup-venv.ps1"

REM Check the exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo  Virtual Environment Setup Complete!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo  Virtual Environment Setup Failed!
    echo ========================================
    echo Exit code: %ERRORLEVEL%
    echo.
    echo Common issues:
    echo - PowerShell execution policy restrictions
    echo - Python not found or not properly installed
    echo - Insufficient permissions
    echo.
    echo Try running as Administrator or check the PowerShell script output above.
)

echo.
echo Press any key to exit...
pause >nul
