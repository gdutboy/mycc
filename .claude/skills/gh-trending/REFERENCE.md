# gh-trending REFERENCE

> 详细说明、示例数据、报告模板、排查指南。配套 SKILL.md 使用。

---

## API 说明

### Gitter API（GitHub Trending 非官方）

```bash
# 综合榜（All Languages）
curl -sS "https://api.gitterapp.com/repositories?since=daily&language=" | head -c 500000

# TypeScript 榜（可选）
curl -sS "https://api.gitterapp.com/repositories?since=daily&language=typescript" | head -c 500000
```

**注意**：这是非官方 API，连续失败时降级用 WebFetch 直接抓 `https://github.com/trending` 页面。

### 数据结构示例

```json
{
  "author": "openclaw",
  "name": "openclaw",
  "url": "https://github.com/openclaw/openclaw",
  "description": "Your own personal AI assistant. Any OS. Any Platform",
  "language": "TypeScript",
  "stars": 191400,
  "forks": 12300,
  "currentPeriodStars": 3209
}
```

---

## 筛选标准详情

### P0 优先关注

| 类别 | 关键词示例 |
|------|-----------|
| Claude Code 生态 | MCP、Skills、插件、路由、claude-code |
| AI 编程 Agent | coding assistant, copilot, agentic AI |
| LLM 基础设施 | LLM API、框架、RAG、训练工具 |
| AI 数据工具 | 爬虫、提取、转换、ETL |
| 前端/小程序 | 小程序、Web 开发工具 |

### P1 次要关注

- 通用 AI 工具（写作、总结、对话）
- 开发效率工具（Git、Terminal、自动化）
- 开源 AI 模型/框架

### 排除

- 游戏、娱乐软件
- 纯硬件/驱动项目
- 传统非 AI 工具（除非特别有价值）

### 关注度标注

- `⭐⭐⭐`：高价值，需深度分析
- `⭐⭐`：中价值，简要分析
- `⭐`：低价值，仅列表记录

---

## 报告模板

````markdown
# 每日研究 {YYYY-MM-DD}

## 摘要

（1~2 段话：AI 占比、顶流项目、Claude Code 更新、趋势关键词）

---

## GitHub Trending

### 综合热门榜（All Languages）

| # | 项目 | 描述 | 语言 | 总星标 | 今日 | AI相关 |
|---|------|------|------|--------|------|--------|
| 1 | {author}/{name} | {description} | {language} | {stars} | +{currentPeriodStars} | ✅ |

### 趋势洞察

1. **{趋势1}**：...
2. **{趋势2}**：...

---

## 深度分析（可选）

### {项目名} — {一句话定位}

**核心价值**：...
**对 aster 的启发**：...
**行动建议**：...

---

## Claude Code 更新（可选）

当前本地版本：{version} | npm 最新：**{latest}**（{date} 发布）

### v{latest}（{date}）

**新功能**：...
**重要修复**：...

---

## 行动项

1. ...
````

---

## 飞书通知完整示例

```bash
node .claude/skills/tell-me/send.js \
  "GitHub Trending | 2026-01-20" \
  "**AI 项目占比**：8/25 (32%)\n**Top 3 关注**：\n1. openclaw/openclaw（+3209）— 跨平台 AI 助手，Claude Code 类竞品\n2. vercel/ai（+1800）— AI SDK，RAG/Agent 工具链\n3. microsoft/promptflow（+950）— LLM 应用编排框架\n\n**趋势**：AI Agent 框架持续热门，本地化部署需求上升\n\n详细分析已保存 → 1-Inbox/" \
  "purple"
```

---

## Claude Code 版本检查

```bash
# 本地版本
claude --version

# npm 最新版本
npm view @anthropic-ai/claude-code version

# 最近发布时间线
curl -sS "https://registry.npmjs.org/@anthropic-ai/claude-code" | jq -r '.time | to_entries | sort_by(.value) | reverse | .[0:5]'
```

---

## 排查指南

| 问题 | 处理方式 |
|------|---------|
| Gitter API 超时/失败 | 降级用 WebFetch 抓 github.com/trending |
| 飞书通知失败 | 检查 tell-me 依赖，参考 tell-me/SKILL.md |
| 报告文件已存在 | 追加新发现，不覆盖已有内容 |
| 无 AI 相关项目 | 仍发通知，说明"今日 AI 项目较少" |
