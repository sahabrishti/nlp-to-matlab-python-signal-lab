# Setup Script for NLP to Signal Processing Lab
# -------------------------------------------

Write-Host "Starting Local Setup for NLP to Signal Processing Lab..."

# 1. Check for Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "Python found."
} else {
    Write-Host "Python not found. Please install Python 3.8+ and add it to your PATH."
    exit 1
}

# 2. Create Virtual Environment
Write-Host "Creating virtual environment (.venv)..."
python -m venv .venv

if (-not (Test-Path ".\.venv")) {
    Write-Host "Failed to create virtual environment folder."
    exit 1
}

# 3. Activate and Install Dependencies
Write-Host "Installing Python dependencies from Python/requirements.txt..."
$pipPath = ".\.venv\Scripts\pip.exe"

if (Test-Path $pipPath) {
    & $pipPath install -r Python/requirements.txt
} else {
    Write-Host "pip.exe not found in .venv/Scripts. Attempting alternate path..."
    $pipPath = ".\.venv\bin\pip"
    if (Test-Path $pipPath) {
        & $pipPath install -r Python/requirements.txt
    } else {
        Write-Host "Could not find pip in virtual environment."
        exit 1
    }
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install dependencies."
    exit 1
}

Write-Host "Python setup complete!"

# 4. MATLAB Instructions
Write-Host ""
Write-Host "MATLAB Setup:"
Write-Host "1. Open MATLAB."
Write-Host "2. Navigate to the 'MATLAB' folder in this repository."
Write-Host "3. Run 'check_env.m' to verify your toolboxes."

Write-Host ""
Write-Host "Setup finished successfully!"
Write-Host "To start the Python lab, run: .\.venv\Scripts\python.exe Python\nlp_to_signal.py"
