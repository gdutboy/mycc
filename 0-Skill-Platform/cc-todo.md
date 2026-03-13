# CC 待办清单

> heartbeat 巡逻员定期扫描此文件，检查 pending 任务的 ready 条件。
> **只有主 cc 可以修改此文件**，巡逻员只读不写。

---

## cc-todo

| ID | 任务名 | 状态 | ready 条件 | 备注 |
|----|--------|------|-----------|------|
| c1 | 每周复盘 | done | 每周日 | 已归档到 5-Archive/周记/2026-03-09~03-11.md |
| c2 | status 快照 | done | 每日 | 已更新 status.md 并追加到 context.md |
| c3 | 归档 stockquant 历史文档 | done | 随时 | 已归档到 5-Archive/stockquant-历史文档/ |
| c4 | 调整 1052-agent 巡检频率 | done | 随时 | f1 项目检查频率从每日改为每周 |

---

## aster-todo

> 用户相关的待办/提醒事项。触发条件满足时回报主 cc，由主 cc 决定是否通知用户。

| ID | 事项 | 触发条件 | 状态 | 备注 |
|----|------|----------|------|------|
| a1 | 示例：检查服务器续费 | 2026-04-01 | pending | 提前提醒 |

---

## 状态说明

- **cc-todo 状态**：`pending`（待执行）、`done`（已完成）
- **aster-todo 状态**：`pending`（待提醒）、`notified`（已通知，不再重复）
