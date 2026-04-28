---
name: mazetd-architect
description: "Use when 开发MazeTD游戏、添加新功能、修复bug、优化性能。触发场景：MazeTD、迷宫塔防、游戏开发、塔防游戏、canvas游戏、HTML5游戏。"
---

# MazeTD 架构师

铁律：每次修改必须保持游戏可玩性。核心循环（建造→开战→击杀→奖励）不可破坏。

## Inputs / Outputs / Gates / Handoffs

- **Inputs**：需求描述、当前代码、预期效果
- **Outputs**：修改后的代码、变更说明、测试建议
- **Gates**：修改后必须验证：1)游戏能启动 2)敌人能移动 3)塔能攻击
- **Handoffs**：`game-test-automation` → 自动化验证

---

## 当前架构（V3.0）

```
index.html (单文件架构)
├── CSS样式 (1-200行)
├── HTML结构 (200-300行)
├── 游戏配置 (300-400行)
│   ├── LEVELS[] - 12关卡配置
│   ├── T{} - 塔类型配置
│   └── ENEMY_TYPES{} - 敌人类型配置
├── 核心函数 (400-1500行)
│   ├── initCanvas() - Canvas初始化
│   ├── findPath() - A*寻路
│   ├── place()/del() - 建造系统
│   ├── spawnWave() - 波次生成
│   ├── loop() - 主循环
│   └── render() - 渲染
└── 辅助函数 (1500-2000行)
    ├── drawTowerIcon() - 塔绘制
    ├── drawEnemyIcon() - 敌人绘制
    └── saveProgress()/loadProgress() - 存档
```

---

## 性能优化清单

### 当前问题
- [ ] 每帧重绘整个地图（可优化）
- [ ] 敌人绘制无批量处理
- [ ] 粒子效果无对象池

### 优化方案

#### 1. 离屏Canvas缓存静态层
```javascript
// 地形层缓存（只在建造时重绘）
let staticCanvas = null;
let staticCtx = null;

function initStaticLayer() {
  staticCanvas = document.createElement('canvas');
  staticCanvas.width = cv.width;
  staticCanvas.height = cv.height;
  staticCtx = staticCanvas.getContext('2d');
  drawStaticLayer();
}

function drawStaticLayer() {
  // 绘制网格、墙壁、固定元素
  staticCtx.clearRect(0, 0, staticCanvas.width, staticCanvas.height);
  // ... 绘制逻辑
}

function render() {
  // 直接复制静态层
  ctx.drawImage(staticCanvas, 0, 0);
  // 只绘制动态元素
  drawEnemies();
  drawBullets();
  drawParticles();
}
```

#### 2. 敌人批量绘制
```javascript
// 按颜色分组绘制
function drawEnemies() {
  const byColor = {};
  for (const e of enemies) {
    const color = e.co;
    if (!byColor[color]) byColor[color] = [];
    byColor[color].push(e);
  }
  
  for (const [color, list] of Object.entries(byColor)) {
    ctx.fillStyle = color;
    ctx.beginPath();
    for (const e of list) {
      ctx.moveTo(e.x + e.sz * CS * 0.5, e.y);
      ctx.arc(e.x, e.y, e.sz * CS * 0.5, 0, Math.PI * 2);
    }
    ctx.fill();
  }
}
```

#### 3. 粒子对象池
```javascript
const particlePool = [];
const MAX_PARTICLES = 200;

function getParticle() {
  return particlePool.pop() || {x:0, y:0, vx:0, vy:0, co:null, l:0, ml:0};
}

function recycleParticle(p) {
  if (particlePool.length < MAX_PARTICLES) {
    particlePool.push(p);
  }
}
```

---

## 数值配置规范

### 关卡难度曲线
```javascript
// 黄金法则：每关难度增幅≤20%
const LEVELS = [
  { id: '1-1', startGold: 600, waves: 5,   // 教学关
    enemies: [{type:'normal', count:3}],
    unlock: ['wall', 'archer'] },
  { id: '1-2', startGold: 550, waves: 6,   // 引入冰塔
    enemies: [{type:'normal', count:5}, {type:'fast', count:2}],
    unlock: ['wall', 'archer', 'ice'] },
  // ... 渐进解锁
];
```

### 敌人强度公式
```javascript
function getEnemyStats(type, wave) {
  const base = ENEMY_TYPES[type];
  return {
    hp: base.hp * (1 + wave * 0.15),      // 血量+15%/波
    speed: base.speed * (1 + wave * 0.02), // 移速+2%/波
    gold: Math.floor(base.gold * (1 + wave * 0.1)) // 奖励+10%/波
  };
}
```

---

## 测试用例

| ID | 场景 | 操作 | 预期 |
|----|------|------|------|
| M01 | 启动 | 打开页面 | 显示标题，FPS≥55 |
| M02 | 建造 | 放置墙壁 | 金币扣除，墙出现 |
| M03 | 开战 | 点击开战 | 敌人生成并移动 |
| M04 | 攻击 | 敌人进射程 | 塔开火，敌人掉血 |
| M05 | 破墙 | 敌人遇墙 | 敌人攻击墙 |

---

## 反模式警告

| 反模式 | 问题 | 修复 |
|--------|------|------|
| 修改核心循环 | 游戏不可玩 | 保护建造→开战→击杀→奖励流程 |
| 破坏存档格式 | 玩家进度丢失 | 版本迁移函数 |
| 数值爆炸 | 后期无意义 | 对数缩放或硬上限 |
| 单文件过大 | 维护困难 | 考虑模块化（暂保持单文件） |

---

## 参考资源

- `game-balance-designer` - 数值平衡设计
- `canvas-render-optimizer` - 渲染性能优化
- `game-test-automation` - 自动化测试
