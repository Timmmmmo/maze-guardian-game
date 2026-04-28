@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "C:\Users\赵鸿杰\.openclaw\agents\game-studio\quant"
python3.12 quant_briefing.py >> briefing.log 2>&1
