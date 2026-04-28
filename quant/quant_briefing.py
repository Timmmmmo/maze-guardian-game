"""
quant_briefing.py - 量化简报推送脚本 (供 cron 调用)
"""
import os
import sys
import json
from datetime import datetime

# 设置UTF-8输出
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_source import get_realtime, get_hist_with_retry
from quant_runner import SimpleEngine, fmt_p, fmt_chg, fmt_profit, is_trading_time

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'state.json')
WATCH_LIST = [
    '600519', '600036', '000001', '601318',
    '000858', '601888', '300750', '002594',
    '600900', '601012',
    '002594', '000762', '601020', '688114',  # 比亚迪、西藏矿业、华钰矿业、华大智造
    '600900', '601012',
]


def generate():
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d %H:%M')

    # 非交易时段
    if not is_trading_time():
        engine = SimpleEngine(STATE_FILE)
        weekday = now.weekday()
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        status = "WEEKEND" if weekday >= 5 else "CLOSED"
        perf = engine.perf({})
        return (
            f"[QUANT] {status} | {now_str} ({day_names[weekday]})\n"
            f"  Holdings: {len(engine.holdings)} | Cash: {fmt_p(engine.cash)}\n"
            f"  Total: {fmt_p(perf['total'])} | P/L: {'+' if perf['profit_pct'] >= 0 else ''}{perf['profit_pct']:.2f}%\n"
            f"  Next: Next trading session"
        )

    engine = SimpleEngine(STATE_FILE)

    # 获取行情
    idx = get_realtime(['000001', '399001', '399006'])
    stocks = get_realtime(WATCH_LIST)

    if not stocks and not idx:
        return f"[QUANT] {now_str} | Data fetch failed, retry later"

    idx_names = {'000001': '上证', '399001': '深证', '399006': '创业板'}

    lines = [f"[QUANT TRADING] {now_str}"]
    lines.append("")

    # 指数
    for code, name in idx_names.items():
        if code in idx:
            q = idx[code]
            sign = "+" if q['chg_pct'] >= 0 else ""
            lines.append(f"  [{name}] {q['current']:.2f}  {sign}{q['chg_pct']:.2f}%")

    lines.append("---")
    buys, sells = [], []

    for code in WATCH_LIST:
        if code not in stocks:
            continue
        info = stocks[code]
        if info['name'] in ['上证指数', '深证成指', '创业板指']:
            continue
        hist = get_hist_with_retry(code, 30)
        signals = engine.scan(code, info, hist)
        for sig in signals:
            sig['code'] = code
            sig['name'] = info['name']
            sig['price'] = info['current']
            sig['chg_pct'] = info['chg_pct']
            if sig['act'] == 'BUY':
                buys.append(sig)
            else:
                sells.append(sig)

    urg_map = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}
    buys.sort(key=lambda x: urg_map.get(x.get('urg', 'MEDIUM'), 3))
    sells.sort(key=lambda x: urg_map.get(x.get('urg', 'MEDIUM'), 3))

    if buys:
        lines.append("")
        lines.append(f"  BUY ({len(buys)})")
        for b in buys[:5]:
            sign = "+" if b['chg_pct'] >= 0 else ""
            lines.append(f"    -> {b['name']}({b['code']}) {fmt_p(b['price'])} {sign}{b['chg_pct']:.2f}%")
            lines.append(f"       [{b['sig']}] {b['reason']}")
    else:
        lines.append("")
        lines.append("  BUY: None")

    if sells:
        lines.append("")
        lines.append(f"  SELL ({len(sells)})")
        for s in sells[:5]:
            h = engine.holdings.get(s['code'], {})
            cost = h.get('avg_cost', 0)
            profit = (s['price'] - cost) * h.get('shares', 0) if h else 0
            profit_pct = (s['price'] - cost) / cost * 100 if cost else 0
            sign = "+" if s['chg_pct'] >= 0 else ""
            lines.append(f"    -> {s['name']}({s['code']}) {fmt_p(s['price'])} {sign}{s['chg_pct']:.2f}%")
            lines.append(f"       Cost:{fmt_p(cost)} | P/L:{fmt_profit(profit, profit_pct)}")
            lines.append(f"       [{s['sig']}] {s['reason']}")

    # 执行
    for sig in sells:
        if sig['code'] in engine.holdings:
            engine.execute(sig['code'], stocks[sig['code']], sig)
    for sig in buys:
        if sig['code'] not in engine.holdings:
            engine.execute(sig['code'], stocks[sig['code']], sig)

    # 持仓 & 收益
    perf = engine.perf(stocks)
    lines.append("")
    lines.append(f"  HOLDINGS ({len(engine.holdings)})")
    if engine.holdings:
        for code, h in engine.holdings.items():
            if code in stocks:
                cur = stocks[code]['current']
                profit = (cur - h['avg_cost']) * h['shares']
                pct = (cur - h['avg_cost']) / h['avg_cost'] * 100
                lines.append(f"    {h['name']}({code}) {fmt_p(cur)} | {fmt_p(h['avg_cost'])} | {fmt_profit(profit, pct)}")
    else:
        lines.append("    (empty)")

    lines.append("")
    lines.append(f"  TOTAL: {fmt_p(perf['total'])} | CASH: {fmt_p(perf['cash'])} | P/L: {'+' if perf['profit_pct'] >= 0 else ''}{perf['profit_pct']:.2f}%")

    engine.save()
    return '\n'.join(lines)


if __name__ == '__main__':
    print(generate())
