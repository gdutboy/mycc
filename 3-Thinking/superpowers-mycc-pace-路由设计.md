# superpowers、mycc 与 PACE 的路由设计

## 结论先说

这套系统最稳的结构不是“全靠 superpowers”，也不是“全靠本地 skill 路由”，而是三层分工：

- **mycc skill**：识别任务领域
- **superpowers**：约束执行流程
- **PACE**：保证治理与留痕

一句话：

> **业务 skill 决定做什么，superpowers 决定怎么做，PACE 决定怎么留痕。**

---

## 一、为什么不能只靠 superpowers

superpowers 很强，但它本质上是**流程型能力**，不是完整的业务路由系统。

它更擅长回答：
- 现在该不该先 brainstorm？
- 该不该写计划？
- 该不该 TDD？
- 该不该 review、verify、收尾？

但它不擅长替你决定：
- 这是写文章还是写代码？
- 这是定时任务还是桌面自动化？
- 这是在做 skill 沉淀还是只是解释 skill？

这部分更适合由 mycc 的业务 skill 承担。

---

## 二、为什么不能只靠 mycc skill

只靠本地 skill 路由也不够。

原因很简单：业务 skill 解决的是“进哪个门”，但不能天然保证过程纪律。

比如：
- `dev` 能把任务带进开发域，但不自动保证先设计、先测试、先验证
- `dev-team` 能识别复杂开发，但不天然保证并行任务拆得对
- `skill-creator` 能进入 skill 开发域，但不天然保证用 TDD 思路打磨 description 和测试场景

这就是 superpowers 的价值：把过程从“凭感觉”变成“有顺序、有检查点”。

---

## 三、为什么还要 PACE

superpowers 解决的是 Claude 的做事方式，PACE 解决的是项目的治理方式。

当任务开始涉及：
- 多文件修改
- artifact 联动
- 计划审批
- 变更索引
- 验证留痕
- 跨会话追踪

就不能只靠对话记忆或 skill 流程，要有稳定的 artifact 和状态机。

所以 PACE 是治理层，不是普通技能层。

---

## 四、三个典型冲突

### 1. `dev` 和 TDD 看起来像重复，实际上不是

它们职责不同：

- `dev`：告诉系统“这是开发任务”
- `superpowers:test-driven-development`：告诉系统“开发时按什么纪律执行”

所以正确关系不是替代，而是叠加。

### 2. `dev-team` 和并行 superpowers 看起来像重复，实际上是上下层

- `dev-team`：说明这是一个复杂开发场景，可能需要多人/多 Agent 协作
- `dispatching-parallel-agents`：判断是否真的适合并行
- `subagent-driven-development`：实际怎么并行执行

所以 `dev-team` 是入口，superpowers 是执行机制。

### 3. `pace-workflow` 和 `writing-plans` 看起来会打架，实际上分工不同

- `writing-plans`：更偏实现前的思考与拆解
- `pace-workflow`：更偏项目级治理、artifact、审批和验证

如果任务只是中型实现，可以只用 `writing-plans`。
如果任务已经进入治理级复杂度，就由 PACE 接管，并吸收 plan 产物。

---

## 五、最常见的误触发根因

### 1. description 写成了“做什么”，没写“什么时候用”

这是最典型问题。

例如：
- “创建、测试和优化 skill”
- “查看当前 skill 列表、平台状态总览”

这种写法会导致只要碰到相关关键词，就容易误触发。

更好的写法应该是：
- 什么时候触发
- 哪些边界不触发
- 覆盖哪些近义表达

### 2. 把解释类请求和执行类请求混在一起

“解释 skill” 和 “改 skill” 完全不是一回事。
“介绍流程” 和 “启动某个流程” 也不是一回事。

如果 description 不写排除条件，误触发几乎必然发生。

### 3. 只覆盖标准说法，不覆盖真实口语

用户不会总说：
- “这是一个 bug”
- “请做 code review”
- “请开始 implementation plan”

用户更常说：
- “白屏了”
- “怎么挂了”
- “帮我过一遍”
- “先梳理一下”

所以触发词不能只写官方术语。

---

## 六、最常见的漏触发根因

### 1. 复杂任务没有被识别成规划任务

用户经常不会主动说“先规划”，但任务本身已经是规划型任务。

比如：
- 重构
- 梳理
- 升级
- 技术选型
- 多模块改造

这类如果不进 `writing-plans` 或 `pace-workflow`，后面很容易乱。

### 2. 调试信号只识别了“bug”这个词

真实世界里，用户更常说的是：
- 接口 500
- 页面白屏
- 测试全红
- 不生效
- 卡住了

如果 description 不覆盖这些口语，`systematic-debugging` 就会漏触发。

---

## 七、最合理的长期策略

### 1. 先收敛高冲突 skill

优先修改：
- `dev`
- `dev-team`
- `skill-creator`
- `create-system`
- `dashboard`
- `scheduler`

因为它们最容易互相抢活。

### 2. description 先改，正文后改

先改 frontmatter 的收益最大、风险最小。

如果一上来就大改正文、hook、自动化逻辑，排查成本会迅速上升。

### 3. 先压误触发，再补漏触发

误触发的破坏通常比漏触发更大。

因为误触发会把对话直接带偏；漏触发通常还能在后续补救。

### 4. 真正评估效果，要看真实对话

description 的好坏，不是靠想象判断，而是靠真实请求中的表现。

所以最佳实践不是一次性把全部 skill 重写，而是：
- 小步改
- 看真实效果
- 再继续扩面

---

## 八、这套体系最终想要的状态

理想状态下：

- 用户一开口，mycc 能先判断这是哪个业务域
- 进入业务域后，superpowers 自动补上正确流程
- 一旦任务复杂度上升，PACE 自动接管治理

这样整套系统就不是一堆零散 skill，而是一个分层协作的操作系统。

---

## 九、后续可继续做的事

1. 给更多 skill 补 description 边界
2. 建立 should-trigger / should-not-trigger 测试集
3. 对高频误触发场景做对话回放复盘
4. 逐步把路由规范反哺到 hooks 或自动评估脚本

---

## 十、当前版本的判断

当前路线是对的。

不是把某一套体系干掉，而是让三套体系各守边界：

- **mycc** 管业务入口
- **superpowers** 管执行纪律
- **PACE** 管工程治理

这才是最稳、最能长期演化的组合方式。
