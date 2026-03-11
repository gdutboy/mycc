# heartbeat 心跳巡逻系统 — 验收任务

## 背景

heartbeat 是一个 prompt-based skill，通过定时唤醒、从焦点池挑最饿的焦点进行思考/检查并回报主 cc。本任务记录该系统的搭建进度与验收标准。

## 需创建/修改的文件

| 文件 | 操作 |
|------|------|
| `0-Skill-Platform/heartbeat-pool.md` | 新建（焦点池） |
| `0-Skill-Platform/cc-todo.md` | 新建（待办清单） |
| `.claude/skills/heartbeat/SKILL.md` | 修改（移除 /reflect 依赖） |
| `.claude/skills/scheduler/tasks.md` | 修改（注册定时任务） |

## 待办

- [ ] 创建 `0-Skill-Platform/heartbeat-pool.md`
- [ ] 创建 `0-Skill-Platform/cc-todo.md`
- [ ] 修改 `SKILL.md`，移除 `/reflect` 依赖行
- [ ] 在 `scheduler/tasks.md` 注册 heartbeat 定时任务
- [ ] 手动触发 `/heartbeat` 做一次冒烟测试

## 验收测试清单

### 1. 文件存在性

- [ ] `0-Skill-Platform/heartbeat-pool.md` 文件存在
- [ ] `0-Skill-Platform/cc-todo.md` 文件存在
- [ ] `.claude/skills/heartbeat/SKILL.md` 已更新（无 /reflect 依赖行）
- [ ] `.claude/skills/scheduler/tasks.md` 包含 heartbeat 条目

---

### 2. heartbeat-pool.md 格式

- [ ] 文件包含 Markdown 表格，列头含：`ID`、`焦点名`、`频率`、`上次`、`产出去向`（顺序不限，列名允许小幅变体）
- [ ] `ID` 列格式为 `f{数字}`，如 f1、f12
- [ ] `频率` 列内容与底部频率参考表的权重值对应（如"每日"、"每周"等可识别关键词）
- [ ] `上次` 列格式为 `YYYY-MM-DD HH:MM` 或 `-`（首次）
- [ ] `产出去向` 列内容可映射到有效区域（如 A区、B区、MEMORY 等）
- [ ] 底部有**频率参考表**，包含频率关键词与 frequency_weight 对应关系
- [ ] 饥饿值公式可计算：`hunger = wait_hours × frequency_weight`，两个变量均可从表格数据中提取

---

### 3. cc-todo.md 格式

- [ ] 文件中存在明确标识的 **cc-todo 区**（如 `## cc-todo` 标题或等效标记）
- [ ] 文件中存在明确标识的 **aster-todo 区**（如 `## aster-todo` 标题或等效标记）
- [ ] cc-todo 区中每条任务包含：ID、任务名、状态（pending/done 等）、ready 条件
- [ ] ready 条件列包含可程序化判断的模式，如："每周X"、"每月X号"、"{ID} done"、"文件存在"
- [ ] aster-todo 区中每条事项包含：ID、事项描述、触发条件、状态（pending/notified）
- [ ] aster-todo 条目状态字段值域为 `pending` 或 `notified`，无其他歧义值

---

### 4. SKILL.md 完整性

- [ ] 文件中**不含** `from .claude/skills/reflect/SKILL.md import /reflect` 这行（或任何引用 /reflect 的依赖声明）
- [ ] `heartbeat-pool.md` 读取路径为 `0-Skill-Platform/heartbeat-pool.md`，与实际文件位置一致
- [ ] `cc-todo.md` 读取路径为 `0-Skill-Platform/cc-todo.md`，与实际文件位置一致
- [ ] 巡逻流程 Step 1/2/3 描述完整，无空白步骤
- [ ] 回报格式模板（f12 格式 + 其他焦点格式）均存在

---

### 5. scheduler 注册

- [ ] `.claude/skills/scheduler/tasks.md` 中存在包含 `heartbeat` 关键词的任务行
- [ ] 该行包含触发间隔或 cron 表达式（如"每小时"、"1h"等）
- [ ] 该行包含触发命令或触发词（如 `/heartbeat` 或 `心跳巡逻`）

---

### 6. 功能验证（冒烟测试）

手动触发 `/heartbeat`，验证以下行为：

- [ ] cc 成功读取 `heartbeat-pool.md`，无报错
- [ ] cc 对所有焦点计算了饥饿值（输出或日志中可见排序结果）
- [ ] cc 选出了**唯一一个**最饿的焦点（或多个并列时按优先级规则选一）
- [ ] 回报格式符合 SKILL.md 模板（含 `## [heartbeat]` 标题、**已更新** 行）
- [ ] `heartbeat-pool.md` 中被选中焦点的 `上次` 列更新为当前时间（`YYYY-MM-DD HH:MM`）
- [ ] 整个执行时间 ≤ 5 分钟

---

### 7. 边界条件

| 场景 | 预期行为 | 通过 |
|------|----------|------|
| 焦点池为空（0 行数据） | 回报"焦点池为空，无可执行焦点"，不崩溃 | [ ] |
| 所有焦点饥饿值完全相同 | 优先选 `产出去向` 为 A区 的焦点；若无 A区 则选第一行 | [ ] |
| 某焦点 `上次` 列为 `-`（首次执行） | wait_hours 用创建日期计算，不报错、不跳过 | [ ] |
| 饥饿值差距 < 10%（多个焦点相近） | 按"A区优先"规则选出唯一焦点，回报中注明并列情况 | [ ] |

---

### 8. 异常处理

| 异常场景 | 预期行为 | 通过 |
|----------|----------|------|
| `heartbeat-pool.md` 文件不存在 | 输出明确错误提示，提示用户创建该文件，不继续执行后续步骤 | [ ] |
| `cc-todo.md` 文件不存在（当 f12 被选中时） | 输出明确错误提示，说明 cc-todo.md 缺失，回报中标注 `confidence: low` | [ ] |
| 某焦点 `上次` 列格式不合法（非日期非 `-`） | 跳过该焦点并在回报中注明"格式异常，已跳过" | [ ] |
| frequency_weight 找不到对应值 | 使用默认权重（1.0）或报错说明，不静默失败 | [ ] |

---

## 下一步

完成上述文件创建后，按顺序执行：
1. 逐项勾选验收清单
2. 发现问题记录到本文件"问题记录"区
3. 全部通过后将本任务归档至 `5-Archive/`

## 问题记录

> 执行验收过程中发现的问题记录于此。
