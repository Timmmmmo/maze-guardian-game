# HappyBricks V5.3 紧急修复 - 球和砖块不可见

## 问题
用户反馈完全看不到子弹和砖块，游戏无法玩。

## 根因
V5.2编辑时，`let balls = []` 声明被意外替换为 `let ballPool = []` + `let activeBalls = []`，导致：
- `balls` 变量从未声明
- 游戏逻辑中 `balls.push()`, `balls.forEach(drawBall)` 等全部失效
- 砖块虽然声明了 (`let rocks = []`)，但 `loadLevel` 中 `balls = []` 在严格模式下报错导致后续代码不执行，砖块也无法渲染

## 修复
- `let ballPool = []` → `let balls = []`
- 删除无用的 `let activeBalls = []` 和 `let activeParticles = []`
- 保留 `let particlePool = []` 供对象池使用

## 部署
- 提交: 15dc080 (V5.3)
- 线上: https://timmmmmo.github.io/HappyBricks/

## 教训
**修改变量声明时必须保证下游引用一致** — 重命名变量需全局搜索替换，不能只改声明处。
