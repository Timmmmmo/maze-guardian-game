# MazeTD V22.0 PixiJS v8迁移成功

## 完成时间
2026-04-17 10:10 GMT+8

## 问题排查过程

### 根本原因：ES Module + HTML onclick隔离问题
游戏加载但`window.startGame`始终为undefined，模块不执行。
- 原因：HTML onclick属性（`onclick="startGame()"`）在模块加载前尝试访问未定义的`startGame`
- 修复：将所有HTML onclick改为`window.startGame()`等window前缀
- 同步：源文件index.html和dist/index.html都要修复

### 次要问题：缺失button ID
- game.js事件监听器查找`#btn-start`，但`<button class="tg">`没有id属性
- 修复：添加`id="btn-start"`, `id="btn-retry"`, `id="btn-menu"`, `id="btn-level-menu"`, `id="btn-next"`

### 技术细节
- `import * as PIXI from 'pixi.js'` 在浏览器中解析失败是因为测试HTML用了裸模块标识符
- Vite构建后的bundle能正确处理PIXI导入
- PixiJS版本不匹配：game.js用v8 API但package.json装的是v7

## 最终修复清单
1. 所有HTML onclick改为window.前缀
2. 添加所有缺失的button ID
3. 升级至PixiJS v8（forceCanvas模式用于兼容性）
4. 修复initPixi异步初始化（v8需要await app.init()）

## 验证结果
- Canvas创建：✅
- 菜单显示：✅
- 开始游戏：✅
- 塔选择/放置：✅
- 战斗系统：✅
- 零错误：✅

## 部署结构
- `gh-pages`分支：dist/（构建产物，GitHub Pages直接服务）
- `feature/pixijs-v8`分支：源码（game.js/index.html/package.json）
- `main`分支：V20.0原始版

## 技术指标
- 主bundle：290KB（gzip 92KB）
- 完整构建：11个JS文件 + index.html
- PixiJS v8 (WebGL渲染)
