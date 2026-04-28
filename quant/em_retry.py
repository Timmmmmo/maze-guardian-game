"""
用东方财富接口获取失败股票
"""
import requests
import json
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'http://quote.eastmoney.com/'
}

# 东方财富股票代码转换
# 沪市: 1.代码  深市: 0.代码
STOCKS = [
    ('002594', '比亚迪', '0'),
    ('300750', '宁德时代', '0'),
    ('000762', '西藏矿业', '0'),
    ('688487', '索辰科技', '1'),
    ('002415', '海康威视', '0'),
]

print(f"=== 东方财富接口补全 | {datetime.now().strftime('%Y-%m-%d %H:%M')} ===\n")

for code, name, market in STOCKS:
    try:
        # 东方财富行情接口
        url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={market}.{code}&fields=f43,f57,f58,f169,f170,f171,f45,f46,f44,f48&ut=fa5fd1943c7b386f172d6893dbfba10b&fltt=2&invt=2"
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.encoding = 'utf-8'
        data = json.loads(r.text)
        
        if 'data' in data and data['data']:
            d = data['data']
            price = d.get('f43', 0) / 100  # 当前价
            close_prev = d.get('f46', 0) / 100  # 昨收
            open_p = d.get('f45', 0) / 100  # 开盘
            high = d.get('f44', 0) / 100  # 最高
            low = d.get('f48', 0) / 100  # 最低
            pct = d.get('f170', 0) / 100  # 涨跌幅
            name_get = d.get('f58', name)
            
            print(f"✅ {name_get}({code}): {price:.2f} {pct:+.2f}%")
            print(f"   开盘:{open_p:.2f} 最高:{high:.2f} 最低:{low:.2f} 昨收:{close_prev:.2f}")
        else:
            print(f"❌ {name}({code}): 无数据 - {r.text[:100]}")
    except Exception as e:
        print(f"❌ {name}({code}): 异常 - {e}")
    
    import time
    time.sleep(0.3)
