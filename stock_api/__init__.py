"""
Stock API - Cloud Code 化A股数据服务

分层架构：
- Layer 1: 数据层 (data_provider) - 原始数据获取
- Layer 2: 服务层 (service_api) - HTTP接口
- Layer 3: 渲染层 (template_renderer) - 预定义模板
- Layer 4: 校验层 (validator) - 数据完整性校验
- Layer 5: 输出层 (main) - 统一入口

使用方式：
    from stock_api import StockService
    service = StockService()
    print(service.get_market_overview())
"""

from .layer1_data_provider import DataProvider, StockData, IndexData, DataResult
from .layer3_template_renderer import TemplateRenderer
from .layer4_validator import DataValidator
from .layer5_main import StockService

__all__ = [
    'DataProvider',
    'StockData',
    'IndexData',
    'DataResult',
    'TemplateRenderer',
    'DataValidator',
    'StockService'
]

__version__ = '2.0.0-cloudcode'
