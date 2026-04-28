@echo off
chcp 65001 >nul
schtasks /create /tn "A股简报20分钟" /tr "C:\Users\赵鸿杰\AppData\Local\Python\pythoncore-3.14-64\python.exe C:\Users\赵鸿杰\.openclaw\agents\game-studio\stock_brief.py" /sc minute /mo 20 /f
echo 定时任务已创建
pause