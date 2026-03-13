# Skill Routing Trigger Test Set - Round 1 Results

> 评估日期：2026-03-13
> 评估方式：人工静态回放（基于当前各 skill frontmatter `description` 判断）
> 说明：本轮不是自动化实测，而是按当前路由文案做人审回放，用于先找出明显通过项与高风险边缘项。

---

## 本轮结论

- `Should-trigger` 主样本整体边界已基本成立，首轮人工判断 **12/12 符合预期**。
- `Should-not-trigger` 主样本首轮人工判断 **12/12 符合预期**。
- 风险主要集中在 **边缘表达**，尤其是：
  - `E02`：`dashboard` 的“看下/长什么样”口语表达是否稳定触发打开看板，而不是解释。
  - `E04`：`skill description 有没有明显漏洞` 这类审阅式请求，是否会被 `skill-creator` 抢走。
  - `E05`：既有“定期看看”又有“先别创建任务”的句子，是否会被 `scheduler` 过早触发。

---

## Should-trigger 回放结果

| ID | 测试语句 | 期望主 skill | 人工判断 | 结果 | 备注 |
|---|---|---|---|---|---|
| T01 | 帮我把 `.claude/skills/dashboard/SKILL.md` 的 description 改得更窄一点，别再误触发解释类请求了。 | `skill-creator` | `skill-creator` | PASS | 明确是修改已有 skill + 校准触发精度 |
| T02 | 这个 Node 服务现在接口 500，测试也全红了，先帮我排查根因再修。 | `dev` | `dev` | PASS | 明确要修已确认问题；后续可叠加调试流程 |
| T03 | 我想做一个新 skill，专门把调试过程沉淀成 SOP。 | `skill-creator` | `skill-creator` | PASS | 新建 skill 信号很强 |
| T04 | 帮我写一篇公众号，主题是“为什么 description 比 hooks 更该先治理”。 | `create-system` | `create-system` | PASS | 明确要产出创作内容 |
| T05 | 先给这篇文章列个结构，我想看三段式提纲。 | `create-system` | `create-system` | PASS | 创作内容生产入口，后续再细分到 `outline` |
| T06 | 看看我这个月 Claude Code 花了多少，token 用量也顺便看下。 | `cc-usage` | `cc-usage` | PASS | 与 `cc-usage` description 高度贴合 |
| T07 | 给我开一下 cc 能力看板，我想看看现在有哪些 skill。 | `dashboard` | `dashboard` | PASS | 明确要打开/查看看板 |
| T08 | 帮我加一个每天早上 9 点检查 heartbeat-pool 的定时任务。 | `scheduler` | `scheduler` | PASS | 新增定时任务安排 |
| T09 | 刚才我们已经决定先做 description 收敛，再做触发测试集，记个决策。 | `decision` | `decision` | PASS | 已形成明确结论 |
| T10 | 把今天这轮 skill 路由治理的结果发飞书给我。 | `tell-me` | `tell-me` | PASS | 明确要求推送到飞书 |
| T11 | 把最近一周 GitHub AI 项目、Claude 更新和量化交易相关新闻收成一页简报。 | `collect` | `collect` | PASS | 多源采集 + 汇总简报 |
| T12 | 这个功能拆成前端改造、hooks 迁移、文档同步三块，让多个 agent 并行推进。 | `dev-team` | `dev-team` | PASS | 明确可拆成并行开发任务 |

---

## Should-not-trigger 回放结果

