---
name: skill-creator
description: 创建、测试和优化 Claude Code Skill。当用户要创建新 skill、改进现有 skill、测试 skill 效果、优化 skill 触发精度时使用。即使用户只说"把这个变成 skill"或"新建技能"也要触发。
---

# Skill Creator

## 触发词

- "帮我创建一个 skill" / "把这个变成 skill" / "新建技能"
- "改进/优化这个 skill" / "skill 触发不准"
- "测试一下这个 skill"

---

## 核心流程

整体循环：**捕获意图 → 写 SKILL.md → 跑测试 → 人工评审 → 改进 → 重复**

根据用户所处阶段灵活切入，不必每次从头走。

---

## Phase 1: 捕获意图

如果对话中已经包含工作流（用户说"把这个变成 skill"），直接从对话提取：用了什么工具、步骤顺序、用户做的修正、输入输出格式。

需要明确的 4 个问题：
1. 这个 skill 让 Claude 做什么？
2. 什么场景/措辞应该触发它？
3. 期望的输出格式是什么？
4. 输出是否可客观验证？（决定是否需要 eval）

主动追问边界情况、依赖项、成功标准。别急着写，先把需求搞清楚。

---

## Phase 2: 编写 SKILL.md

### 目录结构

```
skill-name/
├── SKILL.md          # 必须 - 核心指令
└── 可选资源/
    ├── scripts/      # 可执行脚本（确定性/重复性任务）
    ├── references/   # 参考文档（按需加载，不必全读）
    └── assets/       # 模板、图标等输出资源
```

```bash
mkdir -p .claude/skills/你的skill名
```

### 三层渐进加载

| 层级 | 内容 | 大小建议 |
|------|------|---------|
| 元数据 | name + description | ~100 词，始终在上下文 |
| SKILL.md body | 核心指令 | <500 行，触发时加载 |
| 附加资源 | scripts/ references/ assets/ | 无限制，按需读取 |

超过 500 行时，拆到 references/ 并在 SKILL.md 中指明何时去读。

### frontmatter 写法

```yaml
---
name: skill-name
description: 做什么 + 什么时候触发
---
```

**description 是触发的唯一机制**，必须写得"主动"一点。AI 倾向于 under-trigger（该用不用），所以：

- 不只写"做什么"，还要写"哪些场景该触发"
- 覆盖用户可能的多种说法
- 包含相邻领域的关键词

对比：
- 弱：`生成数据可视化图表`
- 强：`生成数据可视化图表。当用户提到图表、数据展示、dashboard、报表、Excel 可视化、统计图时都应触发，即使没有明确说"图表"。`

### 写作原则

1. **解释 why，不堆 MUST** — AI 有理解力，讲清原因比大写强调更有效。如果你写了 ALWAYS/NEVER，停下来想想能不能换成解释原因
2. **简洁** — 假设 AI 已经很聪明，只告诉它不知道的东西
3. **用示例代替长篇说明** — 一个好例子胜过三段描述
4. **合适的自由度** — 多种有效方法时给文字说明；操作脆弱时给精确脚本

### 存放位置

| 位置 | 作用域 |
|------|--------|
| `~/.claude/skills/` | 个人全局 |
| `项目/.claude/skills/` | 项目级，可 git 共享 |

---

## Phase 3: 测试验证

写完初稿后，别急着交付。创建 2-3 个真实用户会说的测试 prompt，跟用户确认后开始跑。

### 方式 A：快速验证（默认）

直接在真实任务中使用 skill → 发现问题 → 更新 → 重复。适合简单/主观型 skill。

### 方式 B：Eval 驱动验证（推荐用于可客观验证的 skill）

对每个测试 prompt，启动两个 subagent 并行：

1. **with-skill**：带 skill 执行任务，输出保存到 `<skill>-workspace/iteration-N/eval-ID/with_skill/`
2. **baseline**：不带 skill（新建时）或旧版 skill（改进时），保存到 `without_skill/` 或 `old_skill/`

同一轮的所有 subagent 同时启动（不要先跑 with-skill 再跑 baseline）。

等跑的同时，草拟量化断言（assertions）：
- 只对可客观验证的维度写断言（文件是否生成、格式是否正确、关键内容是否包含）
- 主观维度（写作风格、设计质量）留给人工评审
- 断言的名字要一目了然

跑完后：
1. 评分（Grader）— 每个断言 pass/fail + evidence
2. 汇总对比 — with-skill vs baseline 的通过率、耗时、token
3. 展示给用户 — 每个测试的 prompt + 输出 + 评分，让用户留反馈

### 读取反馈

用户反馈为空 = 满意。只关注有具体意见的测试用例。

---

## Phase 4: 改进迭代

根据反馈改进 skill，核心心法：

1. **泛化而非过拟合** — skill 会被用无数次，不要为了当前 2-3 个测试用例加过度具体的规则。如果某个问题很顽固，试试换个角度描述或推荐不同的工作模式
2. **保持精简** — 删掉没用的部分。读 subagent transcript，如果 skill 让 AI 做了很多无意义的事，砍掉那些指令
3. **抽取重复工作** — 如果多个测试中 subagent 都独立写了类似的脚本，说明应该把它提取到 scripts/ 里

改完后进入新一轮 iteration，直到：
- 用户满意
- 反馈全为空
- 没有实质性进展

---

## Phase 5: 描述优化（可选）

skill 功能稳定后，优化 description 的触发精度。

### 创建触发测试集

生成 ~20 条测试查询：

- **should-trigger（8-10 条）**：不同措辞、正式/随意风格、不直接提 skill 名但明显需要它的场景、边缘用例
- **should-not-trigger（8-10 条）**：近似但不该触发的场景（共享关键词但需求不同、相邻领域、有歧义的表述）

关键：测试查询要足够具体和真实（有文件路径、个人背景、具体数据），不要抽象的一句话。负面用例要是"差点就该触发"的近似场景，而非明显无关的请求。

### 迭代优化

用测试集评估当前 description → 找出漏触发和误触发 → 改写 description → 重新测试 → 重复。

展示 before/after 给用户确认。

---

## 参考

- 详细格式规范：同目录下 `REFERENCE.md`
- 官方 Skill 仓库：`https://github.com/anthropics/skills`
