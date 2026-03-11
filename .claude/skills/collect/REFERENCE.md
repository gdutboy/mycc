# collect SKILL — 详细参考文档

## 可选参数

只运行部分 collector：
```bash
node "$PROJECT_ROOT/.claude/skills/collect/scripts/collect.mjs" --sources fxb,gh-trending
```

## Token 预警通知命令

红卡（过期）：
```bash
node "$PROJECT_ROOT/.claude/skills/tell-me/send.js" "风向标 Token 过期" "API 返回 success: false，请刷新 token。\n操作：跟 cc 说「刷新生财 token」即可自动完成" "red"
```

黄卡（即将过期）：
```bash
node "$PROJECT_ROOT/.claude/skills/tell-me/send.js" "风向标 Token 即将过期" "剩余 {daysLeft} 天，{expireDate} 到期。\n操作：跟 cc 说「刷新生财 token」即可自动完成" "yellow"
```

## Agent Prompt 模板

```
你是 {源名} 分析师。请完成以下任务：

1. 读取分析标准：$PROJECT_ROOT/.claude/skills/collect/analysis/{source}-analyst.md
2. 读取原始数据：{$SAVE_DIR}/{source}.json
3. 按分析标准筛选和分析数据
4. 将分析报告写入：{$SAVE_DIR}/{source}-analysis.md

注意：
- 严格按 analyst.md 中的"报告输出格式"段写报告
- 报告要能独立阅读（包含日期、数据量等上下文）
- 如果数据为空或采集失败，写一份简短说明即可
```

## briefing.md 格式模板

```markdown
# 每日简报 | {YYYY-MM-DD}

## 概览
- 风向标：{X} 条（筛选后 {Y} 条命中，精选 {Z} 条）
- GitHub Trending：{X} 个项目（AI 相关 {Y} 个）
- 多平台热点：{X} 条

## 风向标 Top N

### 1. {一句话总结}
- **作者**：xxx | **互动**：👍{likes} 💬{comments}
- **核心观点**：...
- **启发**：...

## GitHub Trending 精选

### {author/name} — {一句话定位}
- **语言**：{lang} | **今日**：+{todayStars}
- **核心价值**：...
- **启发**：...

## 热点速览

| 平台 | 热点 |
|------|------|
| 微博 | {top1} |
| 知乎 | {top1} |

## 趋势洞察
1. ...
2. ...
```

## 加新源

1. 复制 `collectors/_template.mjs`，改名为 `{source}.mjs`
2. 实现采集逻辑 + `formatExtract` 函数（`--extract` 模式）
3. 如果数据量大（>20 条或含长文），加 `--index` 模式
4. 完成。协调器自动发现，无需改 SKILL.md

## Collector 自治标准

每个 collector 包含三种模式：

| 模式 | 必须？ | 说明 |
|------|--------|------|
| 采集（默认） | 必须 | 拉数据，输出 JSON |
| `--extract <json> <idx,...\|all>` | 必须 | 按序号提取（或 `all` 全部），输出 markdown |
| `--index <json>` | 可选 | 数据量大时生成紧凑索引 |

公共函数在 `lib/fetcher.mjs`：`extractItems(jsonPath, indices, formatFn, name)`。

## 分析师文件对应关系

| 分析师 | 文件 | 对应源 |
|--------|------|--------|
| 风向标分析师 | `analysis/fxb-analyst.md` | fxb |
| GitHub 分析师 | `analysis/github-analyst.md` | gh-trending |
| 技术社区分析师 | `analysis/tech-analyst.md` | tech-news |
| 国内热点分析师 | `analysis/trends-analyst.md` | trends |
| 小红书分析师 | `analysis/xhs-analyst.md` | xhs |
| AI 前沿 RSS 分析师 | `analysis/rss-ai-analyst.md` | rss-ai |
| 开发者工具 RSS 分析师 | `analysis/rss-dev-analyst.md` | rss-dev |
| 创业商业 RSS 分析师 | `analysis/rss-startup-analyst.md` | rss-startup |
| 综合分析师（主编） | `analysis/synthesizer.md` | 跨源汇总 |

## 文件结构

```
.claude/skills/collect/
├── SKILL.md
├── REFERENCE.md
├── analysis/                        # 各源分析师 prompt（独立可调）
│   ├── fxb-analyst.md
│   ├── github-analyst.md
│   ├── tech-analyst.md
│   ├── trends-analyst.md
│   ├── xhs-analyst.md
│   ├── rss-ai-analyst.md
│   ├── rss-dev-analyst.md
│   ├── rss-startup-analyst.md
│   ├── cross-source-rules.md        # 跨源分析方法论
│   └── synthesizer.md               # 综合分析师（主编）
└── scripts/
    ├── collect.mjs                  # 协调器
    ├── collectors/
    │   ├── fxb.mjs
    │   ├── gh-trending.mjs
    │   ├── tech-news.mjs
    │   ├── trends.mjs
    │   ├── xhs.mjs
    │   ├── rss-ai.mjs
    │   ├── rss-dev.mjs
    │   ├── rss-startup.mjs
    │   └── _template.mjs
    └── lib/
        ├── fetcher.mjs
        └── rss-parser.mjs
```