| ID | 测试语句 | 不应误触发 skill | 人工判断 | 结果 | 备注 |
|---|---|---|---|---|---|
| N01 | `dashboard` 这个 skill 是干嘛的？ | `dashboard` | 不应触发 `dashboard` | PASS | 属于解释类请求 |
| N02 | superpowers 的触发词到底怎么判断？ | `skill-creator`, `dashboard` | 不应触发这两者 | PASS | 这是规则说明，不是改 skill / 开看板 |
| N03 | 怎么写公众号标题更容易点开？ | `create-system`, `title` | 不应触发这两者 | PASS | 讨论写作方法，不是直接产出内容 |
| N04 | scheduler 的机制是 cron 还是别的？ | `scheduler` | 不应触发 `scheduler` | PASS | 纯机制解释 |
| N05 | tell-me 现在到底支持发什么内容？ | `tell-me` | 不应触发 `tell-me` | PASS | 能力说明，不是发送动作 |
| N06 | 我在想要不要把 skill 路由也做成测试框架，你怎么看？ | `dev`, `skill-creator` | 不应触发这两者 | PASS | 属于方案讨论 |
| N07 | 帮我看看这个决策记录写得清不清楚。 | `decision` | 不应触发 `decision` | PASS | 审阅现有内容，不是新增决策 |
| N08 | 最近总感觉路由有点乱，晚点得系统复盘一下。 | `reflect` | 不应触发 `reflect` | PASS | 只是轻量感受，不是明确复盘请求 |
| N09 | 先解释一下 `dev-team` 和并行 superpowers 的区别。 | `dev-team` | 不应触发 `dev-team` | PASS | 概念解释，不是执行并行开发 |
| N10 | 我想知道 collect 这个 skill 都会抓哪些来源。 | `collect` | 不应触发 `collect` | PASS | 解释来源，不是发起采集 |
| N11 | 如果以后要做一个新的通知系统，也许可以参考 tell-me。 | `tell-me` | 不应触发 `tell-me` | PASS | 泛讨论，不是推送通知 |
| N12 | 我准备明天再处理这个 bug，现在先讲讲为什么会误触发。 | `dev` | 不应触发 `dev` | PASS | 原因分析，不是立即开发/修复 |

---

## 边缘样本观察

| ID | 测试语句 | 首轮判断 | 风险等级 | 观察 |
|---|---|---|---|---|
| E01 | 先梳理一下 skill 路由，等会儿再决定要不要改。 | 暂不应触发 `skill-creator` | 中 | 现在更像分析/梳理，不是立即改 skill |
| E02 | 看下 dashboard 现在长什么样。 | 倾向触发 `dashboard` | 高 | “看下/长什么样”既像打开看板，也可能被误当成解释请求 |
| E03 | 这个问题像 bug，但我现在只想知道可能原因。 | 暂不应触发 `dev` | 中 | description 已写“不用于只做原因分析”，边界合理 |
| E04 | 帮我过一遍这套 skill description 有没有明显漏洞。 | 暂不直接触发 `skill-creator` | 高 | 容易和“修改/测试 skill”混淆；更像 review / analysis 请求 |
| E05 | 想定期看看 GitHub AI 趋势，但先别创建任务。 | 暂不应触发 `scheduler` | 高 | “定期看看”很像 scheduler，但后半句明确否定创建任务 |

---

## 当前最值得继续验证的点

1. **`dashboard` 的查看型口语是否足够稳**
   重点看“打开/开一下/看下/长什么样”这些表达，是否会和解释类请求混淆。

2. **`skill-creator` 是否会吞掉审阅型请求**
   像“过一遍 description 有没有漏洞”“帮我看看这个 skill 写得准不准”这类句子，可能介于 review 与修改之间。

3. **`scheduler` 是否能正确识别否定条件**
   含有“定期”“每天”“周期”但又带“先别创建”“先讨论一下”的句子，要重点防过早执行。

---

## 第二轮边缘样本回放（聚焦 E02 / E04 / E05）

> 说明：本轮依然是人工回放，但判断标准从“静态 description 是否覆盖”进一步收紧为“如果按当前路由语气去选，最可能落到哪里”。

