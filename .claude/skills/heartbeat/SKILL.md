---
name: heartbeat
description: 定时唤醒，从焦点池挑任务思考并回报主 cc
layer: 基础层
authorization: A区（自动执行，无需人类介入）
output_levels: L1（结论）
status: intern
created: 2026-03-02
origin: P23 自主运转引擎设计，aster 与 cc 协作
intern_expires: 2026-04-02
---

# /heartbeat — cc 心跳巡逻

> 自主运转引擎：发现问题 → 直接执行 → 记录日志 → 回报主 cc
> 每次必须挑一个焦点做，没有"没事做"这回事。

## 依赖声明

from .claude/skills/reflect/SKILL.md import /reflect

## 执行流程

### Step 1：计算饥饿值

读 `0-Skill-Platform/heartbeat-pool.md`，对每个焦点计算：

```
hunger = wait_hours × frequency_weight
```

按 hunger 降序排列，挑最饿的那个。

### Step 2：执行焦点

**若挑中 f12（cc-todo 扫描）**：读 `0-Skill-Platform/cc-todo.md`，检查：
- cc-todo 区：哪些 pending 任务的 ready 条件已满足
- aster-todo 区：哪些 pending 且触发条件满足（跳过已 `notified`）

**若挑中 f6（scheduler 运行状态）**：读 `.claude/skills/scheduler/history.md`，检查：
1. 是否有"执行中..."超过1小时的任务（卡住检测）
2. 统计最近24小时任务成功率

**若挑中其他焦点**：围绕该焦点思考，产出洞察或建议。

### Step 3：发现问题 → 自主执行

巡逻过程中发现需要处理的问题时，直接执行（无需用户审批）：

1. **可直接处理的问题**（如归档、修改频率、清理等）：
   - 直接执行
   - **记录到执行日志** `0-Skill-Platform/heartbeat-log.md`

2. **复杂问题**：
   - 创建 cc-todo 任务，待后续处理
   - 记录到执行日志

### Step 4：更新 & 回报

1. 更新 heartbeat-pool.md 的"上次"列为当前时间（`YYYY-MM-DD HH:MM`）
2. 更新执行日志（格式见下方）
3. 用 SendMessage 回报主 cc（格式见 REFERENCE.md）

## 硬边界

- 发现问题必须形成闭环：直接处理 或 创建 cc-todo
- 不 spawn 执行者（除非问题明确可自动处理）
- 不调用 /tell-me（只回报"该催了"，由主 cc 决定）
- 执行时间 ≤5 分钟
- 不确定时标注 `confidence: low`，交主 cc 判断

详细参考：同目录下 REFERENCE.md
