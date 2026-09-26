@echo off
setlocal enabledelayedexpansion

:: Selalu pastikan folder kerja berada di lokasi file batch ini
cd /d "%~dp0"

title Portal Konversi Dokumen Internal (100%% Offline dan Aman)

echo ========================================================
echo   MENJALANKAN PORTAL KONVERSI DOKUMEN INTERNAL
echo ========================================================
echo.

:: 1. Verifikasi Python terpasang di komputer
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan di komputer ini!
    echo Silakan install Python terlebih dahulu atau tambahkan ke PATH.
    echo.
    pause
    exit /b 1
)

:: 2. Cek dependensi modul Python
python -c "import flask, bs4, pandas, openpyxl, mammoth, xhtml2pdf, pymupdf, PIL, pptx" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Menginstall library Python yang dibutuhkan...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo [ERROR] Gagal menginstall library Python. Pastikan koneksi internet aktif saat setup pertama.
        echo.
        pause
        exit /b 1
    )
    echo [SUKSES] Semua library Python berhasil dipasang!
    echo.
)

:: 3. Deteksi LibreOffice untuk hasil Word ke PDF presisi 100%
set "LO_FOUND=0"
where soffice >nul 2>&1
if %errorlevel% equ 0 set "LO_FOUND=1"
if exist "C:\Program Files\LibreOffice\program\soffice.com" set "LO_FOUND=1"
if exist "C:\Program Files\LibreOffice\program\soffice.exe" set "LO_FOUND=1"
if exist "C:\Program Files (x86)\LibreOffice\program\soffice.com" set "LO_FOUND=1"
if exist "C:\Program Files (x86)\LibreOffice\program\soffice.exe" set "LO_FOUND=1"

if "!LO_FOUND!"=="1" (
    echo [OK] Engine LibreOffice terdeteksi: Hasil Word ke PDF 100%% presisi identik asli.
) else (
    echo [INFO] LibreOffice tidak terdeteksi: Menggunakan engine fallback Chromium/Edge.
)
echo.

:: 4. Buka browser secara otomatis setelah server mulai
echo Membuka aplikasi di browser...
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:5050"

:: 5. Bebaskan port 5050 jika ada proses lama yang masih menggantung
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5050 ^| findstr LISTENING') do (
    taskkill /f /pid %%a >nul 2>&1
)

:: 6. Jalankan server Flask
python app.py
if %errorlevel% neq 0 (
    echo.
    echo [PERINGATAN] Server berhenti dengan kode: %errorlevel%
    echo Jika port 5050 sedang dipakai, tutup proses yang berjalan sebelumnya.
    echo.
)
pause


