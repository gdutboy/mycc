# 1052 Agent — 详细参考文档

## 目录结构

```
tasks/{任务名}/
└── 1052_communication/
    ├── task_detail.md      # 任务详情（用户输入）
    ├── task_progress.md    # 执行进度（状态追踪）
    ├── agent_list.md       # Agent 列表（生命周期管理）
    ├── system_prompt.md    # 系统提示（Master 用）
    ├── cleanup_log.md      # 清理日志
    ├── destroy_log_*.md    # 销毁记录
    └── sub_agent_*/
        ├── system_prompt.md
        ├── execution_log.md
        └── result.md
```

## 文件职责说明

| 文件 | 作用 | 维护者 |
|------|------|--------|
| `task_detail.md` | 任务详情、用户输入、需求描述 | Master |
| `task_progress.md` | 执行状态：未开始/执行中/已完成/失败 | Master + Sub |
| `agent_list.md` | Agent 列表、状态、角色 | Master |
| `sub_agent_*/execution_log.md` | 执行日志 | Sub |
| `sub_agent_*/result.md` | 执行结果 | Sub |

## Master Agent Prompt 模板

```
你是 1052 Agent 的 Master（主 Agent）。

职责：
1. 接收用户需求，解析任务
2. 规划 Sub Agent 数量和角色
3. 创建和管理 1052 目录结构
4. 监控 Sub Agent 执行状态
5. 汇总结果，执行资源回收

工作方式：
1. 在 tasks/{任务名}/1052_communication/ 下初始化目录
2. 写入 task_detail.md
3. 分析任务，拆分 Sub Agent（最多 5 个）
4. 通过 Agent tool spawn Sub Agent
5. 监控 task_progress.md
6. 汇总 result.md → 最终输出
7. 执行清理
```

## Sub Agent Prompt 模板

```
你是 1052 Agent 的 Sub Agent（执行 Agent）。

角色：{角色名}
职责：{具体任务}
工作目录：tasks/{任务名}/1052_communication/sub_agent_{n}/

工作方式：
1. 读取 ../task_detail.md 了解任务详情
2. 读取 ./system_prompt.md 了解角色要求
3. 执行任务，写入 execution_log.md
4. 完成后写入 result.md
5. 更新 ../task_progress.md 状态

重要规则：
- 只通过文件通信，不直接调用其他 Agent
- 完成后必须写入 result.md
- 遇到问题写入 execution_log.md 并标记失败
```

## 预定义 Sub Agent 模板库

### 搜索 Agent

```markdown
# 搜索 Agent

角色：从 {数据源} 搜索 {目标信息}

任务：
1. 搜索 {数据源}
2. 提取关键信息
3. 写入 result.md（表格格式）
```

### 分析 Agent

```markdown
# 分析 Agent

角色：分析 {输入内容}

任务：
1. 读取输入内容
2. 按 {筛选标准} 分析
3. 写入 result.md
```

### 汇总 Agent

```markdown
# 汇总 Agent

角色：合并多个 Sub Agent 的结果

任务：
1. 读取所有 result.md
2. 合并关键信息
3. 生成 final_result.md
```

## 自动化清理

### 超时清理（30 分钟）

```bash
# 检查超时任务
find ./1052_communication -type d -name "sub_agent_*" -mmin +30

# 清理
rm -rf ./1052_communication/sub_agent_*/
```

### 清理清单

| 清理项 | 说明 |
|--------|------|
| Sub Agent 目录 | 删除 `sub_agent_*/` |
| 临时文件 | 删除临时数据文件 |
| 清理日志 | 写入 `cleanup_log.md` |

## 与 dev-team 的对比

| 维度 | dev-team | 1052agent |
|------|----------|-----------|
| 通信方式 | Task + 消息 | MD 文件 |
| 状态管理 | Task 工具 | task_progress.md |
| 资源回收 | TeamDelete | 强制清理 |
| 适用场景 | 代码开发 | 复杂多步骤任务 |
| 人工卡点 | 3 个 | 可配置 |

## 适用场景

- 复杂任务拆分：需要多个不同角色的 Sub Agent
- 长时任务：需要持久化状态，防止中断丢失
- 信息聚合：多个来源的信息需要汇总
- 需要审计：所有操作记录在 MD 文件中
- 跨会话继续：状态不丢失

## 不做的事

- 不在简单任务上用 1052 架构（用 /dev）
- 不跳过资源清理
- 不在没有 task_detail.md 的情况下开始

## 优化记录

| 日期 | 优化内容 |
|------|---------|
| 2026-03-09 | 初始版本，增加模板库、自动化清理、架构选择指南 |
