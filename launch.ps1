# Butler Orchestrator launcher
Write-Host "=== Butler Orchestrator ===" -ForegroundColor Cyan

# Move to the script's own folder, so it works from anywhere.
Set-Location -Path $PSScriptRoot

# Check Ollama is running.
try {
    Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 | Out-Null
    Write-Host "[ok] Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "[!] Ollama doesn't appear to be running. Start Ollama, then try again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit
}

# Check Docker is running.
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Docker doesn't appear to be running. Start Docker Desktop, then try again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit
}
Write-Host "[ok] Docker is running" -ForegroundColor Green

# Activate the virtual environment and run the orchestrator.
& ".\venv\Scripts\Activate.ps1"
Write-Host "[ok] Environment activated. Starting...`n" -ForegroundColor Green
python core\orchestrator.py

Read-Host "`nDone. Press Enter to close"