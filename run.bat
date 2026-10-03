@echo off
setlocal enabledelayedexpansion

:: Set working directory to the folder where this batch file is located
cd /d "%~dp0"

TITLE CRYPTO_ALPHA_SNIPER v1.0.0
COLOR 0A

echo ======================================================================
echo   CRYPTO_ALPHA_SNIPER - High-Throughput Intelligence Engine
echo ======================================================================
echo.

:: 1. Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python tidak ditemukan di sistem Anda!
    echo Silakan install Python 3.11+ dan pastikan Add to PATH dicentang saat instalasi.
    echo.
    pause
    exit /b 1
)

:: 2. Check and prepare .env file
if not exist ".env" (
    echo [WARNING] File .env tidak ditemukan.
    if exist ".env.example" (
        echo Menyalin .env.example menjadi .env ...
        copy /y ".env.example" ".env" >nul
        echo File .env baru berhasil dibuat.
    )
    echo.
)

:: 3. Activate Virtual Environment if exists
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Mengaktifkan Virtual Environment .venv
    call ".venv\Scripts\activate.bat"
) else if exist "venv\Scripts\activate.bat" (
    echo [INFO] Mengaktifkan Virtual Environment venv
    call "venv\Scripts\activate.bat"
)

echo [INFO] Memulai CRYPTO_ALPHA_SNIPER Scanner Engine...
echo [INFO] Tekan Ctrl+C untuk menghentikan bot kapan saja.
echo ======================================================================
echo.

:: 4. Run main application
python -m src.main

:: 5. Keep window open if application stops or crashes
echo.
echo ======================================================================
echo [INFO] Aplikasi telah berhenti.
echo ======================================================================
pause
