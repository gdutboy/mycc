---
name: collect
description: 多源并行采集，AI 分析后推送飞书简报
layer: 分析层
authorization: A区（自动执行，无需人类介入）
output_levels: L1（结论）
---

# 每日信息采集

三层流水线：纯脚本采集 → 多 Agent 并行分析 → 主编综合 → 统一通知。

## 执行流程

### Step 1：运行采集脚本

```bash
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
TODAY=$(date +%Y-%m-%d)
SAVE_DIR="$PROJECT_ROOT/1-Inbox/_collect/$TODAY"
node "$PROJECT_ROOT/.claude/skills/collect/scripts/collect.mjs" --save "$SAVE_DIR"
```

### Step 2：检查采集状态

- `token_expired`（fxb）→ 发飞书红卡通知，终止该源
- `token_expiring_soon`（fxb）→ 发飞书黄卡预警，不阻断流程
- 其他错误 → 记录在简报中，不阻断
- 全部失败 → 发错误通知，终止

### Step 3：并行分析（8 个 Agent）

**在同一条消息里发出 8 个 Task 调用**，每个 agent 独立分析一个源：

| Agent | 读取数据 | 分析标准 | 输出报告 |
|-------|---------|---------|---------|
| fxb-analyst | `$SAVE_DIR/fxb.json` | `analysis/fxb-analyst.md` | `$SAVE_DIR/fxb-analysis.md` |
| github-analyst | `$SAVE_DIR/gh-trending.json` | `analysis/github-analyst.md` | `$SAVE_DIR/github-analysis.md` |
| tech-analyst | `$SAVE_DIR/tech-news.json` | `analysis/tech-analyst.md` | `$SAVE_DIR/tech-analysis.md` |
| trends-analyst | `$SAVE_DIR/trends.json` | `analysis/trends-analyst.md` | `$SAVE_DIR/trends-analysis.md` |
| xhs-analyst | `$SAVE_DIR/xhs.json` | `analysis/xhs-analyst.md` | `$SAVE_DIR/xhs-analysis.md` |
| rss-ai-analyst | `$SAVE_DIR/rss-ai.json` | `analysis/rss-ai-analyst.md` | `$SAVE_DIR/rss-ai-analysis.md` |
| rss-dev-analyst | `$SAVE_DIR/rss-dev.json` | `analysis/rss-dev-analyst.md` | `$SAVE_DIR/rss-dev-analysis.md` |
| rss-startup-analyst | `$SAVE_DIR/rss-startup.json` | `analysis/rss-startup-analyst.md` | `$SAVE_DIR/rss-startup-analysis.md` |

每个 agent prompt：读取分析标准 → 读取原始数据 → 按格式写报告到输出路径。fxb agent 额外提示：数据已过滤为昨天帖子，直接全量分析。

### Step 4：主编综合

1. 读取 `analysis/cross-source-rules.md` 和 `analysis/synthesizer.md`
2. 读取昨天 briefing（`1-Inbox/_collect/{昨天}/briefing.md`，不存在则跳过）
3. 依次读取 8 份报告
4. 按五步法分析：实体提取 → 关联矩阵 → 信号连续性 → 行动分级 → 选题提取
5. 按 synthesizer.md 格式输出简报（开头必须有"30 秒速读"）

### Step 5：保存简报

写入 `1-Inbox/_collect/{YYYY-MM-DD}/briefing.md`

### Step 6：飞书通知

```bash
node "$PROJECT_ROOT/.claude/skills/tell-me/send.js" "每日简报 | {YYYY-MM-DD}" --file "$SAVE_DIR/briefing.md" blue
touch "$SAVE_DIR/feishu-sent.flag"
```

详细参考：同目录下 REFERENCE.md
