@echo off
TITLE CRYPTO_ALPHA_SNIPER v1.0.0
COLOR 0A

echo ======================================================================
echo   CRYPTO_ALPHA_SNIPER - High-Throughput Intelligence Engine
echo ======================================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python tidak ditemukan di sistem Anda!
    echo Silakan install Python 3.11+ dan tambahkan ke PATH.
    echo.
    pause
    exit /b 1
)

:: Check if .env file exists
if not exist ".env" (
    echo [WARNING] File .env tidak ditemukan!
    if exist ".env.example" (
        echo Menyalin .env.example ke .env...
        copy .env.example .env >nul
        echo File .env berhasil dibuat. Silakan sesuaikan token Telegram Anda jika diperlukan.
    )
    echo.
)

:: Activate Virtual Environment if available
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Mengaktifkan Virtual Environment (.venv)...
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo [INFO] Mengaktifkan Virtual Environment (venv)...
    call venv\Scripts\activate.bat
)

echo [INFO] Memulai CRYPTO_ALPHA_SNIPER Scanner Engine...
echo [INFO] Tekan Ctrl+C untuk menghentikan bot.
echo.

:: Run main application
python -m src.main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Aplikasi berhenti dengan kode error: %ERRORLEVEL%
    pause
)
