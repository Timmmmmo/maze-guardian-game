#!/usr/bin/env python3
"""
Layer 5: 输出层 - 统一入口
职责：协调各层，处理异常，零幻觉输出
原则：只使用预渲染模板，不现场生成
"""
import sys
import json
import argparse
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from layer1_data_provider import DataProvider, DataResult
from layer3_template_renderer import TemplateRenderer
from layer4_validator import DataValidator

class StockService:
    """
    Cloud Code 化股票服务
    分层架构：数据层 → 服务层 → 渲染层 → 校验层 → 输出层
    """
    
    def __init__(self):
        self.provider = DataProvider()
        self.renderer = TemplateRenderer()
        self.validator = DataValidator()
    
    def get_market_overview(self, output_format: str = "text") -> str:
        """获取市场概览"""
        # Layer 1: 获取数据
        indices_result = self.provider.get_indices()
        stocks_result = self.provider.get_all_stocks()
        
        # 检查数据可用性
        if not indices_result.success and not stocks_result.success:
            # 双层失败，返回错误模板
            return self.renderer.render_error(
                indices_result.error or stocks_result.error or "未知错误",
                "ConnectionError"
            )
        
        # 组装数据
        data = {
            "indices": [],
            "top_gainers": [],
            "top_losers": [],
            "meta": {
                "source": "akshare",
                "timestamp": indices_result.timestamp or stocks_result.timestamp
            }
        }
        
        if indices_result.success and indices_result.data:
            data["indices"] = [self._stock_to_dict(i) for i in indices_result.data]
        
        if stocks_result.success and stocks_result.data:
            sorted_stocks = sorted(stocks_result.data, key=lambda x: x.change, reverse=True)
            data["top_gainers"] = [self._stock_to_dict(s) for s in sorted_stocks[:5]]
            data["top_losers"] = [self._stock_to_dict(s) for s in sorted_stocks[-5:][::-1]]
        
        # Layer 4: 校验数据
        validation = self.validator.validate_market_overview(data)
        if not validation.valid:
            return self.renderer.render_error(
                "; ".join(validation.errors),
                "DataError"
            )
        
        # Layer 3: 渲染输出（零幻觉）
        return self.renderer.render_market_overview(data, output_format)
    
    def get_stock_detail(self, code: str, output_format: str = "text") -> str:
        """获取个股详情"""
        # Layer 1: 获取数据
        result = self.provider.get_stock_by_code(code)
        
        if not result.success:
            return self.renderer.render_error(
                result.error or f"未找到股票: {code}",
                "NotFoundError"
            )
        
        stock_dict = self._stock_to_dict(result.data)
        
        # Layer 4: 校验
        validation = self.validator.validate_stock(stock_dict)
        if not validation.valid:
            return self.renderer.render_error(
                "; ".join(validation.errors),
                "DataError"
            )
        
        # Layer 3: 渲染
        return self.renderer.render_stock_detail(stock_dict, output_format)
    
    def _stock_to_dict(self, stock) -> dict:
        """转换dataclass为dict"""
        if hasattr(stock, '__dataclass_fields__'):
            return {
                'code': stock.code,
                'name': stock.name,
                'price': stock.price,
                'change': stock.change,
                'volume': stock.volume,
                'amount': stock.amount,
                'high': stock.high,
                'low': stock.low,
                'open': stock.open,
                'prev_close': stock.prev_close,
                'timestamp': stock.timestamp,
                'source': 'akshare'
            }
        return stock

def main():
    """主入口"""
    parser = argparse.ArgumentParser(description='Cloud Code 化A股数据服务')
    parser.add_argument('--overview', action='store_true', help='市场概览')
    parser.add_argument('--stock', type=str, help='查询个股代码')
    parser.add_argument('--json', action='store_true', help='JSON格式输出')
    args = parser.parse_args()
    
    # 设置UTF-8输出
    sys.stdout.reconfigure(encoding='utf-8')
    
    service = StockService()
    output_format = "json" if args.json else "text"
    
    if args.overview:
        output = service.get_market_overview(output_format)
        print(output)
    elif args.stock:
        output = service.get_stock_detail(args.stock, output_format)
        print(output)
    else:
        # 默认显示市场概览
        output = service.get_market_overview(output_format)
        print(output)

if __name__ == "__main__":
    main()
