# MazeTD PixiJS 渐进式迁移 — 团队讨论纪要

**日期**: 2026-04-15  
**议题**: 方案B PixiJS 渐进式接入落地方案  
**参与角色**: 前端工程师（小李）、游戏策划（阿策划）、QA（测试姐）、技术负责人（小A）

---

## 一、各方观点

### 🔧 前端工程师（小李）

**支持理由：**
- PixiJS 底层是 WebGL，渲染性能比 Canvas 2D 快 3-5x
- 粒子系统从 MAX_PARTS=120 可以轻松扩展到 500+
- PixiJS 的 Container/DisplayObject 天然支持空间层级管理，比我们手动 ctx.translate 快且不容易出 bug
- `pixi.js` 包体积 ~200KB（gzip ~60KB），可接受

**担忧：**
- 当前代码全部用 `ctx.fillRect / ctx.arc / ctx.fillText`，需要逐个替换成 PixiJS 的 Graphics/Sprite/Text
- **关键问题**：CSS UI 层（#top/#bottom）是 HTML/CSS 写的，迁移后是否保留？

**建议：**
> 保留 HTML/CSS 的 UI 层不变，只把 Canvas 渲染层替换成 PixiJS。PixiJS 的 Canvas 直接挂到 `#canvas-box` 里就行，HTML UI 不受影响。

### 🎮 游戏策划（阿策划）

**支持理由：**
- 粒子特效升级后可以做更炫的击杀效果（爆炸碎片、闪电链可视化、毒雾扩散）
- PixiJS 支持 Spine 骨骼动画，未来可以做角色出场动画
- 性能提升后可以支持更多同屏敌人（50+），为后期精英关卡做准备

**担忧：**
- 迁移期间不能停版本更新，玩家在等着新关卡

**要求：**
> 渐进式迁移，每一步都必须保证游戏能正常运行。不能一口气全改，出 bug 就麻烦了。

### 🧪 QA（测试姐）

**关注点：**
1. **回归测试范围**：所有 25 个关卡必须全量回归
2. **移动端兼容性**：PixiJS 在低端安卓（2GB RAM）上的表现？
3. **存档兼容**：localStorage 数据结构不能变，老玩家存档要兼容

**要求：**
> 每个阶段交付后跑一轮完整回归。用 test.html 自动化测试覆盖核心流程。

### 🏗️ 技术负责人（小A）

**总结共识：**
- ✅ 保留 HTML/CSS UI 层不变
- ✅ 只替换 Canvas 渲染层为 PixiJS
- ✅ 游戏逻辑（寻路/AI/波次/经济）不动
- ✅ 分 3 个阶段渐进交付，每阶段可独立验证

---

## 二、技术架构设计

### 当前架构
```
┌─────────────────────────────────┐
│  index.html (单文件)             │
│  ┌───────────────────────────┐  │
│  │  HTML/CSS UI层            │  │  ← 菜单、按钮、状态栏
│  ├───────────────────────────┤  │
│  │  Canvas 2D 渲染层          │  │  ← ctx.fillRect/arc/text
│  ├───────────────────────────┤  │
│  │  游戏逻辑层                │  │  ← 寻路/AI/波次/经济
│  ├───────────────────────────┤  │
│  │  数据层                    │  │  ← LEVELS/ENEMY_TYPES/T
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

### 目标架构
```
┌─────────────────────────────────┐
│  index.html                     │
│  ┌───────────────────────────┐  │
│  │  HTML/CSS UI层            │  │  ← ✅ 不动
│  ├───────────────────────────┤  │
│  │  PixiJS Application        │  │  ← 🆕 WebGL 渲染
│  │  ├─ gameContainer          │  │
│  │  ├─ gridContainer          │  │  ← 网格+墙壁+塔
│  │  ├─ enemyContainer         │  │  ← 敌人
│  │  ├─ bulletContainer        │  │  ← 子弹
│  │  ├─ particleContainer      │  │  ← 粒子特效
│  │  └─ uiContainer            │  │  ← 伤害数字等
│  ├───────────────────────────┤  │
│  │  游戏逻辑层                │  │  ← ✅ 不动
│  ├───────────────────────────┤  │
│  │  数据层                    │  │  ← ✅ 不动
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

### 核心映射关系（Canvas API → PixiJS）

| 当前 Canvas 2D | PixiJS 替换方案 | 说明 |
|----------------|-----------------|------|
| `ctx.fillRect` | `PIXI.Graphics.drawRect` | 网格、墙壁 |
| `ctx.arc` | `PIXI.Graphics.drawCircle` | 塔、敌人圆形 |
| `ctx.fillText` | `PIXI.Text` | 伤害数字 |
| `ctx.save/restore` | `container.position/rotation` | 坐标变换 |
| `ctx.globalAlpha` | `sprite.alpha` | 透明度 |
| `ctx.setTransform` | `app.stage.scale` | DPR缩放 |
| 离屏canvas(starfield) | `PIXI.Container` + 独立render | 星空背景 |
| requestAnimationFrame | `app.ticker.add` | 主循环 |
| 手动粒子池 | `PIXI.ParticleContainer` | GPU加速粒子 |

---

## 三、分阶段执行计划

