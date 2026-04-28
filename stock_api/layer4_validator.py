#!/usr/bin/env python3
"""
Layer 4: 校验层 - 数据完整性校验
职责：验证数据格式、数值范围、完整性
原则：不通过校验的数据不输出，异常上报
"""
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]
    warnings: List[str]

class DataValidator:
    """数据校验器 - 守门员角色"""
    
    # 数值范围定义
    VALID_RANGES = {
        "price": (0.01, 10000.0),      # 股价范围
        "change": (-30.0, 30.0),        # 涨跌幅范围（%）
        "volume": (0, 1e15),            # 成交量范围
        "amount": (0, 1e20),            # 成交额范围
    }
    
    # 必填字段
    REQUIRED_STOCK_FIELDS = ["code", "name", "price", "change"]
    REQUIRED_INDEX_FIELDS = ["name", "symbol", "value", "change"]
    
    @classmethod
    def validate_stock(cls, stock: Dict[str, Any]) -> ValidationResult:
        """校验个股数据"""
        errors = []
        warnings = []
        
        # 检查必填字段
        for field in cls.REQUIRED_STOCK_FIELDS:
            if field not in stock or stock[field] is None:
                errors.append(f"缺少必填字段: {field}")
        
        if errors:
            return ValidationResult(False, errors, warnings)
        
        # 校验数值范围
        price = stock.get("price", 0)
        if not cls.VALID_RANGES["price"][0] <= price <= cls.VALID_RANGES["price"][1]:
            errors.append(f"股价异常: {price}")
        
        change = stock.get("change", 0)
        if not cls.VALID_RANGES["change"][0] <= change <= cls.VALID_RANGES["change"][1]:
            warnings.append(f"涨跌幅异常: {change}%")
        
        # 校验代码格式
        code = stock.get("code", "")
        if not (len(code) == 6 and code.isdigit()):
            warnings.append(f"股票代码格式异常: {code}")
        
        # 校验名称
        name = stock.get("name", "")
        if not name or len(name) > 20:
            warnings.append(f"股票名称异常: {name}")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    @classmethod
    def validate_index(cls, index: Dict[str, Any]) -> ValidationResult:
        """校验指数数据"""
        errors = []
        warnings = []
        
        # 检查必填字段
        for field in cls.REQUIRED_INDEX_FIELDS:
            if field not in index or index[field] is None:
                errors.append(f"缺少必填字段: {field}")
        
        if errors:
            return ValidationResult(False, errors, warnings)
        
        # 校验数值
        value = index.get("value", 0)
        if value <= 0:
            errors.append(f"指数点位异常: {value}")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    @classmethod
    def validate_market_overview(cls, data: Dict[str, Any]) -> ValidationResult:
        """校验市场概览数据"""
        errors = []
        warnings = []
        
        # 校验指数
        indices = data.get("indices", [])
        if not indices:
            warnings.append("指数数据为空")
        else:
            for idx in indices:
                result = cls.validate_index(idx)
                if not result.valid:
                    errors.extend([f"指数[{idx.get('name', 'unknown')}] {e}" for e in result.errors])
        
        # 校验股票列表
        gainers = data.get("top_gainers", [])
        losers = data.get("top_losers", [])
        
        for stock in gainers + losers:
            result = cls.validate_stock(stock)
            if not result.valid:
                errors.extend([f"股票[{stock.get('code', 'unknown')}] {e}" for e in result.errors])
        
        # 校验元数据
        meta = data.get("meta", {})
        if not meta.get("timestamp"):
            warnings.append("缺少时间戳")
        if not meta.get("source"):
            warnings.append("缺少数据来源")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    @classmethod
    def sanitize_stock(cls, stock: Dict[str, Any]) -> Dict[str, Any]:
        """清洗个股数据"""
        sanitized = {}
        
        # 确保必填字段存在
        for field in cls.REQUIRED_STOCK_FIELDS:
            sanitized[field] = stock.get(field, "")
        
        # 数值字段清洗
        sanitized["price"] = max(0, float(stock.get("price", 0) or 0))
        sanitized["change"] = float(stock.get("change", 0) or 0)
        sanitized["volume"] = max(0, float(stock.get("volume", 0) or 0))
        sanitized["amount"] = max(0, float(stock.get("amount", 0) or 0))
        sanitized["high"] = max(0, float(stock.get("high", 0) or 0))
        sanitized["low"] = max(0, float(stock.get("low", 0) or 0))
        sanitized["open"] = max(0, float(stock.get("open", 0) or 0))
        sanitized["prev_close"] = max(0, float(stock.get("prev_close", 0) or 0))
        
        # 字符串字段清洗
        sanitized["code"] = str(stock.get("code", "")).strip()[:6]
        sanitized["name"] = str(stock.get("name", "")).strip()[:20]
        sanitized["timestamp"] = str(stock.get("timestamp", ""))
        sanitized["source"] = str(stock.get("source", "akshare"))
        
        return sanitized

if __name__ == "__main__":
    # 测试校验
    validator = DataValidator()
    
    test_stock = {
        "code": "000001",
        "name": "平安银行",
        "price": 10.85,
        "change": 2.35,
        "volume": 1000000,
        "amount": 10850000
    }
    
    result = validator.validate_stock(test_stock)
    print(f"Valid: {result.valid}")
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")
