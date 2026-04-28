"""
东方财富实时行情 - 修正版
"""
import requests
import json
import time
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'http://quote.eastmoney.com/'
}

STOCKS = [
    ('002594', '比亚迪'),
    ('300750', '宁德时代'),
    ('000762', '西藏矿业'),
    ('688487', '索辰科技'),
    ('002415', '海康威视'),
]

def get_em_quote(code):
    if code.startswith('6') or code.startswith('5') or code.startswith('9'):
        secid = f"1.{code}"
    else:
        secid = f"0.{code}"
    url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={secid}&ut=fa5fd1943c7b386f172d6893dbfba10b&fltt=2&invt=2&fields=f57,f58,f43,f169,f170,f171,f45,f46,f44,f48,f47,f49,f50"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.encoding = 'utf-8'
        return json.loads(r.text)
    except Exception as e:
        return {}

print(f"=== 个股深度分析 | {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")

for code, name in STOCKS:
    data = get_em_quote(code)
    time.sleep(0.5)
    
    if 'data' in data and data['data']:
        d = data['data']
        price_fen = d.get('f43', 0)
        close_prev_fen = d.get('f46', 0)
        pct_raw = d.get('f170', 0)
        open_pen = d.get('f45', 0)
        high_pen = d.get('f44', 0)
        low_pen = d.get('f48', 0)
        amount_raw = d.get('f49', 0)
        
        price = price_fen / 100 if price_fen > 100 else price_fen
        close_prev = close_prev_fen / 100 if close_prev_fen > 100 else close_prev_fen
        open_p = open_pen / 100 if open_pen > 100 else open_pen
        high = high_pen / 100 if high_pen > 100 else high_pen
        low = low_pen / 100 if low_pen > 100 else low_pen
        pct = pct_raw / 100
        amplitude = ((high - low) / close_prev * 100) if close_prev > 0 else 0
        amount_wan = amount_raw / 10000
        vol_level = "放量" if amount_wan > 100000 else "平量" if amount_wan > 50000 else "缩量"
        
        if price < 0.01 or price > 10000:
            print(f"? {name}({code}): 价格异常 {price}, f43={price_fen}, raw={json.dumps(d)[:200]}")
            continue
        
        print(f"+ {name}({code}): {price:.2f} {pct:+.2f}%")
        print(f"  昨收:{close_prev:.2f} 开盘:{open_p:.2f} 最高:{high:.2f} 最低:{low:.2f}")
        print(f"  振幅:{amplitude:.2f}% 成交额:{amount_wan:.0f}万元 [{vol_level}]")
    else:
        print(f"x {name}({code}): 无数据")
