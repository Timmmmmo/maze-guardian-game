# A股简报定时任务 - 简化的绝对路径
$python = "C:\Users\赵鸿杰\AppData\Local\Python\pythoncore-3.14-64\python.exe"
$script = "C:\Users\赵鸿杰\.openclaw\agents\game-studio\stock_brief.py"
$output = "C:\Users\赵鸿杰\.openclaw\agents\game-studio\data\brief_output.txt"

# 调试：写入日志
$log = "C:\Users\赵鸿杰\.openclaw\agents\game-studio\data\brief_log.txt"
"Starting at $(Get-Date)" | Out-File $log -Encoding UTF8

# 执行脚本
& $python $script *>&1 | Out-File -FilePath $output -Encoding UTF8

"Done at $(Get-Date)" | Out-File $log -Append -Encoding UTF8