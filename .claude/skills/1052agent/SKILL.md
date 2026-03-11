---
name: 1052agent
description: 动态双主多智能体协同架构
layer: 执行层
authorization: B区（生成候选，通知人审核）
output_levels: L2（能力）
status: experimental
created: 2026-03-09
origin: 1052 Agent 方法论
---

# 1052 Agent — 动态双主多智能体协同架构

## 架构选择

| 任务类型 | 推荐架构 |
|---------|---------|
| 简单任务（<5分钟） | /dev |
| 代码开发（需测试保障） | /dev-team |
| 复杂长时任务（需状态追溯） | 1052agent |

## 执行流程

### Step 1: 初始化通信目录

在任务目录下创建 `tasks/{任务名}/1052_communication/`，写入：
- `task_detail.md`：用户需求
- `task_progress.md`：初始状态（未开始）
- `agent_list.md`：空列表

### Step 2: 创建 Sub Agent

按任务需求拆分角色，为每个 Sub Agent：
1. 创建 `sub_agent_{n}/system_prompt.md`（角色定义）
2. 更新 `agent_list.md`
3. 通过 Agent tool spawn Sub Agent

### Step 3: Sub Agent 执行

每个 Sub Agent：
1. 读取 `task_detail.md` + 自身 `system_prompt.md`
2. 执行任务，写入 `execution_log.md`
3. 完成后写入 `result.md`，更新 `task_progress.md`

### Step 4: 结果汇总

Master 读取所有 `sub_agent_*/result.md`，合并生成最终结果。

### Step 5: 资源回收

1. 停止所有 Sub Agent
2. 删除 `sub_agent_*/` 目录
3. 写入 `cleanup_log.md`

## 边界规则

- Agent 数量上限：5 个
- 单任务超时：30 分钟
- 任务完成后必须清理子目录
- 无 `task_detail.md` 时不得开始

详细参考：同目录下 REFERENCE.md