### 📋 阶段1：基础设施搭建（3天）

**目标**：PixiJS 初始化 + 星空背景迁移（最小风险验证）

**具体任务**：
```
Day 1: 引入 PixiJS
  ├─ npm init + 安装 pixi.js@7
  ├─ 创建 vite.config.ts 构建配置
  ├─ 创建 app.ts，初始化 PIXI.Application
  ├─ 将 PixiJS canvas 挂载到 #canvas-box
  └─ 验证：PixiJS canvas 和 HTML UI 共存

Day 2: 星空背景迁移
  ├─ 将 initStarfield() 迁移到 PixiJS Container
  ├─ 用 PIXI.Graphics 绘制星星（替代离屏canvas）
  ├─ 利用 PixiJS ticker 驱动闪烁动画
  └─ 验证：星空视觉效果一致

Day 3: DPR & 响应式
  ├─ 将 resize() 迁移到 PixiJS 的 app.renderer.resize
  ├─ 确保 dpr 缩放、ox/oy 偏移正确
  └─ 验证：移动端/PC端布局一致
```

**验收标准**：
- [ ] PixiJS canvas 正确渲染在 HTML UI 下方
- [ ] 星空背景视觉无差异
- [ ] resize 后网格居中正确
- [ ] test.html 自动化测试全部通过

**回滚方案**：删掉 PixiJS，恢复原 Canvas 代码（git revert）

---

### 📋 阶段2：核心渲染迁移（5天）

**目标**：网格、塔、敌人、子弹全部迁移到 PixiJS

**具体任务**：
```
Day 4-5: 网格系统
  ├─ 用 PIXI.Graphics 绘制网格线
  ├─ 用 PIXI.Graphics 绘制墙壁（带渐变效果）
  ├─ 塔图标改用 PIXI.Graphics（替代小canvas图标）
  └─ 验证：放置/删除/撤销操作正常

Day 6-7: 敌人 & 子弹
  ├─ 敌人用 PIXI.Graphics 绘制（圆形+表情+血条）
  ├─ 子弹用 PIXI.Graphics（小圆+拖尾）
  ├─ 用 Container 管理，支持批量操作
  └─ 验证：战斗流程完整，击杀/伤害/金币正常

Day 8: 粒子 & 特效
  ├─ 迁移粒子系统到 PIXI.ParticleContainer
  ├─ 提升粒子上限 120 → 500
  ├─ 优化：屏幕震动改用 container shake
  └─ 验证：特效视觉增强，性能无回退
```

**验收标准**：
- [ ] 25个关卡全部可通关
- [ ] 移动端 60fps 稳定
- [ ] 粒子数量提升到 500+ 不掉帧
- [ ] 存档兼容（localStorage 结构不变）

---

### 📋 阶段3：性能优化 & 收尾（3天）

**目标**：利用 PixiJS 特性做深度优化

**具体任务**：
```
Day 9: 纹理缓存
  ├─ 将塔/敌人绘制结果缓存为 PIXI.RenderTexture
  ├─ 避免每帧重复绘制静态元素
  └─ 验证：CPU 占用下降

Day 10: 空间分区优化
  ├─ 实现 Grid-based 空间索引（敌人碰撞检测）
  ├─ 替代当前 O(n²) 的距离遍历
  └─ 验证：50+ 敌人时性能稳定

Day 11: 集成测试 & 上线
  ├─ 全量回归 25 关卡
  ├─ 低端机测试（2GB RAM 安卓）
  ├─ 更新 test.html 自动化测试
  ├─ 提交 PR，部署 GitHub Pages
  └─ 版本号升级为 V22.0
```

---

## 四、风险清单

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| PixiJS WebGL 在低端安卓不兼容 | 低 | 高 | PixiJS 自动降级到 Canvas 2D |
| 粒子效果视觉差异 | 中 | 低 | 逐个对比调参 |
| DPR 缩放导致画面模糊 | 中 | 中 | 用 app.renderer.resolution |
| 构建工具引入复杂度 | 低 | 低 | Vite 极简配置 |
| 存档数据不兼容 | 低 | 高 | localStorage 结构不变 |
| 迁移期间影响版本更新 | 中 | 中 | 分支隔离，主分支保持稳定 |

---

## 五、待确认事项

1. **构建工具**：使用 Vite 还是保持单文件无构建？  
   → 小A建议：Vite（开发体验好，打包后仍可单文件部署）

2. **PixiJS 版本**：v7 还是 v8？  
   → 小A建议：v7（稳定，社区成熟；v8 还是 alpha）

3. **是否同步做 TypeScript 迁移？**  
   → 小A建议：本次只做 PixiJS，TS 作为下一阶段单独推进

4. **新版本号**：V22.0 还是 V21.1？  
   → 小A建议：V22.0（渲染层整体替换，算大版本）

---

## 六、讨论结论

✅ **团队一致同意**：PixiJS 渐进式接入方案可行  
✅ **执行节奏**：3 阶段共 11 个工作日  
✅ **质量保障**：每阶段独立验收 + 全量回归  
⏳ **等待主公确认**：上述 4 项待确认事项

---

*纪要整理：小A | 2026-04-15*