| ID | 测试语句 | 首轮判断 | 第二轮判断 | 结果 | 风险说明 | description 调整建议 |
|---|---|---|---|---|---|---|
| E02 | 看下 dashboard 现在长什么样。 | 倾向触发 `dashboard` | 仍倾向触发 `dashboard` | 保持通过 | 这句话更像“打开给我看”，不是“解释 dashboard 是什么”；`dashboard` 当前 description 已覆盖“打开或查看” | 暂不修改；后续真实回放重点观察“看下/长什么样”是否被误答成解释 |
| E04 | 帮我过一遍这套 skill description 有没有明显漏洞。 | 暂不直接触发 `skill-creator` | 暂不触发 `skill-creator` | 保持通过 | 这更像审阅/分析请求，不是“修改已有 skill”也不是“测试 skill 效果”；如果硬触发 `skill-creator`，容易过早进入改 skill 流 | 可考虑给 `skill-creator` 增一条排除语义：不用于只做审阅、点评、解释类请求 |
| E05 | 想定期看看 GitHub AI 趋势，但先别创建任务。 | 暂不应触发 `scheduler` | 暂不触发 `scheduler` | 保持通过 | 前半句有 scheduler 信号，但后半句明确否定执行动作；当前 `scheduler` description 已写“不用于普通提醒说明”，方向对 | 可考虑补强否定边界：不用于只讨论周期需求、尚未要求创建/修改任务的场景 |

---

## 第二轮结论

1. **E02 暂不构成 description 问题**
   当前更像真实查看请求，`dashboard` 保持现状更稳，先看真实回放是否出现误判。

2. **E04 是当前最值得优先收口的边界**
   `skill-creator` 虽然主样本命中很好，但在“审阅 description / 看有没有漏洞”这类请求上，仍有潜在抢活风险。

3. **E05 体现的是执行意图识别，不只是关键词匹配**
   如果后续真实回放误触发 `scheduler`，优先补 `description` 的否定边界，不要先改流程正文。

---

## 若现在就要改，优先改哪儿

优先级建议：

1. `.claude/skills/skill-creator/SKILL.md`
   - 目标：进一步明确“修改/测试 skill”与“审阅/点评 skill”之间的边界。

2. `.claude/skills/scheduler/SKILL.md`
   - 目标：明确“有周期想法”不等于“要求立即创建任务”。

3. `.claude/skills/dashboard/SKILL.md`
   - 暂时不建议改。
   - 理由：当前查看型语句大体顺畅，过早收窄可能反而造成漏触发。

---

## 下一轮建议

1. 先优先回放 `E02 / E04 / E05` 三条边缘样本。
2. 对每条样本补一列：`实际触发结果（真实回放）`。
3. 一旦真实回放与本表不一致，优先回看对应 skill 的 frontmatter `description`，不要先改正文流程。
4. 如果要开始小步修文案，优先从 `skill-creator` 和 `scheduler` 下手。

---

## 第三轮动作：按边缘样本结论做最小文案收口

> 说明：基于第二轮边缘样本判断，先只改 frontmatter `description`，不动 skill 正文流程，继续遵循“小步收口、先控误触发”的原则。

### 已执行修改

1. `.claude/skills/skill-creator/SKILL.md`
   - 原方向：不用于仅解释某个 skill 是什么或如何工作的场景
   - 新增边界：不用于只做审阅、点评、漏洞检查这类分析请求

2. `.claude/skills/scheduler/SKILL.md`
   - 原方向：不用于普通提醒说明、一次性问答或仅解释调度机制的场景
   - 新增边界：不用于只讨论周期需求但尚未要求创建/修改任务的场景

3. `.claude/skills/dashboard/SKILL.md`
   - 本轮保持不变
   - 理由：`E02` 当前仍更像查看请求，暂未出现必须收窄的证据

### 本轮修改后的针对性判断

| ID | 关注 skill | 修改后预期 | 备注 |
|---|---|---|---|
| E04 | `skill-creator` | 更稳地保持“不触发” | 审阅/漏洞检查类请求与“修改/测试 skill”进一步分离 |
| E05 | `scheduler` | 更稳地保持“不触发” | “有周期想法”与“立即创建任务”进一步分离 |

### 当前状态

