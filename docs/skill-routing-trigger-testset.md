# Skill Routing Trigger Test Set

## 目标

为 mycc 的 skill 路由治理提供一组可复用的 `should-trigger / should-not-trigger` 基线样本，用于：

- 人工回放检查 description 是否收口到位
- 后续转换成 eval / benchmark 输入
- 观察高冲突 skill 的误触发与漏触发

---

## 使用方式

1. 逐条把测试语句作为用户输入回放
2. 记录实际触发的业务 skill / superpowers / PACE skill
3. 对比“期望触发 / 期望不触发”
4. 如有误判，优先回看对应 skill 的 frontmatter `description`

---

## 测试范围

本轮优先覆盖高冲突和高频 skill：

- `dev`
- `dev-team`
- `skill-creator`
- `create-system`
- `dashboard`
- `scheduler`
- `collect`
- `decision`
- `reflect`
- `tell-me`

---

## Should-trigger（应触发）

| ID | 测试语句 | 期望主 skill | 备注 |
|---|---|---|---|
| T01 | 帮我把 `.claude/skills/dashboard/SKILL.md` 的 description 改得更窄一点，别再误触发解释类请求了。 | `skill-creator` | 典型 skill 改造请求 |
| T02 | 这个 Node 服务现在接口 500，测试也全红了，先帮我排查根因再修。 | `dev` | 后续应叠加调试流程 skill |
| T03 | 我想做一个新 skill，专门把调试过程沉淀成 SOP。 | `skill-creator` | 新建 skill |
| T04 | 帮我写一篇公众号，主题是“为什么 description 比 hooks 更该先治理”。 | `create-system` | 明确产出内容 |
| T05 | 先给这篇文章列个结构，我想看三段式提纲。 | `create-system` | 后续应路由到 `outline` |
| T06 | 看看我这个月 Claude Code 花了多少，token 用量也顺便看下。 | `cc-usage` | 真实口语触发 |
| T07 | 给我开一下 cc 能力看板，我想看看现在有哪些 skill。 | `dashboard` | 明确查看看板 |
| T08 | 帮我加一个每天早上 9 点检查 heartbeat-pool 的定时任务。 | `scheduler` | 定时任务管理 |
| T09 | 刚才我们已经决定先做 description 收敛，再做触发测试集，记个决策。 | `decision` | 已形成结论 |
| T10 | 把今天这轮 skill 路由治理的结果发飞书给我。 | `tell-me` | 明确要发通知 |
| T11 | 把最近一周 GitHub AI 项目、Claude 更新和量化交易相关新闻收成一页简报。 | `collect` | 多源采集与汇总 |
| T12 | 这个功能拆成前端改造、hooks 迁移、文档同步三块，让多个 agent 并行推进。 | `dev-team` | 明显可并行开发 |

---

## Should-not-trigger（不应触发）

| ID | 测试语句 | 不应误触发的 skill | 理由 |
|---|---|---|---|
| N01 | `dashboard` 这个 skill 是干嘛的？ | `dashboard` | 这是解释类请求，不是打开看板 |
| N02 | superpowers 的触发词到底怎么判断？ | `skill-creator`, `dashboard` | 这是规则说明，不是改 skill 也不是看板操作 |
| N03 | 怎么写公众号标题更容易点开？ | `create-system`, `title` | 这是方法讨论，不是直接产出标题 |
| N04 | scheduler 的机制是 cron 还是别的？ | `scheduler` | 这是解释机制，不是创建或修改任务 |
| N05 | tell-me 现在到底支持发什么内容？ | `tell-me` | 这是能力说明，不是发送通知 |
| N06 | 我在想要不要把 skill 路由也做成测试框架，你怎么看？ | `dev`, `skill-creator` | 这是方案讨论，不是直接实现或修改 skill |
| N07 | 帮我看看这个决策记录写得清不清楚。 | `decision` | 这是审阅现有内容，不是新增决策 |
| N08 | 最近总感觉路由有点乱，晚点得系统复盘一下。 | `reflect` | 还没出现明确故障或复盘请求，信号太弱 |
| N09 | 先解释一下 `dev-team` 和并行 superpowers 的区别。 | `dev-team` | 这是概念解释，不是并行开发任务 |
| N10 | 我想知道 collect 这个 skill 都会抓哪些来源。 | `collect` | 解释来源，不是发起采集 |
| N11 | 如果以后要做一个新的通知系统，也许可以参考 tell-me。 | `tell-me` | 泛讨论，不是发送结果 |
| N12 | 我准备明天再处理这个 bug，现在先讲讲为什么会误触发。 | `dev` | 这是原因分析，不是立即修 bug |

---

## 边缘样本（建议重点观察）

这些表达最容易出现误判，建议后续真实回放时优先验证：

| ID | 测试语句 | 观察点 |
|---|---|---|
| E01 | 先梳理一下 skill 路由，等会儿再决定要不要改。 | 会不会过早触发 `skill-creator` |
| E02 | 看下 dashboard 现在长什么样。 | 是否稳定触发 `dashboard` 而不是解释类回答 |
| E03 | 这个问题像 bug，但我现在只想知道可能原因。 | 是否误入 `dev` 实现流 |
| E04 | 帮我过一遍这套 skill description 有没有明显漏洞。 | 是否更适合 review/analysis，而不是直接修改 |
| E05 | 想定期看看 GitHub AI 趋势，但先别创建任务。 | 是否误触发 `scheduler` 或 `gh-trending` |

---

## 后续升级方向

1. 把本文件转成结构化 eval 数据（JSON / YAML）
2. 对每条样本增加“期望叠加的 superpowers / PACE skill”字段
3. 对高频误判样本增加真实对话回放记录
4. 按月补充新样本，避免测试集老化
