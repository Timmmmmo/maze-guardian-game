# A股简报定时任务 - 简化版
python "C:\Users\赵鸿杰\.openclaw\agents\game-studio\stock_brief.py" >> "C:\Users\赵鸿杰\.openclaw\agents\game-studio\data\brief_latest.txt" 2>&1
echo Completed at %date% %time% >> "C:\Users\赵鸿杰\.openclaw\agents\game-studio\data\brief_log.txt"