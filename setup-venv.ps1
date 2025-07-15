# MCP Virtual Environment Setup Script
# Creates a .venv virtual environment based on user's Python installation

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MCP Virtual Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to test if Python executable exists and get version
function Test-PythonExecutable {
    param([string]$PythonPath)
    
    if (-not (Test-Path $PythonPath)) {
        return $false
    }
    
    try {
        $version = & $PythonPath --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Found Python: $version" -ForegroundColor Green
            return $true
        }
    }
    catch {
        return $false
    }
    
    return $false
}

# Function to find common Python installations
function Find-CommonPythonPaths {
    $commonPaths = @(
        "C:\Python313\python.exe",
        "C:\Python312\python.exe",
        "C:\Python311\python.exe",
        "C:\Python310\python.exe",
        "C:\Python39\python.exe",
        "C:\Python38\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python39\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python38\python.exe"
    )
    
    $foundPaths = @()
    foreach ($path in $commonPaths) {
        if (Test-PythonExecutable $path) {
            $foundPaths += $path
        }
    }
    
    return $foundPaths
}

# Check if .venv already exists
if (Test-Path ".venv") {
    Write-Host "⚠️  Virtual environment already exists!" -ForegroundColor Yellow
    $response = Read-Host "Do you want to remove it and create a new one? (y/N)"
    if ($response -match "^[Yy]$") {
        Write-Host "Removing existing .venv directory..." -ForegroundColor Yellow
        Remove-Item ".venv" -Recurse -Force
        Write-Host "✓ Removed existing virtual environment" -ForegroundColor Green
    }
    else {
        Write-Host "Operation cancelled." -ForegroundColor Red
        exit 1
    }
}

# Try to find Python in PATH first
Write-Host "Checking for Python in PATH..." -ForegroundColor Cyan
try {
    $pythonInPath = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonInPath -and (Test-PythonExecutable $pythonInPath.Source)) {
        Write-Host "✓ Found Python in PATH: $($pythonInPath.Source)" -ForegroundColor Green
        $defaultPython = $pythonInPath.Source
    }
}
catch {
    $defaultPython = $null
}

# Find common Python installations
Write-Host "Searching for Python installations..." -ForegroundColor Cyan
$foundPythons = Find-CommonPythonPaths

if ($foundPythons.Count -gt 0) {
    Write-Host "Found Python installations:" -ForegroundColor Green
    for ($i = 0; $i -lt $foundPythons.Count; $i++) {
        Write-Host "  $($i + 1). $($foundPythons[$i])" -ForegroundColor White
    }
    Write-Host ""
}

# Ask user for Python path
Write-Host "Please specify the Python executable to use:" -ForegroundColor Cyan
if ($defaultPython) {
    Write-Host "Press Enter to use default: $defaultPython" -ForegroundColor Gray
}
if ($foundPythons.Count -gt 0) {
    Write-Host "Or enter a number (1-$($foundPythons.Count)) to select from found installations" -ForegroundColor Gray
}
Write-Host "Or enter the full path to python.exe:" -ForegroundColor Gray

$userInput = Read-Host "Python path"

# Process user input
$pythonPath = ""
if ([string]::IsNullOrWhiteSpace($userInput)) {
    if ($defaultPython) {
        $pythonPath = $defaultPython
    }
    else {
        Write-Host "❌ No default Python found and no path provided!" -ForegroundColor Red
        exit 1
    }
}
elseif ($userInput -match '^\d+$') {
    $index = [int]$userInput - 1
    if ($index -ge 0 -and $index -lt $foundPythons.Count) {
        $pythonPath = $foundPythons[$index]
    }
    else {
        Write-Host "❌ Invalid selection!" -ForegroundColor Red
        exit 1
    }
}
else {
    $pythonPath = $userInput
}

# Validate the selected Python path
Write-Host ""
Write-Host "Validating Python installation..." -ForegroundColor Cyan
if (-not (Test-PythonExecutable $pythonPath)) {
    Write-Host "❌ Invalid Python executable: $pythonPath" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Cyan
try {
    & $pythonPath -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        throw "Python venv command failed"
    }
    Write-Host "✓ Virtual environment created successfully!" -ForegroundColor Green
}
catch {
    Write-Host "❌ Failed to create virtual environment!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Verify virtual environment was created
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment creation failed - python.exe not found!" -ForegroundColor Red
    exit 1
}

# Upgrade pip in virtual environment
Write-Host ""
Write-Host "Upgrading pip in virtual environment..." -ForegroundColor Cyan
try {
    & ".venv\Scripts\python.exe" -m pip install --upgrade pip
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Pip upgraded successfully!" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️  Warning: Failed to upgrade pip, but continuing..." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "⚠️  Warning: Failed to upgrade pip, but continuing..." -ForegroundColor Yellow
}

# Install dependencies if requirements.txt exists
if (Test-Path "requirements.txt") {
    Write-Host ""
    Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Cyan
    try {
        & ".venv\Scripts\python.exe" -m pip install -r requirements.txt
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Dependencies installed successfully!" -ForegroundColor Green
        }
        else {
            Write-Host "⚠️  Warning: Some dependencies may have failed to install" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "⚠️  Warning: Failed to install some dependencies" -ForegroundColor Yellow
    }
}
else {
    Write-Host ""
    Write-Host "ℹ️  No requirements.txt found - skipping dependency installation" -ForegroundColor Blue
}

# Success message
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Virtual Environment Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Virtual environment created at: .venv" -ForegroundColor White
Write-Host "Python executable: .venv\Scripts\python.exe" -ForegroundColor White
Write-Host ""
Write-Host "To activate the virtual environment:" -ForegroundColor Cyan
Write-Host "  .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Or run the MCP configuration generator:" -ForegroundColor Cyan
Write-Host "  .\generate_mcp_config.bat" -ForegroundColor White
Write-Host ""

# Ask if user wants to run the configuration generator
$runConfig = Read-Host "Do you want to run the MCP configuration generator now? (y/N)"
if ($runConfig -match "^[Yy]$") {
    Write-Host ""
    Write-Host "Running MCP configuration generator..." -ForegroundColor Cyan
    if (Test-Path "generate_mcp_config.bat") {
        & ".\generate_mcp_config.bat"
    }
    else {
        Write-Host "❌ generate_mcp_config.bat not found!" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
