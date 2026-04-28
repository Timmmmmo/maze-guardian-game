#!/usr/bin/env python3
"""
Layer 3: 渲染层 - 预定义输出模板
职责：将结构化数据渲染为最终输出格式
原则：模板预定义，AI不生成，只填充
"""
from typing import List, Dict, Any, Optional
from dataclasses import asdict
import json

# 预定义模板 - 零幻觉设计
TEMPLATES = {
    "market_overview_text": """📊 A股市场概览
========================================

【主要指数】
{indices}

【涨幅榜 TOP5】
{top_gainers}

【跌幅榜 TOP5】
{top_losers}

💡 数据来源: {source} | 更新时间: {timestamp}
""",
    
    "index_line": "{emoji} {name}: {value:.2f} ({change:+.2f}%)",
    
    "stock_line_gainer": "📈 {rank}. {name}({code}): {price:.2f} +{change:.2f}%",
    
    "stock_line_loser": "📉 {rank}. {name}({code}): {price:.2f} {change:.2f}%",
    
    "stock_detail_text": """📈 {name}({code})
========================================
最新价: {price:.2f} ({change:+.2f}%)
今开: {open:.2f} | 昨收: {prev_close:.2f}
最高: {high:.2f} | 最低: {low:.2f}
成交量: {volume:,.0f} | 成交额: {amount:,.0f}

💡 数据来源: {source} | 更新时间: {timestamp}
""",
    
    "error_template": """❌ 数据获取失败
========================================
错误信息: {error}

建议操作:
{actions}
""",
    
    "json_template": """{\"success\": true, \"data\": {data}, \"meta\": {meta}}"""
}

# 错误处理建议
ERROR_ACTIONS = {
    "ConnectionError": "1. 检查网络连接\n2. 稍后重试\n3. 使用缓存数据",
    "TimeoutError": "1. 网络延迟较高，请稍后重试\n2. 检查网络稳定性",
    "default": "1. 稍后重试\n2. 联系管理员"
}

class TemplateRenderer:
    """模板渲染器 - 只填充，不创造"""
    
    @staticmethod
    def render_market_overview(data: Dict[str, Any], output_format: str = "text") -> str:
        """渲染市场概览"""
        if output_format == "json":
            return json.dumps(data, ensure_ascii=False, indent=2)
        
        # 渲染指数
        indices_lines = []
        for idx in data.get("indices", []):
            emoji = "📈" if idx.get("change", 0) >= 0 else "📉"
            indices_lines.append(TEMPLATES["index_line"].format(
                emoji=emoji,
                name=idx.get("name", "未知"),
                value=idx.get("value", 0),
                change=idx.get("change_pct", 0)
            ))
        
        # 渲染涨幅榜
        gainers_lines = []
        for i, stock in enumerate(data.get("top_gainers", []), 1):
            gainers_lines.append(TEMPLATES["stock_line_gainer"].format(
                rank=i,
                name=stock.get("name", "未知"),
                code=stock.get("code", ""),
                price=stock.get("price", 0),
                change=stock.get("change", 0)
            ))
        
        # 渲染跌幅榜
        losers_lines = []
        for i, stock in enumerate(data.get("top_losers", []), 1):
            losers_lines.append(TEMPLATES["stock_line_loser"].format(
                rank=i,
                name=stock.get("name", "未知"),
                code=stock.get("code", ""),
                price=stock.get("price", 0),
                change=stock.get("change", 0)
            ))
        
        return TEMPLATES["market_overview_text"].format(
            indices="\n".join(indices_lines) if indices_lines else "暂无数据",
            top_gainers="\n".join(gainers_lines) if gainers_lines else "暂无数据",
            top_losers="\n".join(losers_lines) if losers_lines else "暂无数据",
            source=data.get("meta", {}).get("source", "akshare"),
            timestamp=data.get("meta", {}).get("timestamp", "未知")
        )
    
    @staticmethod
    def render_stock_detail(stock: Dict[str, Any], output_format: str = "text") -> str:
        """渲染个股详情"""
        if output_format == "json":
            return json.dumps(stock, ensure_ascii=False, indent=2)
        
        return TEMPLATES["stock_detail_text"].format(
            name=stock.get("name", "未知"),
            code=stock.get("code", ""),
            price=stock.get("price", 0),
            change=stock.get("change", 0),
            open=stock.get("open", 0),
            prev_close=stock.get("prev_close", 0),
            high=stock.get("high", 0),
            low=stock.get("low", 0),
            volume=stock.get("volume", 0),
            amount=stock.get("amount", 0),
            source=stock.get("source", "akshare"),
            timestamp=stock.get("timestamp", "未知")
        )
    
    @staticmethod
    def render_error(error: str, error_type: str = "default") -> str:
        """渲染错误信息"""
        actions = ERROR_ACTIONS.get(error_type, ERROR_ACTIONS["default"])
        return TEMPLATES["error_template"].format(
            error=error,
            actions=actions
        )

if __name__ == "__main__":
    # 测试渲染
    renderer = TemplateRenderer()
    
    test_data = {
        "indices": [
            {"name": "上证指数", "value": 3256.78, "change_pct": 1.52},
            {"name": "深证成指", "value": 10234.56, "change_pct": 3.18}
        ],
        "top_gainers": [
            {"name": "宁德时代", "code": "300750", "price": 198.50, "change": 3.12}
        ],
        "top_losers": [
            {"name": "万科A", "code": "000002", "price": 7.62, "change": -1.25}
        ],
        "meta": {"source": "akshare", "timestamp": "2026-04-08T12:00:00"}
    }
    
    print(renderer.render_market_overview(test_data))
