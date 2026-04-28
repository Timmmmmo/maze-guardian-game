# A股20分钟简报 - Windows计划任务配置

## 手动创建步骤：

1. 打开任务计划程序 (taskschd.msc)
2. 创建基本任务
3. 名称: A股20分钟简报
4. 触发器: 每20分钟一次
5. 操作: 启动程序
6. 程序: %LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe
7. 参数: C:\Users\赵鸿杰\.openclaw\agents\game-studio\stock_brief.py

## PowerShell一键创建命令：

```powershell
$action = New-ScheduledTaskAction -Execute "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\python.exe" -Argument "C:\Users\赵鸿杰\.openclaw\agents\game-studio\stock_brief.py"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 20) -RepetitionDuration (New-TimeSpan -Days 365)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "A股20分钟简报" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force
```

## 查看简报

简报会输出到控制台。要发送到微信，需要配合消息发送机制。

---

当前状态: 简报脚本已就绪，等待设置定时执行机制。
