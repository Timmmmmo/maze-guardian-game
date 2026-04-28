"""
补充获取失败的股票
"""
import requests
import re
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.sina.com.cn'
}

FAILED_CODES = ['sh002594', 'sh300750', 'sh000762', 'sh688487', 'sh002415']
FAILED_NAMES = {
    'sh002594': '比亚迪',
    'sh300750': '宁德时代',
    'sh000762': '西藏矿业',
    'sh688487': '索辰科技',
    'sh002415': '海康威视'
}

def get_single(code):
    url = f"http://hq.sinajs.cn/list={code}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.encoding = 'gbk'
        raw = r.text.strip()
        print(f"  {code}: {raw[:120]}")
        return raw
    except Exception as e:
        print(f"  {code}: 请求失败 - {e}")
        return ""

# 批量
print("=== 批量请求 ===")
url = f"http://hq.sinajs.cn/list={','.join(FAILED_CODES)}"
r = requests.get(url, headers=HEADERS, timeout=15)
r.encoding = 'gbk'
print(f"原始长度: {len(r.text)}")
print(r.text[:2000])
print("...")

# 逐个
print("\n=== 逐个请求 ===")
for code in FAILED_CODES:
    raw = get_single(code)

def parse_stock(raw, code):
    m = re.search(rf'hq_str_{code}="(.+)"', raw)
    if not m:
        print(f"  正则未匹配: {code}")
        return None
    f = m.group(1).split(',')
    try:
        name = f[0]
        open_p = float(f[1])
        close_prev = float(f[2])
        current = float(f[3])
        high = float(f[4])
        low = float(f[5])
        vol = float(f[8]) if len(f) > 8 else 0
        amount = float(f[9]) if len(f) > 9 else 0
        pct = ((current - close_prev) / close_prev) * 100
        amplitude = ((high - low) / close_prev) * 100
        vol_level = "放量" if amount > 100000 else "平量" if amount > 50000 else "缩量"
        return {
            'name': name, 'code': code[2:],
            'current': current, 'close_prev': close_prev,
            'high': high, 'low': low,
            'pct': pct, 'amplitude': amplitude,
            'vol_wan': amount, 'vol_level': vol_level
        }
    except Exception as e:
        print(f"  解析失败: {e}")
        return None

print("\n=== 解析结果 ===")
for code in FAILED_CODES:
    raw = get_single(code)
    d = parse_stock(raw, code)
    if d:
        print(f"  ✅ {d['name']}({d['code']}): {d['current']} {d['pct']:+.2f}%")
