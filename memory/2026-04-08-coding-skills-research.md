# GitHub 高星 Coding Skills 学习报告

> 研究时间：2026-04-08  
> 研究对象：GitHub star > 200 的 AI Agent Skills 和 MCP Servers

---

## 📊 核心发现

### 一、最值得学习的项目

| 项目名 | Stars | 核心价值 | 学习重点 |
|--------|-------|----------|----------|
| **Expert-Coding-Skills** | 17+ | 中文生产级技能集 | 结构化工作流、铁律设计、门控机制 |
| **fast-agent** | 高 | Agent框架+MCP | Skills/MCP/ACP 完整支持 |
| **DesktopCommanderMCP** | 高 | 终端+文件系统 | MCP Server 最佳实践 |
| **modelcontextprotocol/servers** | 官方 | 官方MCP服务器 | 标准化实现参考 |

---

## 🎯 关键学习点

### 1. Skill 结构设计（来自 Expert-Coding-Skills）

```
skill-name/
├── SKILL.md          # 主文件（<500行）
├── README.md         # 安装和使用说明
└── references/       # 按需加载的参考文档
    ├── checklist.md
    └── template.md
```

**核心原则：**
- `SKILL.md` 控制在 500 行以内
- 重型内容移到 `references/` 按需加载
- 每个 reference 文件聚焦单一主题

---

### 2. SKILL.md 黄金结构

```yaml
---
name: skill-name
description: "核心描述。触发词：关键词1、关键词2、关键词3..."
---

# 技能名称

铁律：[最重要的行为约束，用户最需要知道的一条规则]

<HARD-GATE>
[强制门控：必须等待用户确认才能继续]
</HARD-GATE>

## Inputs / Outputs / Gates / Handoffs

- **Inputs**：最小输入要求
- **Outputs**：产出形态
- **Gates**：继续前必须满足的条件
- **Handoffs**：推荐的下游技能

## 工作流

- [ ] 第一步：[描述]（必须）
  - [子步骤1]
  - [子步骤2]
- [ ] 第二步：[描述]
  - 用户确认门控：[继续前必须获得批准]

## 参考资源

- `references/checklist.md` — 用途说明
```

---

### 3. 严重度分级体系

| 级别 | 名称 | 说明 | 处置 |
|------|------|------|------|
| **P0** | 致命 | 安全漏洞、数据丢失、逻辑错误 | 必须阻止合并 |
| **P1** | 严重 | 重大SOLID违反、性能回退 | 合并前应修复 |
| **P2** | 中等 | 代码异味、可维护性问题 | 本PR修复或创建Issue |
| **P3** | 建议 | 风格、命名、优化建议 | 可选改进 |

---

### 4. 铁律设计模式

**好的铁律：**
- 具体、可执行
- 覆盖最常见的误用场景
- 用表格形式列出"借口 vs 现实"

**示例：**
```markdown
铁律：默认只输出审查报告，不实现任何修改。

| 借口 | 现实 |
|------|------|
| "P0问题这么严重，我帮用户直接修吧" | 用户可能有不同的修复方案。先报告，等确认。 |
| "修复很简单，顺手就改了" | "顺手修复"绕过了用户的决策权。 |
```

---

### 5. 触发词设计

**description 必须包含：**
- 前50字说明解决什么问题
- 10-20个触发关键词（中英文）
- 包含触发场景的动词

**示例：**
```yaml
description: "Use when 用户要求审查代码、评估代码质量、提交PR前检查。触发场景：代码审查、code review、审查代码、review、检查代码、代码检查、代码质量、代码评审、这段代码有问题吗、帮我看看代码、合并前检查。"
```

---

### 6. MCP Server 最佳实践（来自 DesktopCommanderMCP）

**核心能力：**
- 终端命令执行（长运行进程支持）
- 文件系统操作（搜索、读写、编辑）
- 进程管理（列出、杀死）
- Excel/PDF/DOCX 支持
- 审计日志（10MB自动轮转）

**安全机制：**
- 符号链接追踪
- 敏感文件访问警告
- 配置文件保护
- 权限边界检查

---

### 7. Hooks 系统（来自 Expert-Coding-Skills）

| Hook | 触发时机 | 功能 |
|------|----------|------|
| check-secrets | 提交前 | 检测API Key/Token/私钥 |
| warn-sensitive-file | 读取文件 | .env/.key/.pem 访问警告 |
| post-edit-format | 编辑后 | 自动运行Prettier格式化 |
| post-edit-typecheck | 编辑后 | TypeScript类型检查 |
| session-start | 会话开始 | 加载上次会话摘要 |
| session-end | 会话结束 | 保存会话摘要 |

---

## 🔧 对 MazeTD 项目的应用

### 可以创建的 Skills

| 技能名 | 用途 | 优先级 |
|--------|------|--------|
| `game-balance-designer` | 游戏数值平衡设计 | P1 |
| `tower-defense-architect` | 塔防架构设计 | P1 |
| `canvas-render-optimizer` | Canvas渲染优化 | P2 |
| `game-test-automation` | 游戏自动化测试 | P2 |

---

## 📚 推荐学习资源

1. **Expert-Coding-Skills** - https://github.com/ProgrammerAnthony/Expert-Coding-Skills
   - 最完整的中文技能集
   - 覆盖代码审查、安全审计、TDD、架构设计

2. **fast-agent** - https://github.com/evalstate/fast-agent
   - 完整的MCP/ACP支持
   - CLI-first 设计

3. **DesktopCommanderMCP** - https://github.com/wonderwhy-er/DesktopCommanderMCP
   - MCP Server 实现参考
   - 终端+文件系统最佳实践

4. **modelcontextprotocol/servers** - https://github.com/modelcontextprotocol/servers
   - 官方MCP服务器集合
   - 标准化实现

---

## 💡 关键洞察

1. **铁律 > 工作流** - 先定义"不能做什么"，再定义"怎么做"
2. **门控 > 自动化** - 关键决策必须等待用户确认
3. **按需加载 > 一次性加载** - 减少context消耗
4. **触发词 > 描述** - 10-20个关键词确保被发现
5. **反模式清单 > 最佳实践** - 告诉AI"不该做什么"更重要

---

## 🔧 已创建的 Skills

基于学习成果，已为 MazeTD 项目创建以下技能：

| 技能名 | 用途 | 文件位置 |
|--------|------|---------|
| `game-balance-designer` | 游戏数值平衡设计 | `skills/game-balance-designer/SKILL.md` |
| `canvas-render-optimizer` | Canvas渲染优化 | `skills/canvas-render-optimizer/SKILL.md` |
| `game-test-automation` | 游戏自动化测试 | `skills/game-test-automation/SKILL.md` |
| `mazetd-architect` | MazeTD架构专用 | `skills/mazetd-architect/SKILL.md` |

### 测试文件
- `MazeTD-prototype/test.html` - 自动化测试框架（10个核心测试用例）

---

*报告生成时间：2026-04-08 23:40*
