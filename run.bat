@echo off
chcp 65001 > nul
echo 批量檔案重命名工具
echo ====================
echo.

echo 檢查 Python 環境...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo 錯誤: 未找到 Python，請確保已安裝 Python 3.7+
    echo 下載地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python 環境正常
echo.

echo 啟動批量檔案重命名工具...
python main.py

if %errorlevel% neq 0 (
    echo.
    echo 程式執行時發生錯誤，錯誤代碼: %errorlevel%
    echo.
    echo 如果問題持續發生，請檢查:
    echo 1. Python 版本是否為 3.7 或更高
    echo 2. 是否正確安裝了 tkinter（通常隨 Python 一起安裝）
    echo 3. 檔案權限是否正確
    echo.
    pause
)