# OpenClaw /proxy 接口规范 v1.0

> Cloud Code 化统一网关规范

## 设计原则

1. **单一职责**: 每个 /proxy 端点只负责一类数据源
2. **统一格式**: 所有响应遵循统一 JSON Schema
3. **零幻觉**: AI 不构造 URL，只调用预定义端点
4. **错误隔离**: 外部服务故障不影响系统其他部分

---

## 统一响应格式

```json
{
  "success": true,
  "data": {},
  "meta": {
    "source": "akshare",
    "timestamp": "2026-04-08T12:00:00Z",
    "cached": false,
    "cache_ttl": 60
  },
  "error": null
}
```

### 错误响应

```json
{
  "success": false,
  "data": null,
  "meta": {
    "source": "akshare",
    "timestamp": "2026-04-08T12:00:00Z"
  },
  "error": {
    "code": "CONNECTION_ERROR",
    "message": "无法连接到数据源",
    "retryable": true,
    "fallback_available": true
  }
}
```

---

## 端点列表

### 1. 金融数据 /proxy/finance

| 路径 | 方法 | 描述 | 参数 |
|------|------|------|------|
| `/proxy/finance/market/overview` | GET | 市场概览 | - |
| `/proxy/finance/stocks` | GET | 全部股票 | `limit=20` |
| `/proxy/finance/stock` | GET | 个股详情 | `code=000001` |
| `/proxy/finance/indices` | GET | 指数列表 | - |

**实现**: `stock_api/layer2_service_api.py`

### 2. 游戏配置 /proxy/game

| 路径 | 方法 | 描述 | 参数 |
|------|------|------|------|
| `/proxy/game/config` | GET | 完整游戏配置 | - |
| `/proxy/game/towers` | GET | 塔配置列表 | - |
| `/proxy/game/tower` | GET | 单个塔配置 | `id=archer` |
| `/proxy/game/enemies` | GET | 敌人配置列表 | - |
| `/proxy/game/levels` | GET | 关卡配置列表 | - |

**实现**: `MazeTD/config/api.py` (待实现)

### 3. 文件存储 /proxy/storage

| 路径 | 方法 | 描述 | 参数 |
|------|------|------|------|
| `/proxy/storage/upload` | POST | 上传文件 | `file`, `path` |
| `/proxy/storage/download` | GET | 下载文件 | `path` |
| `/proxy/storage/list` | GET | 列出文件 | `dir=/` |

**实现**: `cloud-upload-backup/skill` (已存在)

---

## 错误码规范

| 错误码 | 描述 | 重试策略 |
|--------|------|---------|
| `CONNECTION_ERROR` | 连接失败 | 重试3次，间隔3s |
| `TIMEOUT_ERROR` | 超时 | 重试2次，间隔5s |
| `DATA_ERROR` | 数据异常 | 不重试，使用缓存 |
| `NOT_FOUND` | 资源不存在 | 不重试 |
| `VALIDATION_ERROR` | 校验失败 | 不重试，上报 |
| `RATE_LIMIT` | 限流 | 按Retry-After重试 |

---

## AI 调用规范

```python
# ✅ 正确: 调用统一端点
response = call_proxy("/proxy/finance/market/overview")
if response["success"]:
    render_template(response["data"])
else:
    handle_error(response["error"])

# ❌ 错误: 直接构造URL
data = requests.get("https://finance.eastmoney.com")  # 禁止
```

---

## 实现清单

- [x] `/proxy/finance/*` - 金融数据API
- [ ] `/proxy/game/*` - 游戏配置API
- [x] `/proxy/storage/*` - 文件存储API (已有)
- [ ] `/proxy/cache/*` - 缓存管理API
- [ ] `/proxy/health` - 健康检查

---

## 部署架构

```
┌─────────────────────────────────────────┐
│           OpenClaw Agent                │
├─────────────────────────────────────────┤
│  /proxy/finance  →  stock_api:8765      │
│  /proxy/game     →  game_api:8766       │
│  /proxy/storage  →  qclaw-cos           │
├─────────────────────────────────────────┤
│  统一网关: localhost:8000               │
└─────────────────────────────────────────┘
```

---

*规范版本: v1.0*  
*最后更新: 2026-04-08*
