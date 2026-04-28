"""
quant_runner.py - 量化交易简报 v4
基于已验证可用的新浪数据接口
"""
import os
import sys
import json
from datetime import datetime, time as dtime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_source import get_realtime, get_hist_with_retry

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'state.json')

# 自选股池
WATCH_LIST = [
    '600519', '600036', '000001', '601318',
    '000858', '601888', '300750', '002594',
    '600900', '601012',
    '002594', '000762', '601020', '688114',  # 比亚迪、西藏矿业、华钰矿业、华大智造
]


def is_trading_time():
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    t = now.time()
    return (dtime(9, 30) <= t <= dtime(11, 30)) or (dtime(13, 0) <= t <= dtime(15, 0))


def fmt_p(p): return f"${p:.2f}"
def fmt_chg(p):
    s = "+" if p >= 0 else ""
    return f"{s}{p:.2f}%"
def fmt_chg_emo(p):
    if p > 0: return f"RED {fmt_chg(p)}"
    if p < 0: return f"GREEN {fmt_chg(p)}"
    return f"WHITE {fmt_chg(p)}"
def fmt_profit(amount, pct):
    s = "+" if amount >= 0 else ""
    return f"{s}${amount:.2f} ({s}{pct:.2f}%)"


class SimpleEngine:
    def __init__(self, state_path):
        self.path = state_path
        self.holdings = {}
        self.trades = []
        self.cash = 100000.0
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                self.holdings = d.get('holdings', {})
                self.trades = d.get('trades', [])
                self.cash = d.get('cash', 100000.0)
            except: pass

    def save(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump({'holdings': self.holdings, 'trades': self.trades, 'cash': self.cash}, f, ensure_ascii=False, indent=2)

    def calc_ma(self, prices, n):
        if len(prices) < n: return None
        return sum(prices[-n:]) / n

    def calc_rsi(self, closes, n=14):
        if len(closes) < n + 1: return None
        gains, losses = 0, 0
        for i in range(-n, 0):
            d = closes[i+1] - closes[i]
            gains += d if d > 0 else 0
            losses += -d if d < 0 else 0
        if losses == 0: return 100
        rs = gains / losses
        return 100 - 100 / (1 + rs)

    def scan(self, code, info, hist):
        signals = []
        c = info['current']
        chg_pct = info['chg_pct']

        if not hist or len(hist.get('close', [])) < 10:
            return signals

        closes = hist['close']
        highs = hist.get('high', closes)
        lows = hist.get('low', closes)

        ma5 = self.calc_ma(closes, 5)
        ma10 = self.calc_ma(closes, 10)
        ma20 = self.calc_ma(closes, 20)

        # === 买入信号 ===
        # MA金叉
        if len(closes) >= 11 and ma5 and ma10:
            prev5 = sum(closes[-11:-6]) / 5
            prev10 = sum(closes[-11:-1]) / 10
            if prev5 <= prev10 and ma5 > ma10 and ma20 and c > ma20:
                signals.append({'act': 'BUY', 'sig': 'MA_GOLDEN', 'urg': 'HIGH',
                    'reason': f'MA5({ma5:.2f}) crosses above MA10({ma10:.2f}), price({c:.2f}) > MA20({ma20:.2f})'})

        # RSI超卖
        rsi5 = self.calc_rsi(closes, 5)
        rsi14 = self.calc_rsi(closes, 14)
        if rsi5 and rsi5 < 30 and rsi14 and rsi14 < 50:
            signals.append({'act': 'BUY', 'sig': 'RSI_OVERSOLD', 'urg': 'HIGH',
                'reason': f'RSI5={rsi5:.1f}<30 oversold, RSI14={rsi14:.1f}<50'})

        # 突破20日高点
        if c > max(highs[-20:]) * 1.005:
            signals.append({'act': 'BUY', 'sig': 'BREAKOUT', 'urg': 'HIGH',
                'reason': f'Price {c:.2f} breaks 20-day high'})

        # 动量
        if chg_pct > 3 and len(closes) >= 5:
            ma3 = sum(closes[-3:]) / 3
            ma5_v = sum(closes[-5:]) / 5
            if ma3 > ma5_v:
                signals.append({'act': 'BUY', 'sig': 'MOMENTUM', 'urg': 'MEDIUM',
                    'reason': f'+{chg_pct:.1f}% today, strong momentum'})

        # === 卖出信号 ===
        if code in self.holdings:
            h = self.holdings[code]
            cost = h['avg_cost']
            loss_pct = (c - cost) / cost * 100

            # 硬止损 -8%
            if loss_pct < -8:
                signals.append({'act': 'SELL', 'sig': 'STOP_LOSS', 'urg': 'CRITICAL',
                    'reason': f'Loss {loss_pct:.1f}% < -8%, forced exit'})

            # MA死叉
            elif len(closes) >= 11 and ma5 and ma10:
                prev5 = sum(closes[-11:-6]) / 5
                prev10 = sum(closes[-11:-1]) / 10
                if prev5 >= prev10 and ma5 < ma10:
                    signals.append({'act': 'SELL', 'sig': 'MA_DEAD', 'urg': 'MEDIUM',
                        'reason': f'MA5({ma5:.2f}) crosses below MA10({ma10:.2f})'})

            # RSI超买
            elif rsi5 and rsi5 > 70:
                signals.append({'act': 'SELL', 'sig': 'RSI_OVERBOUGHT', 'urg': 'MEDIUM',
                    'reason': f'RSI5={rsi5:.1f}>70 overbought, take profit'})

            # 跌破10日低点止损 -3%
            elif c < min(lows[-10:]) * 0.97:
                signals.append({'act': 'SELL', 'sig': 'TRAIL_STOP', 'urg': 'HIGH',
                    'reason': f'Price {c:.2f} drops below 10-day low, stop-loss'})

        return signals

    def execute(self, code, info, sig):
        c = info['current']
        name = info['name']

        if sig['act'] == 'BUY':
            if code in self.holdings:
                return False
            budget = self.cash * 0.2
            shares = int(budget / c / 100) * 100
            if shares < 100:
                return False
            self.cash -= shares * c
            self.holdings[code] = {'name': name, 'shares': shares, 'avg_cost': c,
                'buy_date': datetime.now().strftime('%Y-%m-%d'), 'signal': sig['sig']}
            self.trades.append({
                'time': datetime.now().strftime('%Y-%m-%d %H:%M'), 'act': 'BUY',
                'code': code, 'name': name, 'price': c, 'shares': shares,
                'amount': shares * c, 'sig': sig['sig'], 'reason': sig['reason']})
            return True

        elif sig['act'] == 'SELL':
            if code not in self.holdings:
                return False
            h = self.holdings[code]
            proceeds = h['shares'] * c
            profit = proceeds - h['shares'] * h['avg_cost']
            self.cash += proceeds
            self.trades.append({
                'time': datetime.now().strftime('%Y-%m-%d %H:%M'), 'act': 'SELL',
                'code': code, 'name': h['name'], 'price': c, 'shares': h['shares'],
                'amount': proceeds, 'profit': profit, 'profit_pct': profit / (h['shares'] * h['avg_cost']) * 100,
                'sig': sig['sig'], 'reason': sig['reason']})
            del self.holdings[code]
            return True

        return False

    def portfolio_value(self, quotes):
        pos_val = sum(h['shares'] * quotes.get(code, {}).get('current', h['avg_cost'])
                       for code, h in self.holdings.items())
        return self.cash + pos_val

    def perf(self, quotes):
        total = self.portfolio_value(quotes)
        pos_val = total - self.cash
        return {
            'total': total, 'cash': self.cash, 'pos': pos_val,
            'profit': total - 100000, 'profit_pct': (total - 100000) / 100000 * 100,
            'trade_count': len(self.trades),
        }


def generate_report(engine, watch):
    quotes = get_realtime(watch)
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')

    lines = [
        "=" * 50,
        "  QUANT TRADING BRIEF",
        f"  {now_str}",
        "=" * 50,
    ]

    # 指数
    idx_quotes = get_realtime(['000001', '399001', '399006'])
    idx_names = {'000001': '上证', '399001': '深证', '399006': '创业板'}
    for code, name in idx_names.items():
        if code in idx_quotes:
            q = idx_quotes[code]
            lines.append(f"\n[{name}] {q['current']:.2f}  {fmt_chg_emo(q['chg_pct'])}")

    lines.append("\n" + "=" * 50)
    lines.append(f"  MARKET SCAN ({len(watch)} stocks)")
    lines.append("")

    buys, sells = [], []

    for code in watch:
        if code not in quotes:
            continue
        info = quotes[code]
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

    # 排序
    urg_map = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}
    buys.sort(key=lambda x: urg_map.get(x.get('urg', 'MEDIUM'), 3))
    sells.sort(key=lambda x: urg_map.get(x.get('urg', 'MEDIUM'), 3))

    if buys:
        lines.append(f"  BUY SIGNAL ({len(buys)})")
        for b in buys[:5]:
            lines.append(f"    -> {b['name']}({b['code']}) {fmt_p(b['price'])} {fmt_chg_emo(b['chg_pct'])}")
            lines.append(f"       [{b['sig']}] {b['reason']}")
    else:
        lines.append("  BUY SIGNAL: None")

    lines.append("")

    if sells:
        lines.append(f"  SELL SIGNAL ({len(sells)})")
        for s in sells[:5]:
            h = engine.holdings.get(s['code'], {})
            cost = h.get('avg_cost', 0)
            profit = (s['price'] - cost) * h.get('shares', 0) if h else 0
            profit_pct = (s['price'] - cost) / cost * 100 if cost else 0
            lines.append(f"    -> {s['name']}({s['code']}) {fmt_p(s['price'])} {fmt_chg_emo(s['chg_pct'])}")
            lines.append(f"       Cost: {fmt_p(cost)} | P/L: {fmt_profit(profit, profit_pct)}")
            lines.append(f"       [{s['sig']}] {s['reason']}")
    else:
        lines.append("  SELL SIGNAL: None")

    # 执行
    for sig in sells:
        if sig['code'] in engine.holdings:
            engine.execute(sig['code'], quotes[sig['code']], sig)
    for sig in buys:
        if sig['code'] not in engine.holdings:
            engine.execute(sig['code'], quotes[sig['code']], sig)

    # 持仓
    lines.append("\n" + "=" * 50)
    perf = engine.perf(quotes)
    lines.append(f"  HOLDINGS ({len(engine.holdings)})")
    if engine.holdings:
        for code, h in engine.holdings.items():
            if code in quotes:
                cur = quotes[code]['current']
                val = cur * h['shares']
                profit = (cur - h['avg_cost']) * h['shares']
                pct = (cur - h['avg_cost']) / h['avg_cost'] * 100
                lines.append(f"    {h['name']}({code}) {fmt_p(cur)} | Cost:{fmt_p(h['avg_cost'])} | P/L:{fmt_profit(profit, pct)}")
    else:
        lines.append("    (empty)")

    lines.append("")
    lines.append("=" * 50)
    lines.append(f"  TOTAL ASSETS: {fmt_p(perf['total'])}")
    lines.append(f"  CASH: {fmt_p(perf['cash'])}")
    lines.append(f"  POSITIONS: {fmt_p(perf['pos'])}")
    lines.append(f"  TOTAL P/L: {fmt_profit(perf['profit'], perf['profit_pct'])}")
    lines.append(f"  TRADE COUNT: {perf['trade_count']}")
    lines.append("=" * 50)

    engine.save()
    return '\n'.join(lines)


if __name__ == '__main__':
    engine = SimpleEngine(STATE_FILE)

    if not is_trading_time():
        now = datetime.now()
        weekday = now.weekday()
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        status = "WEEKEND" if weekday >= 5 else "AFTER HOURS"
        print(f"Market {status} | {now.strftime('%Y-%m-%d %H:%M')} ({day_names[weekday]})")
        print(f"Holdings: {len(engine.holdings)} | Cash: ${engine.cash:.2f}")
        perf = engine.perf({})
        print(f"Total: ${perf['total']:.2f} | P/L: {perf['profit_pct']:+.2f}%")
    else:
        print(generate_report(engine, WATCH_LIST))
