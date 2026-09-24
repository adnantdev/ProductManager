@echo off
echo ========================================
echo Building Product Management System
echo ========================================

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found!
    pause
    exit /b 1
)


REM Build using python -m pyinstaller
echo.
echo Building executable...
python -m PyInstaller --name="ProductManagement" ^
    --windowed ^
    --onefile ^
    --add-data="src/database.py;." ^
    --hidden-import=PyQt5 ^
    --hidden-import=PyQt5.QtChart ^
    --hidden-import=pandas ^
    --hidden-import=openpyxl ^
    --hidden-import=csv ^
    --hidden-import=shutil ^
    --hidden-import=datetime ^
    --collect-all=PyQt5 ^
    --collect-all=PyQtChart ^
    --clean ^
    src/main.py

if errorlevel 1 (
    echo.
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ Build successful!
echo ========================================
echo.
echo Executable: dist\ProductManagement.exe
dir dist\ProductManagement.exe 2>nul
echo.
echo You can now run: dist\ProductManagement.exe

pause