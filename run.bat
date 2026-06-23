@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo 仮想環境がありません。README のセットアップ手順を実行してください。
    exit /b 1
)
.venv\Scripts\python.exe main.py --once %*
