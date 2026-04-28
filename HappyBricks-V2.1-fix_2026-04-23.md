# V2.1 修复记录

## 修复内容

### Bug 1: 瞄准方向反转
- **原因**: `Math.atan2(-dy, -dx)` 取了反方向
- **修复**: 改为 `Math.atan2(dy, dx)`，手势方向即发射方向
- **额外**: 加了 canvas 缩放修正（`scaleX/scaleY`），确保触摸坐标在不同屏幕尺寸下准确

### Bug 2: 卡顿/抖动
- **原因**: 没有 `e.preventDefault()`，浏览器同时处理滚动导致卡顿
- **修复**: 所有 pointer 事件加 `preventDefault()`
- **额外**: 加了 8px 最小移动阈值，避免轻触时角度抖动

### 改动 3: 第一关弹球数量
- 3 → 8 颗

## 部署
- commit: 396bd19
- 在线版: https://timmmmmo.github.io/HappyBricks/
