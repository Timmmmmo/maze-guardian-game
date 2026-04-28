# 量化交易系统 cron 任务

## 配置信息
- 数据源: 新浪实时 + 新浪历史K线
- 脚本: C:\Users\赵鸿杰\.openclaw\agents\game-studio\quant\quant_briefing.py
- 状态文件: C:\Users\赵鸿杰\.openclaw\agents\game-studio\quant\state.json
- 自选股: 贵州茅台、招商银行、平安银行、中国平安、五粮液、中国中免、宁德时代、比亚迪、长江电力、隆基绿能

## 策略
- MA金叉、RSI超卖、突破20日高点、动量追涨
- 止损: -8%硬止损、-3%跟踪止损
- 仓位: 每次20%仓位

## 数据源状态
- 新浪实时 hq.sinajs.cn: ✅ 可用
- 新浪历史 money.finance.sina.com.cn: ✅ 可用
- 东方财富 push2his.eastmoney.com: ❌ 被墙
- akshare stock_zh_a_hist: ❌ 被墙
- baostock api.baostock.com: ❌ 被墙
