---
name: dev-team
description: 多 Agent 团队协作开发，支持标准与快速两种模式
layer: 执行层
authorization: B区（生成候选，通知人审核）
output_levels: L2（能力）
status: active
created: 2026-02-09
origin: AI Agents 协作开发范式探讨沉淀
---

# dev-team 执行流程

## 依赖声明

from .claude/skills/test-review/SKILL.md import /test-review
from .claude/skills/dev/SKILL.md import /dev

---

## 触发判断

- 含 "jarvis" / "贾维斯" / "并行开发" / "多代理" → **快速模式**
- 含 "/dev-team" / "组队开发" / "团队模式开发" → **标准模式**

---

## 标准模式（TDD Pipeline）

任务链 T1-T9，三个人工卡点（✋）：

```
T1: 需求澄清（Lead）
T2: 写测试（dev）     blockedBy: T1
T3: 审查测试（reviewer）  blockedBy: T2，执行 /test-review
T4: ✋ 人审核测试（Lead）  blockedBy: T3
T5: 写代码实现（dev）  blockedBy: T4
T6: 跑测试+报告（dev） blockedBy: T5
T7: ✋ 人验收（Lead）  blockedBy: T6
T8: 文档同步（reviewer）blockedBy: T7
T9: ✋ 人确认文档（Lead） blockedBy: T8
```

执行步骤：
1. TeamCreate → team_name: "dev-{功能名}"
2. 读项目 00-项目定义.md，创建 tasks/{功能名}.md
3. TaskCreate T1-T9，设置 blockedBy 依赖
4. spawn dev Agent + reviewer Agent（general-purpose）
5. 各 Agent 用 TaskList 查任务 → TaskUpdate 认领 → 完成后标 completed
6. Lead 在 ✋ 卡点汇报，等人说"过"再继续

**关键规则**：测试失败改代码不改测试；文档按 00-项目定义.md 变更矩阵同步。

---

## 快速模式（Jarvis）

并行执行，只有最终一个人工卡点：

1. Lead 拆解需求为**可独立并行**的子任务
2. 同时 spawn 多个 Agent（最多 5 个），每人负责一个子任务
3. 每个 Agent：读代码 → 实现功能 + 写测试 → 跑测试 → TaskUpdate completed
4. 所有完成后，Lead 跑全量测试 → 汇报 → ✋ 人验收
5. 有强依赖的任务 → 降级为标准模式

---

## 关闭流程

1. 任务文档标「已完成」，移到 tasks/done/
2. SendMessage type: shutdown_request → dev, reviewer
3. TeamDelete

---

详细参考：同目录下 REFERENCE.md
