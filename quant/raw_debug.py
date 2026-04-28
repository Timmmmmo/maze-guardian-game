"""
直接看东方财富原始数据
"""
import requests
import json
import time

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

for code, name in STOCKS:
    if code.startswith(('6', '5', '9')):
        secid = f"1.{code}"
    else:
        secid = f"0.{code}"
    url = f"http://push2.eastmoney.com/api/qt/stock/get?secid={secid}&ut=fa5fd1943c7b386f172d6893dbfba10b&fltt=2&invt=2&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15,f16,f17,f18,f19,f20,f21,f22,f23,f24,f25,f26,f27,f28,f29,f30,f31,f32,f33,f34,f35,f36,f37,f38,f39,f40,f41,f42,f43,f44,f45,f46,f47,f48,f49,f50"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.encoding = 'utf-8'
        data = json.loads(r.text)
        if data.get('data'):
            d = data['data']
            name_got = d.get('f58', name)
            # f43=最新价, f46=昨收, f44=最高, f48=最低, f47=成交量, f49=成交额
            # 东方财富价格字段: 创业板/沪市深市是否需要/100
            print(f"=== {name}({code}) ===")
            print(f"  名称: {name_got}")
            print(f"  f43(最新价): {d.get('f43')}")
            print(f"  f44(最高): {d.get('f44')}")
            print(f"  f45(开盘): {d.get('f45')}")
            print(f"  f46(昨收): {d.get('f46')}")
            print(f"  f47(成交量): {d.get('f47')}")
            print(f"  f48(最低): {d.get('f48')}")
            print(f"  f49(成交额): {d.get('f49')}")
            print(f"  f50: {d.get('f50')}")
            print(f"  f169: {d.get('f169')}")
            print(f"  f170(涨跌幅): {d.get('f170')}")
            print(f"  f171(涨跌额): {d.get('f171')}")
            print(f"  f57: {d.get('f57')}")
            print(f"  f58: {d.get('f58')}")
            print()
    except Exception as e:
        print(f"x {name}({code}): {e}")
    time.sleep(0.5)
