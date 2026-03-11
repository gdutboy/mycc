---
name: gh-trending
description: 采集 GitHub Trending AI 项目，分析后推飞书
layer: 执行层
authorization: A区（自动执行，无需人类介入）
output_levels: L1（结论）
status: active
created: 2026-01-20
origin: P20 采集系统
---

# GitHub Trending AI 项目推送

## 触发词

- "/gh-trending"、"GitHub Trending"、"今日 GitHub"

## 依赖

from .claude/skills/tell-me/SKILL.md import /tell-me

## 执行流程

**Step 1：采集 GitHub Trending**

```bash
curl -sS "https://api.gitterapp.com/repositories?since=daily&language=" | head -c 500000
```

取 Top 25，关键字段：`author/name`、`description`、`stars`、`currentPeriodStars`、`language`。

**Step 2：AI 筛选**

优先筛选（P0）：Claude Code 生态、AI 编程 Agent、LLM 基础设施、AI 数据工具、前端开发工具。
次要关注（P1）：通用 AI 工具、开发效率工具、开源模型。
排除：游戏、娱乐、纯硬件。

**Step 3：深度分析高价值项目**

对 ⭐⭐⭐/⭐⭐ 项目输出：项目分类、核心价值、对当前业务的启发、行动建议。

**Step 4：趋势洞察**

输出 3~5 条趋势：AI 项目占比、Claude Code 生态动态、新兴技术方向、热点技术栈。

**Step 5：Claude Code 更新检查（可选）**

```bash
claude --version && npm view @anthropic-ai/claude-code version
```

榜单有 CC 相关项目或近期未检查时执行，版本落后则在报告中记录。

**Step 6：飞书通知**

```bash
node .claude/skills/tell-me/send.js \
  "GitHub Trending | {YYYY-MM-DD}" \
  "**AI 项目占比**：{X}/{Y}\n**Top 3**：\n1. {项目}（+{今日星}）— {价值}\n...\n\n**趋势**：{一句话}\n\n详细报告 → 1-Inbox/" \
  "purple"
```

**Step 7：保存报告**

路径：`1-Inbox/{YYYY-MM-DD}-每日研究-GitHub-Trending.md`
内容：摘要 → Trending 表格 → 趋势洞察 → 深度分析（可选）→ CC 更新（可选）→ 行动项。
已有文件则追加，不覆盖。

## 资源预算

- 执行时间 ≤10 分钟；飞书通知 ≤10 行；报告 ≤150 行

详细参考：同目录下 REFERENCE.md