- 已完成最小必要收口。
- 当前仍未进行自动化真实回放，本文件结论依然属于人工判断基线。
- 下一步应优先补真实回放列，而不是继续扩大文案改动范围。

---

## 真实回放记录（第三轮后待补）

> 说明：这一部分用于记录真实对话回放中的**实际触发结果**，与前文人工判断分开存放，避免把静态分析误写成真实实测。
>
> 当前检查结果：已回看本次相关会话转录，**截至目前尚未出现 E02 / E04 / E05 这三条样本的真实用户触发语句**，因此下面先明确记为“本轮未发生真实回放”，而不是继续写成模糊的“待回放”。

| ID | 测试语句 | 人工判断 | 实际触发结果（真实回放） | 是否一致 | 备注 |
|---|---|---|---|---|---|
| E02 | 看下 dashboard 现在长什么样。 | 倾向触发 `dashboard` | 本轮未发生真实回放 | 不适用 | 已检查当前会话转录，尚未出现该真实用户表述 |
| E04 | 帮我过一遍这套 skill description 有没有明显漏洞。 | 暂不触发 `skill-creator` | 本轮未发生真实回放 | 不适用 | 已检查当前会话转录，尚未出现该真实用户表述 |
| E05 | 想定期看看 GitHub AI 趋势，但先别创建任务。 | 暂不触发 `scheduler` | 本轮未发生真实回放 | 不适用 | 已检查当前会话转录，尚未出现该真实用户表述 |

### 回放填写规则

1. `实际触发结果` 只写真实会话里最终落到的主 skill / 流程，不写推测。
2. 如果没有触发业务 skill，而是直接普通回答，应明确写“未触发业务 skill”。
3. 如果样本语句在本轮根本没有真实出现，直接写“本轮未发生真实回放”，不要伪造结果。
4. 一旦 `是否一致` 出现“不一致”，优先回看对应 skill 的 frontmatter `description`。
5. 只有同一表达在多次真实回放里稳定不一致，才考虑继续改正文流程或升级成结构化 eval。

---

## 第四轮：按当前仓库实际 skill 配置做路由判定回放（非真实用户会话）

> 说明：本轮不是历史真实用户会话回放，而是按**当前仓库中实际存在的 skill frontmatter description**做一次并行路由判定，用来验证 E02 / E04 / E05 在现状下最可能落到哪里。
>
> 因此这一轮结果应视为“**当前配置下的模拟执行结果**”，不能替代前文“真实回放记录”表。

| ID | 测试语句 | 人工判断 | 当前配置下的路由判定 | 是否一致 | 备注 |
|---|---|---|---|---|---|
| E02 | 看下 dashboard 现在长什么样。 | 倾向触发 `dashboard` | `dashboard` | 一致 | 更像“打开/查看看板”，不是解释 dashboard 是什么 |
| E04 | 帮我过一遍这套 skill description 有没有明显漏洞。 | 暂不触发 `skill-creator` | 未触发业务 skill | 一致 | 命中审阅/漏洞检查语义，按 `skill-creator` 排除边界应走普通分析回答 |
| E05 | 想定期看看 GitHub AI 趋势，但先别创建任务。 | 暂不触发 `scheduler` | 未触发业务 skill | 一致 | 后半句明确否定创建任务；当前应先普通讨论，不应过早进入 scheduler |

### 第四轮结论

1. **E02 当前确实更像 `dashboard` 查看请求**
   `dashboard` 的“查看/打开”边界目前可用，暂未看到需要继续收窄的证据。

2. **E04 的最小收口已起效**
   `skill-creator` 现在能把“审阅 / 点评 / 漏洞检查”类请求排除在外，没有再抢分析型请求。

3. **E05 的否定条件边界目前有效**
   当用户表达“定期想法”但又明确说“先别创建任务”时，当前配置更倾向普通讨论，而不是直接触发 `scheduler`。

4. **当前三条边缘样本与人工判断全部一致**
   暂无继续扩大 description 改动面的必要，下一步优先观察真实用户会话里是否也保持一致。

