@echo off
title Discord Token Onliner
cd /d "%~dp0"

if not exist "discord-token-onliner\" (
    python -m venv discord-token-onliner
)

call discord-token-onliner\Scripts\activate.bat
pip install -r requirements.txt
python main.py

pause