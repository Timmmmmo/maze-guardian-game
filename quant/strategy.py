"""
strategy.py - 量化交易策略引擎
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class StrategyEngine:
    """策略引擎 - 多策略组合"""
    
    def __init__(self, watch_pool_file: str = None):
        self.watch_pool = []
        self.holdings = {}  # {code: {'name': '', 'shares': 0, 'avg_cost': 0.0, 'buy_date': ''}}
        self.trade_log = []
        self.capital = 100000.0  # 模拟起始资金10万
        self.positions_value = 0.0
        
        if watch_pool_file and os.path.exists(watch_pool_file):
            self.load_state(watch_pool_file)
    
    # ---------- 指标计算 ----------
    
    @staticmethod
    def calc_ma(prices: List[float], period: int) -> Optional[float]:
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period
    
    @staticmethod
    def calc_rsi(prices: List[float], period: int = 14) -> Optional[float]:
        if len(prices) < period + 1:
            return None
        gains, losses = 0, 0
        for i in range(-period, 0):
            diff = prices[i+1] - prices[i]
            if diff > 0:
                gains += diff
            else:
                losses -= diff
        if losses == 0:
            return 100
        rs = gains / losses
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def calc_volatility(closes: List[float]) -> Optional[float]:
        if len(closes) < 5:
            return None
        rets = [(closes[i+1]-closes[i])/closes[i] for i in range(len(closes)-1)]
        import statistics
        return statistics.stdev(rets) if len(rets) > 1 else None
    
    # ---------- 核心策略 ----------
    
    def strategy_ma_cross(self, code: str, info: Dict, hist: Dict) -> Optional[Dict]:
        """均线金叉死叉策略"""
        if not hist or len(hist.get('close', [])) < 10:
            return None
        
        closes = hist['close']
        ma5 = self.calc_ma(closes, 5)
        ma10 = self.calc_ma(closes, 10)
        ma20 = self.calc_ma(closes, 20)
        
        if ma5 is None or ma10 is None:
            return None
        
        current = info['current']
        name = info['name']
        
        # 金叉买入条件: MA5上穿MA10，且价格在MA20之上
        if len(closes) >= 10:
            prev_ma5 = sum(closes[-11:-6]) / 5
            prev_ma10 = sum(closes[-11:-1]) / 10
            if prev_ma5 <= prev_ma10 and ma5 > ma10 and ma20 and current > ma20:
                return {
                    'action': 'BUY',
                    'reason': f'MA5({ma5:.2f})上穿MA10({ma10:.2f})，现价{current} > MA20({ma20:.2f})，MA多头排列',
                    'signal': 'MA_GOLDEN',
                    'urgency': 'HIGH'
                }
        
        # 死叉卖出条件
        if code in self.holdings and len(closes) >= 10:
            prev_ma5 = sum(closes[-11:-6]) / 5
            prev_ma10 = sum(closes[-11:-1]) / 10
            if prev_ma5 >= prev_ma10 and ma5 < ma10:
                return {
                    'action': 'SELL',
                    'reason': f'MA5({ma5:.2f})下穿MA10({ma10:.2f})，趋势转弱',
                    'signal': 'MA_DEAD',
                    'urgency': 'MEDIUM'
                }
        
        return None
    
    def strategy_rsi_oversold(self, code: str, info: Dict, hist: Dict) -> Optional[Dict]:
        """RSI超卖策略"""
        if not hist or len(hist.get('close', [])) < 15:
            return None
        
        closes = hist['close']
        rsi5 = self.calc_rsi(closes, 5)
        rsi14 = self.calc_rsi(closes, 14)
        current = info['current']
        
        if rsi5 is None:
            return None
        
        # RSI < 30 超卖买入
        if rsi5 < 30 and rsi14 and rsi14 < 50:
            return {
                'action': 'BUY',
                'reason': f'RSI5={rsi5:.1f} < 30 超卖区，RSI14={rsi14:.1f}',
                'signal': 'RSI_OVERSOLD',
                'urgency': 'HIGH'
            }
        
        # RSI > 70 超买卖出
        if code in self.holdings and rsi5 > 70:
            return {
                'action': 'SELL',
                'reason': f'RSI5={rsi5:.1f} > 70 超买区，止盈',
                'signal': 'RSI_OVERBOUGHT',
                'urgency': 'MEDIUM'
            }
        
        return None
    
    def strategy_breakout(self, code: str, info: Dict, hist: Dict) -> Optional[Dict]:
        """突破策略"""
        if not hist or len(hist.get('close', [])) < 20:
            return None
        
        closes = hist['close']
        highs = hist.get('high', closes)
        lows = hist.get('low', closes)
        current = info['current']
        
        # 计算20日高点
        high_20 = max(highs[-20:])
        high_10 = max(highs[-10:])
        
        # 突破20日高点买入
        if current > high_20 * 1.005:
            return {
                'action': 'BUY',
                'reason': f'股价{current}突破20日高点{high_20:.2f}(+{((current/high_20)-1)*100:.1f}%)',
                'signal': 'BREAKOUT_HIGH',
                'urgency': 'HIGH'
            }
        
        # 跌破10日低点止损
        if code in self.holdings:
            low_10 = min(lows[-10:])
            if current < low_10 * 0.97:
                return {
                    'action': 'SELL',
                    'reason': f'股价{current}跌破10日低点{low_10:.2f}，触发止损(-3%)',
                    'signal': 'STOP_LOSS',
                    'urgency': 'HIGH'
                }
        
        return None
    
    def strategy_momentum(self, code: str, info: Dict, hist: Dict) -> Optional[Dict]:
        """动量策略"""
        if not hist or len(hist.get('close', [])) < 5:
            return None
        
        closes = hist['close']
        current = info['current']
        chg_pct = info['chg_pct']
        
        # 强势股追涨: 今日涨幅>3%，且5日均线向上
        if chg_pct > 3 and closes[-1] > closes[-3]:
            ma3 = sum(closes[-3:]) / 3
            ma5 = sum(closes[-5:]) / 5
            if ma3 > ma5:
                return {
                    'action': 'BUY',
                    'reason': f'今日涨幅{chg_pct:.1f}%，动量强劲，MA3>{ma3:.2f}>MA5',
                    'signal': 'MOMENTUM_UP',
                    'urgency': 'MEDIUM'
                }
        
        return None
    
    def check_stop_loss(self, code: str, info: Dict) -> Optional[Dict]:
        """硬止损 - 亏损超过8%强制卖出"""
        if code not in self.holdings:
            return None
        holding = self.holdings[code]
        current = info['current']
        cost = holding['avg_cost']
        loss_pct = (current - cost) / cost * 100
        
        if loss_pct < -8:
            return {
                'action': 'SELL',
                'reason': f'亏损{loss_pct:.1f}% > 8%，强制止损',
                'signal': 'HARD_STOP_LOSS',
                'urgency': 'CRITICAL'
            }
        return None
    
    def analyze(self, code: str, info: Dict, hist: Dict) -> List[Dict]:
        """综合分析 - 运行所有策略"""
        signals = []
        
        for strategy_fn in [
            self.strategy_ma_cross,
            self.strategy_rsi_oversold,
            self.strategy_breakout,
            self.strategy_momentum,
            self.check_stop_loss,
        ]:
            try:
                sig = strategy_fn(code, info, hist)
                if sig:
                    signals.append(sig)
            except Exception as e:
                pass
        
        return signals
    
    def execute_trade(self, code: str, info: Dict, signal: Dict) -> bool:
        """执行交易"""
        action = signal['action']
        current = info['current']
        name = info['name']
        
        if action == 'BUY':
            # 检查是否已持仓
            if code in self.holdings:
                return False
            
            # 计算买入数量 (按金额，1手=100股)
            budget = self.capital * 0.2  # 每次用20%仓位
            shares = int(budget / current / 100) * 100
            if shares < 100:
                return False
            
            cost = shares * current
            self.capital -= cost
            self.holdings[code] = {
                'name': name,
                'shares': shares,
                'avg_cost': current,
                'buy_date': datetime.now().strftime('%Y-%m-%d'),
                'signal': signal['signal']
            }
            
            trade = {
                'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'action': 'BUY',
                'code': code,
                'name': name,
                'price': current,
                'shares': shares,
                'amount': cost,
                'signal': signal['signal'],
                'reason': signal['reason']
            }
            self.trade_log.append(trade)
            return True
        
        elif action == 'SELL':
            if code not in self.holdings:
                return False
            
            holding = self.holdings[code]
            shares = holding['shares']
            proceeds = shares * current
            profit = proceeds - (shares * holding['avg_cost'])
            profit_pct = profit / (shares * holding['avg_cost']) * 100
            
            self.capital += proceeds
            
            trade = {
                'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'action': 'SELL',
                'code': code,
                'name': holding['name'],
                'price': current,
                'shares': shares,
                'amount': proceeds,
                'profit': profit,
                'profit_pct': profit_pct,
                'signal': signal['signal'],
                'reason': signal['reason'],
                'hold_days': (datetime.now() - datetime.strptime(holding['buy_date'], '%Y-%m-%d')).days
            }
            self.trade_log.append(trade)
            del self.holdings[code]
            return True
        
        return False
    
    def get_portfolio_value(self, quotes: Dict[str, Dict]) -> float:
        """计算当前总资产"""
        holdings_value = 0
        for code, holding in self.holdings.items():
            if code in quotes:
                current = quotes[code]['current']
                holdings_value += holding['shares'] * current
        self.positions_value = holdings_value
        return self.capital + holdings_value
    
    def get_performance(self, quotes: Dict[str, Dict]) -> Dict:
        """获取当前收益情况"""
        total_value = self.get_portfolio_value(quotes)
        total_cost = 100000.0  # 初始资金
        
        return {
            'total_value': total_value,
            'cash': self.capital,
            'positions_value': self.positions_value,
            'total_profit': total_value - total_cost,
            'total_profit_pct': (total_value - total_cost) / total_cost * 100,
            'capital': total_cost,
            'holdings': self.holdings,
            'trade_count': len(self.trade_log),
        }
    
    def save_state(self, path: str):
        state = {
            'holdings': self.holdings,
            'trade_log': self.trade_log,
            'capital': self.capital,
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    def load_state(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            self.holdings = state.get('holdings', {})
            self.trade_log = state.get('trade_log', [])
            self.capital = state.get('capital', 100000.0)
        except Exception as e:
            print(f'加载状态失败: {e}')
