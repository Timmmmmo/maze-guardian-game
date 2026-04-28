#!/usr/bin/env python3
"""
Layer 1: 数据层 - 原始数据获取
职责：从外部数据源获取原始数据，返回结构化结果
原则：不格式化、不渲染、只获取和清洗
"""
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Union
from datetime import datetime
import json

@dataclass
class StockData:
    code: str
    name: str
    price: float
    change: float
    volume: float
    amount: float
    high: float
    low: float
    open: float
    prev_close: float
    timestamp: str

@dataclass
class IndexData:
    name: str
    symbol: str
    value: float
    change: float
    change_pct: float
    timestamp: str

@dataclass
class DataResult:
    success: bool
    data: Optional[Union[List[StockData], List[IndexData], StockData, IndexData]]
    error: Optional[str]
    source: str
    timestamp: str

class DataProvider:
    """数据提供者 - 只负责获取原始数据"""
    
    def __init__(self):
        self.source = "akshare"
    
    def get_all_stocks(self) -> DataResult:
        """获取全部A股实时行情"""
        try:
            import akshare as ak
            df = ak.stock_zh_a_spot_em()
            
            stocks = []
            for _, row in df.iterrows():
                stocks.append(StockData(
                    code=str(row['代码']),
                    name=str(row['名称']),
                    price=float(row['最新价']) if pd.notna(row['最新价']) else 0.0,
                    change=float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else 0.0,
                    volume=float(row['成交量']) if pd.notna(row['成交量']) else 0.0,
                    amount=float(row['成交额']) if pd.notna(row['成交额']) else 0.0,
                    high=float(row['最高']) if pd.notna(row['最高']) else 0.0,
                    low=float(row['最低']) if pd.notna(row['最低']) else 0.0,
                    open=float(row['今开']) if pd.notna(row['今开']) else 0.0,
                    prev_close=float(row['昨收']) if pd.notna(row['昨收']) else 0.0,
                    timestamp=datetime.now().isoformat()
                ))
            
            return DataResult(
                success=True,
                data=stocks,
                error=None,
                source=self.source,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return DataResult(
                success=False,
                data=None,
                error=str(e),
                source=self.source,
                timestamp=datetime.now().isoformat()
            )
    
    def get_indices(self) -> DataResult:
        """获取主要指数"""
        try:
            import akshare as ak
            indices = []
            
            index_map = {
                '000001': '上证指数',
                '399001': '深证成指',
                '399006': '创业板指'
            }
            
            for symbol, name in index_map.items():
                try:
                    df = ak.index_zh_a_hist(
                        symbol=symbol,
                        period='daily',
                        start_date=datetime.now().strftime('%Y%m%d'),
                        end_date=datetime.now().strftime('%Y%m%d')
                    )
                    if not df.empty:
                        latest = df.iloc[-1]
                        indices.append(IndexData(
                            name=name,
                            symbol=symbol,
                            value=float(latest['收盘']),
                            change=float(latest['涨跌额']),
                            change_pct=float(latest['涨跌幅']),
                            timestamp=datetime.now().isoformat()
                        ))
                except:
                    continue
            
            return DataResult(
                success=True,
                data=indices,
                error=None,
                source=self.source,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return DataResult(
                success=False,
                data=None,
                error=str(e),
                source=self.source,
                timestamp=datetime.now().isoformat()
            )
    
    def get_stock_by_code(self, code: str) -> DataResult:
        """按代码查询个股"""
        result = self.get_all_stocks()
        if not result.success:
            return result
        
        stocks = result.data
        for stock in stocks:
            if stock.code == code:
                return DataResult(
                    success=True,
                    data=stock,
                    error=None,
                    source=self.source,
                    timestamp=datetime.now().isoformat()
                )
        
        return DataResult(
            success=False,
            data=None,
            error=f"未找到股票代码: {code}",
            source=self.source,
            timestamp=datetime.now().isoformat()
        )

# 导入pandas用于数据校验
try:
    import pandas as pd
except ImportError:
    pd = None

if __name__ == "__main__":
    # 测试数据层
    provider = DataProvider()
    result = provider.get_indices()
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2, default=lambda o: asdict(o) if hasattr(o, '__dataclass_fields__') else str(o)))
