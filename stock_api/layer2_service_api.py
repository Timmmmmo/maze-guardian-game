#!/usr/bin/env python3
"""
Layer 2: 服务层 - 统一API接口
职责：提供本地HTTP接口，统一数据格式，隔离外部依赖
原则：RESTful设计，状态码清晰，错误标准化
"""
import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from layer1_data_provider import DataProvider, DataResult

class StockAPIHandler(BaseHTTPRequestHandler):
    """本地HTTP服务处理器"""
    
    provider = DataProvider()
    
    def log_message(self, format, *args):
        # 静默日志
        pass
    
    def _send_json(self, data: dict, status: int = 200):
        """发送JSON响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def _result_to_response(self, result: DataResult) -> dict:
        """转换DataResult为HTTP响应"""
        if result.success:
            return {
                "success": True,
                "data": result.data,
                "meta": {
                    "source": result.source,
                    "timestamp": result.timestamp
                }
            }
        else:
            return {
                "success": False,
                "error": result.error,
                "meta": {
                    "source": result.source,
                    "timestamp": result.timestamp
                }
            }
    
    def do_GET(self):
        """处理GET请求"""
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)
        
        # 路由分发
        if path == "/api/v1/market/overview":
            self._handle_market_overview()
        elif path == "/api/v1/stocks":
            self._handle_all_stocks(params)
        elif path == "/api/v1/stock":
            self._handle_stock_detail(params)
        elif path == "/api/v1/indices":
            self._handle_indices()
        elif path == "/health":
            self._handle_health()
        else:
            self._send_json({
                "success": False,
                "error": "Not Found",
                "available_endpoints": [
                    "/api/v1/market/overview",
                    "/api/v1/stocks",
                    "/api/v1/stock?code=000001",
                    "/api/v1/indices",
                    "/health"
                ]
            }, 404)
    
    def _handle_market_overview(self):
        """市场概览"""
        indices_result = self.provider.get_indices()
        stocks_result = self.provider.get_all_stocks()
        
        if not indices_result.success and not stocks_result.success:
            self._send_json(self._result_to_response(indices_result), 503)
            return
        
        # 计算涨跌榜
        top_gainers = []
        top_losers = []
        
        if stocks_result.success and stocks_result.data:
            sorted_stocks = sorted(stocks_result.data, key=lambda x: x.change, reverse=True)
            top_gainers = sorted_stocks[:5]
            top_losers = sorted_stocks[-5:][::-1]
        
        response = {
            "success": True,
            "data": {
                "indices": indices_result.data if indices_result.success else [],
                "top_gainers": top_gainers,
                "top_losers": top_losers
            },
            "meta": {
                "source": "akshare",
                "timestamp": indices_result.timestamp if indices_result.success else stocks_result.timestamp
            }
        }
        self._send_json(response)
    
    def _handle_all_stocks(self, params: dict):
        """全部股票列表"""
        limit = int(params.get('limit', ['20'])[0])
        result = self.provider.get_all_stocks()
        
        if result.success and result.data:
            result.data = result.data[:limit]
        
        self._send_json(self._result_to_response(result), 200 if result.success else 503)
    
    def _handle_stock_detail(self, params: dict):
        """个股详情"""
        code = params.get('code', [''])[0]
        if not code:
            self._send_json({
                "success": False,
                "error": "Missing required parameter: code"
            }, 400)
            return
        
        result = self.provider.get_stock_by_code(code)
        self._send_json(self._result_to_response(result), 200 if result.success else 404)
    
    def _handle_indices(self):
        """指数列表"""
        result = self.provider.get_indices()
        self._send_json(self._result_to_response(result), 200 if result.success else 503)
    
    def _handle_health(self):
        """健康检查"""
        self._send_json({
            "status": "healthy",
            "service": "stock-api",
            "version": "1.0.0"
        })

def run_server(port: int = 8765):
    """启动服务"""
    server = HTTPServer(('127.0.0.1', port), StockAPIHandler)
    print(f"Stock API Server running at http://127.0.0.1:{port}")
    server.serve_forever()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    
    run_server(args.port)
