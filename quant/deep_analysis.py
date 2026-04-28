"""
深度持仓分析
"""
import requests
import re
import json
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.sina.com.cn'
}

def sina_get(codes):
    url = f"http://hq.sinajs.cn/list={','.join(codes)}"
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.encoding = 'gbk'
    return r.text

def parse_stock(raw, code):
    m = re.search(rf'hq_str_{code}="(.+)"', raw)
    if not m: return None
    f = m.group(1).split(',')
    try:
        name = f[0]
        open_p = float(f[1])
        close_prev = float(f[2])
        current = float(f[3])
        high = float(f[4])
        low = float(f[5])
        vol = float(f[8]) if len(f) > 8 else 0  # 手
        amount = float(f[9]) if len(f) > 9 else 0  # 成交额(万)
        change = current - close_prev
        pct = (change / close_prev) * 100
        amplitude = ((high - low) / close_prev) * 100
        # 量比估算
        vol_level = "放量" if amount > 100000 else "平量" if amount > 50000 else "缩量"
        return {
            'name': name, 'code': code[2:], 
            'open': open_p, 'close_prev': close_prev,
            'current': current, 'high': high, 'low': low,
            'change': change, 'pct': pct, 
            'amplitude': amplitude,
            'vol_wan': amount,  # 万元
            'vol_level': vol_level
        }
    except:
        return None

# ===== 完整持仓池 =====
WATCH = [
    ('sh002594', '比亚迪', '新能源汽车'),
    ('sh300750', '宁德时代', '锂电池'),
    ('sh688114', '华大智造', '生物医药'),
    ('sh000762', '西藏矿业', '矿产资源'),
    ('sh688487', '索辰科技', '科技'),
    ('sh603773', '沃格光电', '光电显示'),
    ('sh600552', '凯盛科技', '新材料'),
    ('sh601020', '华钰矿业', '矿产资源'),
    ('sh601318', '中国平安', '金融'),
    ('sh002415', '海康威视', '科技'),
]

codes = [c for c, _, _ in WATCH]
raw = sina_get(codes)

results = {}
for code, name, sector in WATCH:
    d = parse_stock(raw, code)
    if d:
        d['sector'] = sector
        results[code] = d

