@echo off
echo ============================================
echo   SHUTTING DOWN BUTLER...
echo ============================================
echo.
echo [1/3] Stopping Butler server...
taskkill /f /im python.exe >nul 2>&1
echo [2/3] Stopping Ollama...
taskkill /f /im ollama.exe >nul 2>&1
taskkill /f /im "ollama app.exe" >nul 2>&1
echo [3/3] Stopping Docker...
taskkill /f /im "Docker Desktop.exe" >nul 2>&1
taskkill /f /im com.docker.backend.exe >nul 2>&1
wsl --shutdown >nul 2>&1
echo.
echo  Butler is fully shut down. VRAM and RAM freed, sir.
timeout /t 3 >nul
