# Skill 体系设计综合报告

> 调研时间：2026-03-12
> 调研对象：superpowers（obra/superpowers）、agency-agents（msitarzewski/agency-agents）
> 目的：提取可借鉴的设计规范，用于改进 mycc skill 体系

---

## 一、三套体系横向对比

| 维度 | superpowers | agency-agents | mycc skills |
|------|------------|---------------|-------------|
| **本质** | 工作流纪律强制系统 | 职能角色人格库 | 能力封装+自动化系统 |
| **粒度** | 开发流程步骤级 | 职能角色级 | 任务能力级 |
| **触发方式** | 元 skill 强制 + 描述触发 | 手动指定 | 描述触发 + 定时任务 |
| **有无脚本** | 有（辅助验证） | 无 | 有（TypeScript/Bash/Node） |
| **有无状态** | 无 | 无 | 有（PACE + 记忆系统） |
| **设计哲学** | 对抗 AI 自我合理化 | 专业分工协同 | Agent First 自动化 |
| **Stars** | ~78K | ~30K | - |

**结论**：三套体系不是竞争关系，而是三个不同层次：
- superpowers = **纪律层**（怎么工作）
- agency-agents = **人格层**（谁在工作）
- mycc = **能力层**（能做什么）

mycc 已经有自己的定位优势（有状态、有脚本、有飞书集成），缺的是 superpowers 的纪律层设计。

---

## 二、superpowers 最值得借鉴的 5 个设计

### 1. Description 只写触发条件（最重要）

**原理**：Claude 读完 description 就以为"理解了"，然后按自己的理解执行，跳过读正文。

**当前 mycc 问题**：大部分 skill 的 description 里包含了功能摘要，等于"泄露了答案"。

**改法**：
```
❌ 当前：description: 多源并行采集，AI 分析后推送飞书简报
✅ 改后：description: 当需要采集时政、AI、股票等多源信息并生成简报时使用
```

### 2. 反 Rationalization 段落

Claude 会找借口跳过 skill，常见借口要在 skill 里预先封堵：

```markdown
## 你可能想跳过的理由（都是错的）

| 你的想法 | 为什么不对 |
|---------|-----------|
| "这个任务太简单了" | 简单任务也需要遵循流程 |
| "我已经知道怎么做了" | 知道不等于执行，skill 是检查点 |
| "先做，回头再记录" | 事后记录的信息质量远低于过程中记录 |
```

### 3. 显式调用链（每个 skill 末尾写下一步）

当前 mycc skill 是孤立的，用完就完了。加上显式出口：

```markdown
## 完成后

- 有代码变更 → 调用 `/decision` 记录决策
- 需要通知 → 调用 `/tell-me`
- 发现新任务 → 更新 `0-Skill-Platform/cc-todo.md`
```

### 4. Skill TDD

写新 skill 之前，先记录"现在 Claude 在这个场景下会做什么错误的事"，skill 写完后验证那些错误是否消失。这是 skill 质量保证的核心方法。

### 5. 严格文件大小控制

- SKILL.md 主文件：< 500 行
- 重内容拆到子文件（reference.md、examples/）
- SKILL.md 只引用一层深度

当前 mycc 有些 skill（如 collect）的 SKILL.md 塞了大量流程细节，应该拆出去。

---

## 三、agency-agents 最值得借鉴的 3 个设计

### 1. Deliverables 明确化

每个 Agent 都明确声明"执行后交付什么"，格式清晰：

```markdown
## Deliverables

- **主交付物**：briefing.md（简报文件）
- **副交付物**：分析报告（8个 *-analysis.md）
- **状态标记**：feishu-sent.flag
```

当前 mycc 的 skill 大部分缺少 deliverables 声明，用户/CC 不清楚"做完了"的标志是什么。

### 2. Success Metrics（成功指标）

```markdown
## Success Metrics

- 至少 5 个信息源成功采集
- 简报包含"30 秒速读"
- 飞书通知发送成功（feishu-sent.flag 存在）
```

### 3. Nexus 协调者模式

设立一个专门的协调 skill，负责任务拆解和 skill 分配。
对 mycc 的启发：`dev-team` skill 可以进一步强化协调者角色定义。

---

## 四、对 mycc 的具体改进行动

### 优先级 P0（影响大、改动小）

**A. 修复所有 skill 的 description 格式**

扫描 `.claude/skills/*/SKILL.md`，将 description 全部改为 `Use when...` / `当...时使用` 格式，去掉功能摘要。

预计影响：skill 触发精度大幅提升。

**B. 为高频 skill 添加 Deliverables 声明**

优先级：collect、tell-me、dev、dev-team、heartbeat

**C. 创建 `using-mycc` bootstrap skill**

把 CLAUDE.md 里的 skill 路由规则抽出来，做成一个 meta-skill，加入强制触发逻辑和反 rationalization。

### 优先级 P1（影响大、改动中等）

**D. 关键 skill 加显式调用链**

优先：pace-workflow、dev、collect、heartbeat

**E. 重构过长的 skill**

collect/SKILL.md 的流程步骤太详细，应该只保留决策逻辑，流水线细节移到 REFERENCE.md。

### 优先级 P2（有价值但不紧急）

**F. 引入 Skill TDD 实践**

下次写新 skill 时先记录失败行为，写完后验证。

**G. 整理 skill 三层分类体系**

参考 superpowers 的 Meta / Process / Implementation 分类，为 mycc 建立分类标签。

---

## 五、今日最重要的一个行动

**立即做：把 `collect` skill 的 description 改成触发条件格式，并加上 Deliverables 声明。**

这是成本最低、效果最明显的单点改进，改完可以作为模板推广到其他 skill。

---

## 参考
- 详细调研报告：`1-Inbox/superpowers-research.md`
- 详细调研报告：`1-Inbox/agency-agents-research.md`