# ===== 1. 个股分析 =====
print("=" * 70)
print(f"📊 持仓个股深度分析 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 70)

print(f"\n{'名称':<8} {'代码':<8} {'收盘':>8} {'涨跌':>8} {'换手':>7} {'量能':>6} {'振幅':>6} {'板块':<10}")
print("-" * 70)

for code, name, sector in WATCH:
    d = results.get(code)
    if d:
        emoji = "+" if d['pct'] > 0 else "-"
        zt = "🔒" if abs(d['pct'] - 9.99) < 0.05 or abs(d['pct'] - 10) < 0.1 else ""
        print(f"{d['name']:<8} {d['code']:<8} {d['current']:>8.2f} {emoji}{d['pct']:>7.2f}% {d['amplitude']:>6.2f}% {d['vol_level']:>6} {sector:<10} {zt}")
    else:
        print(f"⚠️{name}: 数据获取失败")

# ===== 2. 板块分布 =====
print("\n【持仓板块分布】")
sectors = {}
for code, _, sector in WATCH:
    d = results.get(code)
    if d:
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append((d['name'], d['pct']))

for sector, stocks in sorted(sectors.items(), key=lambda x: -sum(d[1] for d in x[1])):
    avg_pct = sum(d[1] for d in stocks) / len(stocks)
    print(f"\n【{sector}】平均: {avg_pct:+.2f}%")
    for name, pct in stocks:
        emoji = "▲" if pct > 0 else "▼"
        zt = " [涨停]" if abs(pct - 9.99) < 0.05 else ""
        print(f"  {emoji}{name}: {pct:+.2f}%{zt}")

# ===== 3. 综合评分 =====
print("\n【综合持仓评估】")

total_pct = sum(d['pct'] for d in results.values())
avg_pct = total_pct / len(results) if results else 0

up_count = sum(1 for d in results.values() if d['pct'] > 0)
down_count = len(results) - up_count

limit_up = [d['name'] for d in results.values() if abs(d['pct'] - 9.99) < 0.05 or abs(d['pct'] - 10) < 0.1]
limit_down = [d['name'] for d in results.values() if abs(d['pct'] + 9.99) < 0.05 or abs(d['pct'] + 10) < 0.1]

print(f"  持仓数量: {len(results)}只")
print(f"  上涨: {up_count}只 | 下跌: {down_count}只")
print(f"  组合平均涨幅: {avg_pct:+.2f}%")
print(f"  涨停: {', '.join(limit_up) if limit_up else '无'}")
print(f"  跌停: {', '.join(limit_down) if limit_down else '无'}")

# ===== 4. 强势股分析 =====
print("\n【强势个股点评】")
for code, _, _ in WATCH:
    d = results.get(code)
    if not d: continue
    
    # 基础评分
    score = 0
    reasons = []
    
    # 涨幅评分
    if d['pct'] > 7:
        score += 30
        reasons.append("强势涨停/逼近涨停")
    elif d['pct'] > 3:
        score += 20
        reasons.append("大幅跑赢大盘")
    elif d['pct'] > 0:
        score += 10
        reasons.append("小幅收红")
    else:
        score -= 10
        reasons.append("收跌跑输大盘")
    
    # 量能评分
    if d['vol_level'] == '放量':
        score += 20
        reasons.append("量能放大，资金入场")
    elif d['vol_level'] == '缩量':
        score += 5
        reasons.append("缩量整理")
    
    # 振幅评分 (振幅大但收涨 = 强)
    if d['amplitude'] > 5:
        score += 10
        reasons.append("高振幅洗盘")
    
    # 在大盘中的相对位置
    if d['pct'] > avg_pct + 2:
        score += 15
        reasons.append("显著跑赢市场")
    elif d['pct'] < avg_pct - 2:
        score -= 10
        reasons.append("明显跑输市场")
    
    rating = "★★★★★" if score >= 65 else "★★★★☆" if score >= 45 else "★★★☆☆" if score >= 25 else "★★☆☆☆" if score >= 10 else "★☆☆☆☆"
    
    emoji = "🟢" if d['pct'] > 0 else "🔴"
    print(f"\n  {emoji}{d['name']}({d['code']}) {d['pct']:+.2f}%")
    print(f"     综合: {rating} ({score}分)")
    if reasons:
        print(f"     要点: {' | '.join(set(reasons))}")

# ===== 5. 操作建议 =====
print("\n【组合操作建议】")
print("-" * 50)

# 找出最强和最弱
strongest = max(results.values(), key=lambda x: x['pct'])
weakest = min(results.values(), key=lambda x: x['pct'])

print(f"  今日最强: {strongest['name']} {strongest['pct']:+.2f}%")
print(f"  今日最弱: {weakest['name']} {weakest['pct']:+.2f}%")

# 判断仓位建议
heavy_sectors = [s for s, stocks in sectors.items() if any(d[1] > 3 for d in stocks)]
if heavy_sectors:
    print(f"\n  重点配置方向: {', '.join(heavy_sectors)}")
    
if avg_pct > 2:
    print(f"\n  ✅ 今日组合表现优秀(均涨{avg_pct:.1f}%)，持仓方向正确")
elif avg_pct > 0:
    print(f"\n  ⚠️ 今日组合小幅盈利({avg_pct:.1f}%)，可继续持有")
else:
    print(f"\n  ⚠️ 今日组合亏损({avg_pct:.1f}%)，关注止损")

# 具体建议
print("\n  具体操作建议:")
for code, name, sector in WATCH:
    d = results.get(code)
    if not d: continue
    
    if d['pct'] > 7:
        print(f"  - {name}: 强势，可继续持有或适度加仓")
    elif d['pct'] > 2:
        print(f"  - {name}: 走势健康，持有")
    elif d['pct'] > 0:
        print(f"  - {name}: 小幅上涨，观望")
    elif d['pct'] > -2:
        print(f"  - {name}: 微跌，可继续持有观察")
    else:
        print(f"  - {name}: 下跌较多，谨慎，跌破关键位考虑止损")

print("\n" + "=" * 70)
