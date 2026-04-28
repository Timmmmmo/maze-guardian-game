---
name: game-test-automation
description: "Use when 需要自动化测试游戏、验证游戏逻辑、回归测试、性能测试。触发场景：游戏测试、自动化测试、回归测试、功能验证、性能测试、冒烟测试、单元测试。"
---

# 游戏自动化测试专家

铁律：测试用例必须覆盖"玩家最常用的操作路径"，而非边缘情况。一个能发现真实bug的测试比100个永不过的测试更有价值。

## Inputs / Outputs / Gates / Handoffs

- **Inputs**：游戏代码、测试场景描述、预期行为
- **Outputs**：测试用例、测试脚本、测试报告
- **Gates**：核心功能测试不通过不发布
- **Handoffs**：`game-balance-designer` → 验证数值平衡

---

## 测试用例设计

### 1. MazeTD 核心测试用例

```markdown
| ID | 场景 | 操作 | 预期结果 | 优先级 |
|----|------|------|---------|--------|
| T01 | 游戏启动 | 打开页面 | 标题显示，无报错 | P0 |
| T02 | 放置墙壁 | 点击建造模式，点击格子 | 墙壁出现，金币扣除 | P0 |
| T03 | 放置塔 | 选择塔类型，点击格子 | 塔出现，攻击范围内显示 | P0 |
| T04 | 开战 | 点击开战按钮 | 敌人生成并移动 | P0 |
| T05 | 塔攻击敌人 | 敌人进入射程 | 塔开火，敌人掉血 | P0 |
| T06 | 敌人破墙 | 敌人遇到墙 | 敌人攻击墙，墙掉血 | P1 |
| T07 | 波次完成 | 击杀所有敌人 | 显示下一波，金币奖励 | P1 |
| T08 | 游戏结束 | 敌人到达终点 | 显示失败，可重试 | P1 |
| T09 | 存档功能 | 刷新页面 | 进度恢复 | P2 |
| T10 | 教学引导 | 首次进入 | 提示出现 | P2 |
```

### 2. 自动化测试脚本框架

```javascript
// 测试框架
class GameTester {
  constructor(game) {
    this.game = game;
    this.results = [];
  }

  // 模拟点击
  async click(x, y) {
    const event = new MouseEvent('click', {clientX: x, clientY: y});
    this.game.canvas.dispatchEvent(event);
    await this.wait(100);
  }

  // 模拟触摸
  async touch(x, y) {
    const touch = new Touch({identifier: 0, target: this.game.canvas, clientX: x, clientY: y});
    const event = new TouchEvent('touchstart', {touches: [touch]});
    this.game.canvas.dispatchEvent(event);
    await this.wait(100);
  }

  // 等待
  wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // 断言
  assert(condition, message) {
    this.results.push({
      pass: condition,
      message: message,
      time: new Date().toISOString()
    });
  }

  // 运行测试
  async runTests(tests) {
    for (const test of tests) {
      console.log(`Running: ${test.name}`);
      try {
        await test.fn(this);
        console.log(`✓ ${test.name}`);
      } catch (e) {
        console.log(`✗ ${test.name}: ${e.message}`);
      }
    }
    return this.results;
  }
}

// 测试用例
const tests = [
  {
    name: 'T01-游戏启动',
    fn: async (t) => {
      t.assert(document.title.includes('迷宫塔防'), '标题正确');
      t.assert(!console.error.toString().includes('error'), '无报错');
    }
  },
  {
    name: 'T02-放置墙壁',
    fn: async (t) => {
      const goldBefore = t.game.gold;
      await t.click(100, 100); // 建造模式
      await t.click(200, 200); // 放置位置
      t.assert(t.game.gold < goldBefore, '金币扣除');
      t.assert(t.game.walls.length > 0, '墙壁创建');
    }
  },
  {
    name: 'T04-开战',
    fn: async (t) => {
      await t.click(300, 50); // 开战按钮
      await t.wait(500);
      t.assert(t.game.enemies.length > 0, '敌人生成');
    }
  }
];
```

### 3. 性能测试

```javascript
// 压力测试：200个敌人
async function stressTest() {
  const game = new Game();
  
  // 生成200个敌人
  for (let i = 0; i < 200; i++) {
    game.enemies.push(createEnemy({x: i * 10, y: 0}));
  }
  
  // 测量FPS
  const fps = await measureFPSOverTime(5000);
  
  console.log(`平均FPS: ${fps.avg}`);
  console.log(`最低FPS: ${fps.min}`);
  console.log(`帧率稳定性: ${fps.stability}%`);
  
  return fps.avg >= 30; // 目标：30帧以上
}
```

---

## 工作流

- [ ] **第一步：识别核心路径**
  - [ ] 玩家最常用的操作流程
  - [ ] 必须正确的业务逻辑
  - [ ] 曾经出过bug的地方

- [ ] **第二步：编写测试用例**
  - [ ] 输入条件
  - [ ] 预期输出
  - [ ] 边界条件

- [ ] **第三步：实现自动化脚本**
  - [ ] 模拟用户操作
  - [ ] 验证游戏状态
  - [ ] 收集性能数据

- [ ] **第四步：运行并报告**
  - 用户确认门控：**展示测试结果，失败用例必须修复**

- [ ] **第五步：持续集成**
  - 每次代码变更自动运行
  - 失败阻止发布

---

## 测试报告格式

```markdown
## 测试报告

### 总览
- 总用例数：10
- 通过：8
- 失败：2
- 跳过：0
- 执行时间：12.5s

### 失败用例

#### T06-敌人破墙
- 预期：敌人攻击墙，墙掉血
- 实际：敌人直接穿过墙
- 截图：[附图]
- 建议：检查碰撞检测逻辑

### 性能数据
- 平均FPS：58
- 最低FPS：42
- 内存峰值：125MB
```

---

## 反模式警告

| 反模式 | 问题 | 修复 |
|--------|------|------|
| 测试边缘情况 | 核心功能漏测 | 优先测试主路径 |
| 脆弱的测试 | 一改就挂 | 测试行为而非实现 |
| 慢测试 | 不愿运行 | 控制在30秒内 |
| 无断言 | 假装测试了 | 每个测试必须有断言 |
| 测试覆盖率迷信 | 数字好看但质量差 | 关注关键路径覆盖 |

---

## 参考资源

- `references/test-templates.md` — 各类测试模板
- `references/ci-integration.md` — CI/CD集成指南
