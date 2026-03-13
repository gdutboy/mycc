# Skill Routing Spec

## 目标

统一 mycc 项目中的 skill 路由规则，降低误触发与漏触发，明确 **业务 skill / superpowers / PACE** 三层职责。

---

## 一、三层模型

### 1. 业务层：决定做什么

业务层 skill 负责识别用户任务类型，并进入对应工作域。

常见映射：

| 用户意图 | 主 skill |
|---|---|
| 写代码 / 修 bug / 实现功能 | `dev` |
| 多模块并行开发 | `dev-team` |
| 写文章 / 大纲 / 初稿 / 润色 / 公众号 | `create-system` |
| 定时任务 / 周期执行 | `scheduler` |
| 飞书通知 | `tell-me` |
| 桌面自动化 | `desktop` |
| 创建或优化 skill | `skill-creator` |
| 查看能力看板 | `dashboard` |

### 2. 流程层：决定怎么做

superpowers 负责约束过程，不替代业务 skill。

常见映射：

| 场景 | superpowers |
|---|---|
| 新功能、改行为、需要先想清楚 | `superpowers:brainstorming` |
| 多步骤任务需写计划 | `superpowers:writing-plans` |
| 开始实现功能或修 bug | `superpowers:test-driven-development` |
| 遇到 bug / 报错 / 测试失败 | `superpowers:systematic-debugging` |
| 存在多个独立子任务 | `superpowers:dispatching-parallel-agents` |
| 按计划并行落地 | `superpowers:subagent-driven-development` |
| 实现完成后请求审查 | `superpowers:requesting-code-review` |
| 收到 review 后准备修改 | `superpowers:receiving-code-review` |
| 声称完成前先验证 | `superpowers:verification-before-completion` |
| 收尾、PR、合并、清理分支 | `superpowers:finishing-a-development-branch` |

### 3. 治理层：决定如何留痕

PACE 负责计划文件、artifact、审批、验证、任务状态等治理要求。

优先使用：
- `pace-workflow`
- `pace-bridge`
- `artifact-management`
- `change-management`

---

## 二、路由优先级

按以下顺序判断：

1. **用户显式指定**
   - 例：`/dashboard`、`用 dev`、`开 worktree`
2. **业务 skill**
   - 先识别任务领域
3. **superpowers 流程 skill**
   - 再补充执行流程约束
4. **PACE 治理 skill**
   - 达到复杂度或治理要求时启用

> 规则：**业务 skill 决定做什么，superpowers 决定怎么做，PACE 决定怎么留痕。**

---

## 三、组合规则

### 1. 普通开发

```text
用户要实现功能 / 修 bug
→ dev
→ 视情况叠加 brainstorming / writing-plans / TDD / verification
```

### 2. 复杂并行开发

```text
用户要做多模块、多子任务、前后端并行开发
→ dev-team
→ 视情况叠加 writing-plans / dispatching-parallel-agents / subagent-driven-development
```

### 3. 排障修复

```text
用户报告异常、报错、失败、白屏、不生效
→ dev
→ systematic-debugging
→ 确认进入修复实现后再进入 TDD
```

### 4. skill 开发

```text
用户要新建 / 修改 / 测试 skill
→ skill-creator
→ superpowers:writing-skills
```

### 5. 创作任务

```text
用户明确要产出内容
→ create-system
→ 再路由到 outline / draft / polish / title / gzh
```

---

## 四、误触发控制规则

### 1. 解释类请求不应误入执行类 skill

以下请求默认是解释/说明，不应直接触发执行型 skill：
- “这个 skill 是干嘛的？”
- “superpowers 的触发词是什么？”
- “解释一下这个流程”
- “这个规则什么意思？”

处理原则：
- 先回答说明
- 不因出现 `skill`、`superpowers`、`流程` 等词就直接进入 `skill-creator`、`dashboard`、`dev`

### 2. 方法讨论不应误入内容产出

以下请求不应触发 `create-system`：
- “怎么写公众号？”
- “写作流程怎么设计？”
- “标题策略有什么套路？”

只有在用户明确要产出内容时，才触发创作类 skill。

### 3. 普通开发不应误入 dev-team

以下情况不触发 `dev-team`：
- 单文件或单模块改动
- 普通单人开发
- 没有明显可并行子任务

---

## 五、漏触发补强规则

### 1. 调试类近义表达要覆盖

以下表达应视为调试信号：
- 报错
- 异常
- 白屏
- 挂了
- 卡住
- 不生效
- 结果不对
- 测试全红
- 接口 500

### 2. 复杂任务即使没说“规划”也要考虑写计划

以下表达应视为规划信号：
- 重构
- 梳理
- 升级
- 重做
- 架构调整
- 多文件修改
- 技术选型
- 方案设计

### 3. code review 近义表达要覆盖

以下表达应视为 review 信号：
- 审一下
- 帮我 review
- 过一遍
- 看看有没有问题
- 看看有没有隐患

---

## 六、冲突处理规则

### 1. `dev` vs `superpowers:test-driven-development`

不是二选一。

- `dev`：业务入口
- `TDD`：实现流程约束

### 2. `dev-team` vs 并行 superpowers

不是二选一。

- `dev-team`：复杂开发场景入口
- `dispatching-parallel-agents`：判断是否适合并行
- `subagent-driven-development`：实际并行落地方式

### 3. `pace-workflow` vs `superpowers:writing-plans`

按职责区分：

- **需要 artifact、审批、治理留痕** → `pace-workflow`
- **需要实现前思考和拆解** → `writing-plans`

如果同时满足，两者可叠加，但由 PACE 统筹治理。

---

## 七、description 编写规范

所有 SKILL frontmatter 的 `description` 建议遵守：

1. 只写 **什么时候用**
2. 不写详细流程
3. 写清边界与排除项
4. 尽量覆盖近义表达
5. 避免把“解释类请求”写成“执行类触发条件”

推荐格式：

```yaml
description: Use when [明确触发场景]；不用于 [容易误触发的边界场景]
```

---

## 八、维护建议

优先维护以下易冲突 skill 的 description：
- `dev`
- `dev-team`
- `skill-creator`
- `create-system`
- `dashboard`
- `scheduler`

后续若继续优化，建议补充：
- `collect`
- `decision`
- `reflect`
- `desktop`
- `tell-me`

---

## 九、落地原则

- 小步修改 description，先修高冲突 skill
- 先降低误触发，再逐步补漏触发
- 不在一次迭代中同时大改 description、正文流程、hooks
- 路由规则变化后，优先在真实对话中观察效果，再决定是否继续扩面
