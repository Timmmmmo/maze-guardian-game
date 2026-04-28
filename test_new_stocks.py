import sys
sys.path.insert(0, r'C:\Users\赵鸿杰\.openclaw\agents\game-studio\quant')
from data_source import get_realtime

# 测试新加入的股票
test_codes = ['002594', '000762', '601020', '688114']
print('Testing new stocks...')
result = get_realtime(test_codes)
for code, info in result.items():
    name = info['name']
    current = info['current']
    chg = info['chg_pct']
    print(f'{name}({code}): {current} {chg:+.2f}%')
