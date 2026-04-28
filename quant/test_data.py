import sys
sys.path.insert(0, r'C:\Users\赵鸿杰\.openclaw\agents\game-studio\quant')
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONLEGACYWINDOWSSTDIO'] = 'utf-8'

from data_source import get_realtime_quotes_v2, get_stock_hist

print('=== 行情 ===')
q = get_realtime_quotes_v2(['000001', '399001', '399006', '600519', '600036'])
for c, i in q.items():
    print(f'{i["name"]}({c}): {i["current"]}, {i["chg_pct"]:+.2f}%')

print()
print('=== 历史K线 ===')
h = get_stock_hist('600519', 10)
if h:
    print(f'贵州茅台: {h["dates"][-5:]}, 收盘: {h["close"][-5:]}')
else:
    print('贵州茅台历史失败')

h2 = get_stock_hist('000001', 10)
if h2:
    print(f'上证指数: {h2["dates"][-5:]}, 收盘: {h2["close"][-5:]}')
else:
    print('上证历史失败')
