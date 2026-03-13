---
name: evolve
description: Use when 用户要对比 GitHub Trending 最新项目与 mycc 现有 skill 体系的差距，并产出升级建议、能力缺口或进化方向时触发；不用于普通趋势播报、单次采集或只解释某个 skill 的场景
---

# cc 自进化巡检

## 触发词

- `/evolve` — 立即执行一次巡检
- `自进化`、`升级检查`、`cc 进化`
- 定时：每天凌晨 3 点自动触发

## 执行步骤

### 立即触发时

```bash
node .claude/skills/evolve/scripts/scan.mjs
```

输出报告后，用 `/tell-me` 推送飞书。

### 等待用户回复

- **"升级 <repo名>"** → 拉起 `/dev` 流程实现对应能力，更新 watchlist 状态为"已覆盖"
- **"备用 <repo名>"** → 追加到 `0-Skill-Platform/evolve-log.md`，更新 watchlist 状态为"观望"
- **"忽略 <repo名>"** → 更新 watchlist 状态为"已覆盖"

## 文件说明

| 文件 | 用途 |
|------|------|
| `scripts/scan.mjs` | 扫描 + 评分 + 报告生成 |
| `scripts/watchlist.md` | 关注仓库列表（可手动编辑添加） |
| `scripts/scan.test.mjs` | 单元测试 |

## 注册定时任务（凌晨 3 点）

首次使用前，在 mycc 对话中执行：

```
请帮我注册一个每天凌晨 3 点的定时任务，触发 /evolve 巡检
```

或手动通过 scheduler skill 注册，prompt 设置为：`执行 /evolve 自进化巡检`，时间 `03:00`。

## watchlist 维护

编辑 `scripts/watchlist.md`，格式：

```
- owner/repo | 状态 | 备注
```

状态：`必看` / `观望` / `已覆盖`
