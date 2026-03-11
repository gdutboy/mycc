# 调研记录

## 摘要索引

<!-- 格式：- [状态] 标题 — 关键结论 #finding [date:: YYYY-MM-DD] [change:: CHG-ID] -->

- [x] Hooks 配置冲突：全局 vs 项目双配置 + Vault 模板干扰 — 全局 hook 拦截 `.pace/findings.md` 误判为 artifact；Stop hook 读取 vault 模板而非 `.pace/` 实际文件；修复：pre-tool-use.js 添加 `/.pace/` 排除 + 删除 vault 模板目录 #finding [date:: 2026-03-11]
- [x] knowledge 注入仅 L0 摘要，详情不可见 — compact 路径已注入 L0（3 条）；L1 详情注入延后到笔记 10+ 再评估 #finding [date:: 2026-03-08] [change:: CHG-20260308-04]
- [x] AI 记录 findings 习惯性跳过详情 — PostToolUse H14 + Stop 终态双层检查 findings [ ] 索引 vs ### 详情 #finding [date:: 2026-03-08] [change:: CHG-20260308-04]
- [x] 指引体系补遗：旧格式应 DENY 而非仅警告 + compact 后格式规则注入 — PreToolUse 旧格式 DENY（emoji/表格）+ compact 路径 FORMAT_SNIPPETS 注入 #finding [date:: 2026-03-08] [change:: CHG-20260308-04]
- [x] PACEflow 指引体系断裂：DENY"只说不教"+模板注入一次性+Skill 链路断裂 — 三层问题：10/11 DENY 无格式示例（webot 8 次无法自愈）+impl_plan 模板注释最弱仅 1 行+格式信息分散 3-4 个 Skill 且调用可靠性仅 30-50%；方案：DENY 内联 FORMAT_SNIPPETS 常量+SessionStart 格式校验+模板注释增强+artifact-management 格式速查整合；~220 行改动 0 新文件 #finding [date:: 2026-03-08] [change:: CHG-20260308-03]
- [x] PACEflow 流程保障漏洞：impl_plan 详情+walkthrough 详情+native plan compact 丢失 — 4 个漏洞：H13 一次性 flag 后静默+H13 仅扫描活跃区+stop.js 零 impl_plan 详情检查+native plan(`~/.claude/plans/`)compact 后丢失且 pre-compact 不快照；根因：详情完整性检查仅靠 PostToolUse 单点一次性提醒，无终态守门 #finding [date:: 2026-03-07] [change:: CHG-20260307-04]
- [x] PACEflow Plugin 化可行性调研 — 技术完全可行：hooks.json 格式兼容+skills 目录结构一致+模板可携带；安装 50 步→1 步；需解决 VAULT_PATH 参数化+CLAUDE.md 注入+无 PostInstall 事件；目标 v5.0.0 #finding [date:: 2026-03-07] [change:: CHG-20260307-03]
- [x] S-4 walkthrough/findings 活跃区无归档机制 — 三层策略：SessionStart 智能截断（walkthrough 3 详情/findings 开放项详情/impl_plan 进行中变更）+ PostToolUse warnOnce + Stop warning 兜底 #finding [date:: 2026-03-09] [change:: CHG-20260309-03]
- [x] S-1 统一 stdin 解析方向 — pace-utils 新增 parseHookStdin/withStdinParsed/parseStdinSync 3 函数，6 个 hook 入口重构完成 #finding [date:: 2026-03-09] [change:: CHG-20260309-05]
- [x] S-3 版本自动化方向 — bump-version.js 创建完成，支持 --dry-run + 6 文件同步 + 格式校验 #finding [date:: 2026-03-09] [change:: CHG-20260309-06]
- [x] PACEflow v4.8.1 设计全面评估 #finding [date:: 2026-03-07] [change::] — 6 维度评分：设计哲学 A/架构健壮性 A-/协议完整性 B+/测试覆盖 B/可维护性 A-/实际效果 A；最大风险 install.js 零测试；核心差距 E 阶段中途纠偏+无回滚机制；25+ CHG 迭代验证核心设计决策正确 #finding [date:: 2026-03-07]
- [x] docs/plans/ 旧计划文件导致 PACE 桥接反复 DENY — 新增 hasUnsyncedPlanFiles/listUnsyncedPlanFiles 区分已同步文件，formatBridgeHint 集中化桥接消息 #finding [date:: 2026-03-06] [change:: CHG-20260307-01]
- [x] Claude Code plan mode 桥接缺口 — 部分问题：无 compact 时 native plan 在上下文中可自然桥接；compact 后计划丢失且 PACEflow 无恢复机制，需 SessionStart/pre-compact 补覆盖 #finding [date:: 2026-03-06] [change:: CHG-20260307-04]
- [x] ticket13 全面审查+验证：5-agent 审计 vs 5-agent 验证 — 26 项发现中 7 误报(27%)+12 有意设计(46%)+7 确认(27%)；6 Critical 中 4 个推翻；确认项全为文档/代码风格（0 运行时 bug）；审计误报根因：模式匹配非路径追踪+缺设计意图+未实际 diff+严重度膨胀 #finding [date:: 2026-03-06] [change:: CHG-20260306-01]
- [x] Hook stdin.cwd + CLAUDE_PROJECT_DIR 环境变量发现 — stdin JSON 包含 cwd 字段（所有事件）；CLAUDE_PROJECT_DIR 为项目根（不随 cd 漂移）；resolveProjectCwd 向上搜索 .pace/ 是多余 workaround #finding [date:: 2026-03-05] [change:: CHG-20260305-01]
- [x] Superpowers-PACEflow 集成断层 — 三层拦截链（SessionStart 提醒+TodoWrite DENY+Code DENY）+ pace-bridge skill 桥接 #finding [date:: 2026-03-04] [change:: CHG-20260304-04]
- [x] getProjectName CWD 漂移导致 vault 幽灵项目 — resolveProjectCwd() 向上搜索 .pace/ 定位项目根，7 hook 统一替换 #finding [date:: 2026-03-04] [change:: CHG-20260304-03]
- [x] Obsidian CLI 调研：PACEflow 集成机会分析 — 最佳集成点在 AI 交互层（MCP server），非 Hook 层；obsidian-cli-rest 插件提供 MCP 原生支持；hooks 必须保持 fs 操作（CLI 100-500ms vs fs <5ms） #finding [date:: 2026-03-02] [change:: CHG-20260302-01]
- [x] Agent Teams 生产实测：PACEflow hooks 交互分析 — Stop 不对 teammate 触发（官方"main agent only"）；TaskCompleted 触发条件是共享任务非 PACE task.md（语义错位）；`CLAUDE_CODE_TEAM_NAME` 环境变量可检测 teammate 身份；方向 C 混合策略推荐（信息 hook 保留+阻止 hook 降级+同步 hook 静默） #finding [date:: 2026-02-26] [change:: CHG-20260226-02]
- [-] claude-mem 实测评估 — 已移除：搜索命中率 0/5、project 碎片化、只捕获工具调用不捕获决策、28MB 数据库无可用知识 #finding [date:: 2026-02-25]
- [x] Claude Code 2.1.42→2.1.55 变更影响分析 — v2.1.47 修复 Windows hooks+last_assistant_message；v2.1.49 ConfigChange hook；v2.1.50 SIMPLE 禁用 hooks；v2.1.53-55 Windows 稳定性修复（无 hooks 变更） #finding [date:: 2026-02-25] [change:: CHG-20260225-05]
- [-] vault-sync 知识自动流转方案验证 — 已否定：findings 导出不自包含+thought 无法确定性触发，全部回滚 #finding [date:: 2026-02-24] [change:: CHG-20260224-03]
- [x] 记忆系统方案对比（claude-mem/lite/自建） — claude-mem 已否定；CC 2.1.59 内置 auto-memory 覆盖基础需求；Obsidian knowledge/+thoughts/ 覆盖跨项目知识沉淀；自建不再需要 #finding [date:: 2026-02-19]
- [x] PACEflow 信息捕获能力自评 — 项目内终态~85% 已验证；否定决策短板由 H8 [-] 理由检测缓解；跨项目由 Vault 迁移+knowledge/ 解决；思考演进由 thoughts/ 覆盖 #finding [date:: 2026-02-19]
- [x] 跨项目 Findings 统一管理方案调研 — 核心问题是"跨项目待办可见性"；4 种方案对比 + 3 社区参考 #finding [date:: 2026-02-19]
- [x] 跨会话 Checkpoint 机制调研 — SessionStart 已覆盖 artifact 注入；低成本改进：注入 git branch+commit #finding [date:: 2026-02-18]
- [-] 外部计划源通用化架构 — 保持现状：当前只有 1 个上游工具，过早抽象不值得 #finding [date:: 2026-02-17]
- [x] HelloAGENTS 对比分析：安装部署体验 — 4 项改进方向中 install.js 已实现（--dry-run/--force/备份/settings 自动更新）；工作流无可借鉴（基于 issue 模板非 hooks）；剩余 UX 差距（npm 全局安装/plugin 打包）待 CC plugin 生态成熟后再评估 #finding [date:: 2026-02-16]
- [-] OpenSpec 对比分析 — 保持现状：Artifact 结构差异大（变更文件夹 vs 根文件+双区），无紧迫需求 #finding [date:: 2026-02-16]
- [x] PACEflow 与 Subagent/Agent Teams 兼容性 — 全部 hooks 生效；todowrite-sync 对团队任务存在误报 #finding [date:: 2026-02-16]
- [x] TodoWrite 工具名变更 — 三种工具名共存：TodoWrite/TaskCreate/TaskUpdate；matcher 必须覆盖全部 #finding [date:: 2026-02-14] [change:: CHG-20260214-04]
- [x] PACE-TodoWrite 同步方案调研 — PreToolUse:TodoWrite 实测通过；PostToolUse:TodoWrite 全平台不触发；四层 A+B+C+D 方案完成 #finding [date:: 2026-02-14] [change:: CHG-20260214-04]
- [x] TodoWrite/Tasks 存储机制与 Hook 交互可行性 — Hook 无法直接操作内存中的 TodoWrite 状态；PostCompact hook 不存在 #finding [date:: 2026-02-14]
- [x] PACE+Superpowers 空项目集成社区调研 — 三项目验证多信号激活+hooks-skills 协调；isPaceProject() 四信号方案通过 7/7 #finding [date:: 2026-02-14] [change:: CHG-20260214-01]
- [x] Stop 防无限循环验证 — BLOCK(1/3)→(2/3)→(3/3)→降级 exit 0，计数器正常 #finding [date:: 2026-02-13]
- [x] E2E 测试全流程验证 — SessionStart+PreToolUse+PostToolUse+Stop 全部正常 #finding [date:: 2026-02-13]
- [x] v3→v4 致命错误修正 — stderr+exit 0 被完全忽略；v4 改用 JSON stdout additionalContext + exit 2 阻止 #finding [date:: 2026-02-13] [change:: CHG-20260213-01]
- [x] PreToolUse additionalContext 验证 — hookSpecificOutput.additionalContext 成功注入 AI 上下文 #finding [date:: 2026-02-13] [change:: CHG-20260213-01]
- [x] Hook command 路径格式 — settings.json 必须用 `node C:/Users/...`（Windows 原生路径） #finding [date:: 2026-02-13]
- [x] Claude Code 工作流强制执行研究 — CLAUDE.md 遵守问题是已知缺陷；hooks+skills+plugins 组合最佳 #finding [date:: 2026-02-13]
- [x] Hooks 官方文档深度调研 — stdin/stdout/stderr 协议、exit code、blocking 机制、14 种 hook 事件完整文档 #finding [date:: 2026-02-13]
- [x] Hooks 配置生效 — settings.json 修改后需重启 Claude Code 才能生效 #finding [date:: 2026-02-12] [change:: CHG-01] ✅ 2026-02-25
- [x] grep -qF 标记检测 — grep 因 `--` 失败，改用 `grep -qF 'ARCHIVE'` #finding [date:: 2026-02-11] [change:: CHG-01]
- [x] Hook 路径格式 — Git Bash 不认 K:/ 盘符，需用 /k/ 格式 #finding [date:: 2026-02-11] [change:: CHG-01]

**状态说明**: `[x]` 已采纳/已验证 | `[-]` 保持现状/已否定 | `[ ]` 参考中/待评估

## 未解决问题


## Corrections 记录

<!-- 已归档到详细记录 -->

## 详细记录

### [2026-03-11] Correction: 新 hook 事件语义未实测确认就实施
- **错误行为**：v4.6.0 批次 3（CHG-20260225-06）基于文档描述推断 TaskCompleted = PACE 任务完成、TeammateIdle = teammate 质量门控，直接编写代码。implementation_plan 中虽标注"⚠️ stdin 格式需实测确认"，但跳过实测直接交付
- **正确做法**：新 hook 事件必须先用最小脚本实测触发条件和 stdin 字段，确认语义匹配后再编写业务逻辑。文档描述的"任务完成"可能指完全不同的任务系统
- **触发场景**：利用新发现的 hook 事件扩展功能时，急于覆盖更多事件而跳过验证
- **后果**：两个 hook 从创建至今从未按设计意图工作——task-completed.js 检查 PACE artifact 但由 Agent Teams 事件触发（语义错位），teammate-idle.js 在 teammate 已完成工作时注入无意义的约束提醒
- **根本原因**：对 hook 事件名称的直觉理解（"TaskCompleted = 任务完成"）替代了严格验证
- [knowledge:: ai-verification-discipline]

### [2026-03-11] Correction: thinking 发现异常但未验证就跳过
- **错误行为**：验证脚本输出缺少预期的详情行，thinking 中已识别"嵌套结构可能不匹配"，但用"verify.js 已经 5/5 通过"自我说服，直接向用户报告"全部绿灯"
- **正确做法**：thinking 中发现任何异常必须立即验证，不能用其他间接证据合理化跳过。如果 verify.js 也有同样的 bug，就是假阳性
- **触发场景**：验证/测试结果与预期不完全一致时，用"另一个检查通过了所以没问题"来回避深究
- **根本原因**：倾向于给用户呈现"干净的结果"，而不是诚实暴露不确定性
- [knowledge:: ai-verification-discipline]

### [2026-03-11] Correction: 任务完成后未主动归档
- **错误行为**：标记 T-117 为 [x] 后，询问用户"需要归档 task.md 吗？"
- **正确做法**：G-9 明确要求回复"任务完成"前必须确认 task.md 已归档。归档是必须步骤，不需要询问
- **触发场景**：任务标 [x] 后准备结束时，容易忘记归档直接汇报完成
- [knowledge:: project-only]

### [2026-03-11] Correction: 记录 findings 时只写索引不写详情
- **错误行为**：记录新 finding 时只在摘要索引区添加一行条目，跳过在"## 未解决问题"区写详情段落。被用户追问后才补写。本次 CHG-20260308-03 审视发现的两个缺口（旧格式 DENY + compact 格式注入）就是这样——先只写了索引，用户说"不记录详情吗"才补充
- **正确做法**：每条新 finding 必须同时写入索引条目和详情段落。详情应包含：背景（发现过程）、问题描述（当前行为 vs 应有行为）、代码定位、修复方案。findings 跨多个 session 存活，只有索引时后续 session 无法还原发现时的上下文
- **触发场景**：任务收尾阶段记录 findings 时，倾向于"快速记一笔就完事"，把详情当作可选项
- **根本原因**：把 findings 索引当成 TODO 备忘而非知识记录。索引是给搜索用的，详情是给未来 session 还原上下文用的——两者用途不同，缺一不可
- [knowledge:: ai-verification-discipline]

### [2026-03-09] S-1 统一 stdin 解析方向

### [2026-03-09] S-1 统一 stdin 解析方向

**背景**：经过 25+ 个 CHG 迭代（2026-02-11 至 2026-03-07），对 PACEflow 从设计角度进行全面评估。3 个 subagent 并行分析（hook 架构 + PACE 协议 + 测试覆盖）。

**六维度评分**：

| 维度 | 评分 | 说明 |
|------|------|------|
| 设计哲学 | **A** | "确定性 hooks + 建议性 CLAUDE.md"分层清晰，避免了纯 LLM 指令的不可靠性 || 架构健壮性 | **A-** | pace-utils 公共模块 + 顶层 try-catch + 降级放行，单点故障风险低 || 协议完整性 | **B+** | P-A-C-E-V 五阶段覆盖完整，但 E 阶段缺乏中途纠偏机制 || 测试覆盖 | **B** | 单元 36 + E2E 48 + verify 6 覆盖 hooks/utils，但 install.js 零测试 || 可维护性 | **A-** | 常量集中 + 版本单一源 + 双模板同步，代码风格一致 || 实际效果 | **A** | 15 轮审查（ticket1-15）验证核心逻辑健壮，确认问题集中在文档/风格层 |

**核心优势**：
1. **确定性保障层**：hooks 提供 100% 阻止能力（deny/exit 2），不依赖 AI 自律2. **多信号激活**：`isPaceProject()` 五级判定避免误激活/漏激活3. **优雅降级**：teammate 场景 deny→hint，异常时 exit 0 静默放行4. **Vault 统一存储**：`getArtifactDir()` 唯一路径解析器，消除 artifact 分裂

**关键差距**：1. **install.js 零测试覆盖**（最大风险）：安装脚本处理 settings.json 合并、文件备份、模板清理，任何 bug 直接影响生产环境，但无自动化测试2. **E 阶段中途纠偏缺失**：执行阶段发现方案有误时，无标准化的"暂停→修正→恢复"流程，依赖 AI 自行判断3. **无回滚机制**：artifact 归档后无法撤销，依赖 git 版本控制4. **verify.js 覆盖有限**：健康检查 6 组仅覆盖静态一致性，不覆盖运行时行为

**设计决策验证（经 25+ CHG 迭代确认正确）**：- `countByStatus().done = [x]+[-]` vs `stop.js xCount = [x]` — 有意区分，不是 bug- Hook I/O 协议 `exit 0 + stderr = 忽略` — 多次踩坑后成为硬性约束- `.pace/` 运行时状态 vs Vault artifact 存储 — 关注点分离- `CLAUDE_PROJECT_DIR` 替代 `.pace/` 向上搜索 — 根因修复 vs workaround**

**建议优先级**：
- **P0**：install.js 测试（至少 settings.json 合并 + 文件备份的关键路径）- **P1**：E 阶段纠偏协议（`[!]` 阻塞状态 → 方案修正 → 恢复执行）- **P2**：Plugin 化打包（消除手动 install.js 部署，走 CC 原生分发）
### [2026-03-08] knowledge 注入仅 L0 摘要，详情不可见

**背景**：CHG-20260308-03 完成后讨论 Correction 双写到 knowledge/ 的效果时，审视 knowledge 注入机制发现：知识笔记写得再详细，AI 实际只能自动看到 summary 一句话。

**当前注入机制**（`pace-utils.js:scanRelatedNotes` + `session-start.js:L272-284`）：

```
SessionStart (非 compact)
  → scanRelatedNotes(projectName)
  → 扫描 thoughts/ + knowledge/ 两个目录
  → 匹配 frontmatter projects 字段包含当前项目
  → 过滤 status: archived
  → 输出最多 5 条 L0 摘要：
    [status] title — "summary"
```

**三层内容只注入了一层**：

| 层级 | 内容 | 自动注入？ | AI 实际看到？ |
|------|------|----------|------------|
| L0 标题+摘要 | `[status] title — "summary"` | ✅ SessionStart | ✅ 每次启动 |
| L1 详情 | `## 摘要` 段落、模式分析、规则表 | ❌ | ❌ 需主动 Read（~30-50%） |
| L2 全文 | 完整笔记含代码示例 | ❌ | ❌ 需主动 Read |

**具体影响**——以 `ai-verification-discipline` 为例：
- summary 只说"新 API 先实测、发现异常立即追查、记录 findings 必须同时写详情"
- 3 个具体模式（API 语义假设、间接证据合理化、记录偷懒跳详情）的**触发场景和正确做法完全不可见**
- 通用规则表（4 行对照表）不可见
- AI 看到"记录 findings 必须同时写详情"一句话，但不知道"详情至少包含什么"——又是"只说不教"

**与 Skill 调用可靠性是同一类问题**：
- Skill：DENY 消息引用 `paceflow:artifact-management skill`，但 AI 调用 Skill 概率 30-50%
- Knowledge：SessionStart 注入 `[concluded] ai-verification-discipline — "..."` 一句话，但 AI 主动 Read 概率 30-50%

**compact 时更严重**：
- `eventType !== 'compact'` 守卫导致 compact 恢复路径**完全不注入** knowledge
- auto compact 2-3 次/change 是常态，每次 compact 后 knowledge 上下文归零

**可能的改进方向**（待讨论）：
1. **compact 路径也注入 L0 摘要**（最小改动，~3 行，移除 `eventType !== 'compact'` 守卫）
2. **L1 关键规则注入**：scanRelatedNotes 返回 `## 摘要` 段落内容（不只是 frontmatter summary），SessionStart 注入前 N 行
3. **触发式注入**：PostToolUse 检测到特定操作（如写 findings.md）时，自动注入相关 knowledge 笔记的关键规则
4. **Correction 特殊通道**：knowledge 笔记中标记为 Correction 的模式，在 SessionStart 以更高优先级注入（因为 Correction 是验证过的错误模式，复发概率高）

**改动量估算**：方向 1 最小（~3 行）；方向 2 中等（~20 行，需解析 `## 摘要` 段落）；方向 3/4 较大（~40-50 行，需 PostToolUse 新增检测逻辑）。

### [2026-03-08] AI 记录 findings 习惯性跳过详情

**背景**：CHG-20260308-03 完成后记录两个遗漏缺口到 findings.md，只写了索引行，被用户追问"不记录详情吗"后才补写。回顾历史，这不是第一次——多个 session 中出现过类似行为。

**问题本质**：AI 把 findings 索引当 TODO 备忘（"记一笔下次做"），而非知识记录。索引和详情的用途完全不同：

| 组成部分 | 用途 | 受众 |
|---------|------|------|
| 索引条目 | 搜索入口、状态追踪 | SessionStart 自动注入给当前 session |
| 详情段落 | 上下文还原、方案记录 | 未来 session 的 AI 通过 Read 获取 |

**findings 跨 session 生命周期**：一条 finding 通常跨 10+ session 存活（从发现到修复）。如果只有索引，后续 session 的 AI 看到"旧格式应 DENY"一句话，但不知道：
- 怎么发现的（触发事件）
- 当前行为具体是什么（代码位置、执行路径）
- 应有行为是什么（对比）
- 修复方案是什么（代码改动、行数估算）

**已有缓解**：记录为 Correction（findings.md Corrections 区）+ 同步到 `knowledge/ai-verification-discipline.md` 模式 3。但 knowledge 注入本身也只有 L0 摘要（见上一条 finding），Correction 的详细规则在 AI 写 findings 时不一定可见。

**根因链**：
```
AI 记录 findings → 偷懒只写索引
→ 原因：没有外部强制（PostToolUse 不检查 findings 是否有对应详情段落）
→ 原因：knowledge 中的 Correction 规则在写 findings 时不可见（仅 L0 注入）
→ 原因：knowledge 注入机制太轻量（见上一条 finding）
```

**可能的改进方向**：
1. **PostToolUse 检测**：Edit findings.md 且 `new_string` 含新索引条目（`- [ ]`）时，检查"## 未解决问题"区是否有对应的 `###` 详情段落 → HINT 提醒（类似 H13 impl_plan 详情检查）
2. **Stop 检查**：findings.md 有 `[ ]` 索引但无对应详情段落 → 加入 warnings（~10 行）
3. **SessionStart 提醒**：检测 findings.md 活跃区有 `[ ]` 条目无详情段落 → 注入提醒

**改动量估算**：方向 1 最实用（~15 行，复用 H13 模式），方向 2 兜底（~10 行）。

### [2026-03-08] 指引体系补遗：旧格式应 DENY + compact 后格式规则注入

**背景**：CHG-20260308-03 完成后审视发现两个遗漏缺口。指引体系增强解决了"DENY 只说不教"，但还有两个场景未覆盖——旧格式能写入（仅警告不阻止）和 compact 后格式上下文丢失。

**缺口 A：旧格式应 DENY 而非仅警告**

**当前行为**：
```
SessionStart → 检测 impl_plan 有表格/emoji 格式 → 输出格式合规警告（不阻塞）
→ AI Edit impl_plan 用表格/emoji 格式 → PreToolUse 放行（不检查内容格式）
→ 旧格式持续存在 → 下次 SessionStart 再警告 → 循环
```

**应有行为**：
```
AI Edit impl_plan → PreToolUse 检测 new_string 含表格行或 emoji 状态标记
→ DENY + 给出正确 checkbox 格式（FORMAT_SNIPPETS.implIndex + formatRule）
→ AI 被拒 1-2 次后改用正确格式 → 问题根除
```

**实现方案**：`pre-tool-use.js` 新增格式检查分支（~15 行）
```javascript
// 在 impl_plan 详情守门之后、native plan 桥接之前
if (toolName === 'Edit' && paceSignal && fileName === 'implementation_plan.md' && newString) {
  // 检测表格格式（行首 | ... | 且无 checkbox 索引）
  if (/^\|.+\|$/m.test(newString) && !/^- \[.\]/m.test(newString)) {
    reason = `impl_plan 使用了表格格式，hook 无法识别。${FORMAT_SNIPPETS.formatRule}\n正确格式：${FORMAT_SNIPPETS.implIndex}`;
    // DENY
  }
  // 检测 emoji 状态标记
  if (/[✅❌📋🔄⏳]/.test(newString)) {
    reason = `impl_plan 使用了 emoji 状态标记，hook 无法识别。${FORMAT_SNIPPETS.formatRule}\n正确格式：${FORMAT_SNIPPETS.implIndex}`;
    // DENY
  }
}
```

**关键决策**：限定 `fileName === 'implementation_plan.md'` 时才检查 → 零误报风险（不影响代码文件中的表格或 emoji）。

**缺口 B：compact 后格式规则注入**

**问题**：auto compact 是常态（2-3 次/change），每次 compact 后 AI 失去所有格式上下文。当前 compact 恢复路径只注入活跃区内容和快照状态，不注入格式规则。AI 的训练默认可能选择表格/emoji，下次 Edit 就写成旧格式。

**当前 compact 恢复输出**：
```
=== Compact 恢复（快照 ...）===
进行中任务:
  - [/] T-001 ...
待办任务: 2 个
```

**应追加的格式规则摘要**（~5 行）：
```javascript
// session-start.js compact 路径，快照输出之后
if (paceSignal) {
  lines.push('');
  lines.push('=== 格式提醒 ===');
  lines.push(FORMAT_SNIPPETS.formatRule);
  lines.push(`task.md 格式：${FORMAT_SNIPPETS.taskEntry}`);
  lines.push(`impl_plan 索引格式：${FORMAT_SNIPPETS.implIndex}`);
}
```

**为什么 startup 路径不需要**：startup 注入完整活跃区内容（包含现有正确格式的 artifact），AI 从内容中学习格式。compact 路径仅注入快照摘要（任务数/状态），无格式信息，需要补充。

**改动量估算**：缺口 A ~15 行 + 缺口 B ~5 行 = ~20 行，0 新文件。

### [2026-03-08] PACEflow 指引体系断裂：DENY"只说不教"+模板注入一次性+Skill 链路断裂

**背景**：webot 项目在 30 分钟内被 pre-tool-use.js E 阶段 DENY 连续拦截 8 次，AI 始终无法自愈。根因不仅是 impl_plan 格式不兼容（旧表格+emoji vs checkbox），更深层的问题是 PACEflow 的指引体系存在系统性断裂——hook 拦截能力很强但"只拦不教"。

**触发事件**：2026-03-08 02:07-02:34，生产 hook 日志记录 11 次 DENY：webot 8 次（E 阶段格式不兼容）+ paceflow-hooks 3 次（空窗期+synced-plans 漏记）。

**三层断裂详析**：

#### 断裂 1：DENY 消息"只说不教"（10/11 无格式示例）

**证据来源**：`pre-tool-use.js` 全部 10 个 DENY 分支源码分析

| DENY 场景 | 当前消息问题 | 行号 |
|-----------|------------|------|
| 强信号（无活跃任务） | 说"执行 P-A-C 流程"但不给 task.md 任务格式 | L232-236 |
| C 阶段未批准 | 说"添加 APPROVED"但不说放在哪 | L285 |
| E 阶段无 [/] | 说"改为 [/]"但不说 hook 检测的正则格式 | L293-303 |
| impl_plan 详情守门 | 说"添加详情段落"但不给段落模板 | L142-165, L167-191 |
| Write 覆盖保护 | 说"用 Edit"但不给 Edit 参数格式 | L87-102 |
| Native plan 桥接 | 说"桥接到 artifacts"但不引用 pace-bridge skill | L194-203 |

**11 个 DENY 中仅 1 个（Superpowers 桥接）引用了 Skill**（pace-bridge），其余 10 个完全没有 DENY→Skill 的引导链。

**webot 8 次 DENY 的具体根因链**：
```
E 阶段 DENY → "无 [/] 变更索引" → AI 看 impl_plan 是表格格式
→ DENY 消息没说 hook 检测的是 /^- \[\/\]/m 正则
→ AI 修改表格中的"状态"文字 → hook 正则不匹配 → 再次 DENY → 循环 8 次
```

#### 断裂 2：模板注入一次性 + 格式注释质量不均

**证据来源**：`pre-tool-use.js` T-206 逻辑（L104-119）、`session-start.js` 注入逻辑（L118-137）、5 个模板文件

**AI 看到格式规范的机会**：

| 时机 | 次数 | 条件 |
|------|------|------|
| SessionStart | 0 | 仅注入活跃区内容，无格式规范 |
| 首次 Write 新建 | 0-1 | T-206 注入模板，但 `createTemplates` 可能已抢先创建文件 |
| Edit 已有文件 | 0 | 无任何格式提示 |
| compact 后恢复 | 0 | 仅恢复快照，无格式信息 |

**模板注释质量评估**：

| 模板 | 注释质量 | 关键缺失 |
|------|---------|---------|
| findings.md | 高 | 无明显缺失 |
| spec.md | 高 | 占位符自解释 |
| walkthrough.md | 中 | 详情格式示例藏在归档区注释 |
| task.md | 低 | 无任务条目示例、无 T-NNN 格式、无 APPROVED 位置说明 |
| implementation_plan.md | **最低** | 仅 1 行 HTML 注释；无详情段落格式；无禁止项 |

**webot 旧格式产生原因**：项目创建时 impl_plan 模板注释不足 → AI 自由发挥选择表格+emoji → SessionStart 每次注入旧格式 → AI 学习并延续旧风格 → 无任何机制发现和纠正。

**附加发现**：webot 的 impl_plan 有**两个 `<!-- ARCHIVE -->` 标记**（第 221 行和第 448 行），导致 `readActive` 截断大量活跃内容。

#### 断裂 3：Skill 格式信息分散 + 调用链路断裂

**证据来源**：6 个 Skill SKILL.md 的 description 和内容分析

**task.md 完整格式分散在 3-4 个 Skill 中**：

| 格式信息 | 所在 Skill |
|---------|-----------|
| 状态标记、T-NNN、双区结构 | artifact-management |
| CHG 分组格式、联动规则 | change-management |
| APPROVED/VERIFIED 标记位置 | pace-workflow |
| 焦点变更头部、桥接完整格式 | pace-bridge |

AI 在被 DENY 后需要读 3-4 个 Skill 才能拼凑完整格式——在修复模式下几乎不可能发生。

**Skill 调用可靠性量化**：

| Skill | 被 DENY 引用 | 估计调用率 |
|-------|------------|-----------|
| pace-bridge | 是（1 处） | 60-70% |
| pace-workflow | 否 | 50-70% |
| artifact-management | 否 | 40-60% |
| change-management | 否 | 30-50% |

**推荐方案（增强版方案 C）**：

#### P0：DENY/Stop/HINT 消息内联格式示例

- `pace-utils.js` 新增 `FORMAT_SNIPPETS` 硬编码常量（~10 行）
- `pre-tool-use.js` 增强 10 个 DENY 消息，每个包含可直接复制的格式片段（~50 行）
- `stop.js` 增强 14 个 warning + stderr 改编号列表 + 降级递进式消息（~50 行）
- `post-tool-use.js` 增强 13 个 HINT 消息（~30 行）

**关键设计决策**：
- 格式示例用硬编码常量（确定性最高、零 I/O、格式极少变更）
- 不创建新规则文件（模板+Skill 已是权威来源）
- E 阶段 DENY 消息明确提示：`hook 检测格式为行首 "- [/] "（Markdown checkbox），非表格格式无法识别`
- Stop stderr 从分号拼接改为 `[1]...\n[2]...` 编号列表
- 降级递进：第 2 次加修复 hint，第 3 次加降级警告

#### P1：模板和 SessionStart 格式校验

- `implementation_plan.md` 和 `task.md` 模板活跃区补充格式注释 + 禁止项（~20 行）
- `session-start.js` 新增格式合规检查模块：旧表格+emoji 检测、双 ARCHIVE 检测（~30 行）

#### P2：Skill 格式速查整合

- `artifact-management/SKILL.md` 新增"格式速查"section，集中展示 task.md 和 impl_plan 的完整格式（~30 行）
- DENY 消息末尾追加 `详见 paceflow:xxx skill`

**总改动量**：~220 行修改，0 新文件。

**三层指引体系优化后的定位**：

| 层级 | 载体 | 确定性 | 定位 |
|------|------|--------|------|
| L1 确定性强制 | Hook DENY/exit 2 | 100% | 门控拦截 |
| L2 上下文引导 | DENY 消息内联格式 + SessionStart 校验 | 80-90% | **即时可操作的修复指引**（本次核心增强） |
| L3 参考规范 | Skill 文件 + 模板注释 | 30-50% | 详细参考手册 |

### [2026-03-07] PACEflow 流程保障漏洞：impl_plan 详情+walkthrough 详情+native plan compact 丢失

**背景**：v5.0.0 Plugin 化迁移（CHG-20260307-03）完成后，切换到 plugin 模式时发现 impl_plan 和 walkthrough 均缺少当次变更的详情段落。进一步排查发现这并非偶发遗漏，而是 hook 系统的结构性缺陷。同时回溯发现之前标记为"非问题"的 native plan compact 丢失问题，在实际场景中确认为真实风险。

**4 个漏洞详析**：

#### 漏洞 1：H13 一次性 flag 后静默

**代码位置**：`post-tool-use.js:136-152`

```javascript
// H13: impl_plan 详情缺失检测
if (planActive && !fs.existsSync(path.join(PACE_RUNTIME, 'impl-detail-reminded'))) {
    // ... 扫描 planActive 中 [x] 条目，检查 planFull 中是否有 ### CHG-... 详情
    warnOnce('impl-detail-reminded', ...);  // 写入 flag 文件 → 本会话不再触发
}
```

**问题**：`warnOnce()` 写入 `.pace/impl-detail-reminded` flag 后，整个会话内所有后续 H13 检查被跳过。如果 AI 当时未能补写详情（例如在执行其他任务），后续再也不会收到提醒。

**影响**：一个 CHG 完成后如果首次提醒被忽略/遗漏，整个会话内详情缺失不再被检测到。

#### 漏洞 2：H13 仅扫描活跃区索引

**代码位置**：`post-tool-use.js:137`

```javascript
const doneIndexH13 = planActive.match(/^- \[x\] ((?:CHG|HOTFIX)-\d{8}-\d{2})/gm) || [];
```

**问题**：`planActive` 仅包含 `<!-- ARCHIVE -->` 上方的内容。当 CHG 完成并归档（索引和详情都移到 ARCHIVE 下方）后，H13 永远无法发现这些 CHG 缺少详情。

**致命路径**：
```
CHG 标 [x] → H13 首次触发提醒（但被 flag 吃掉/AI 忽略）
→ 归档索引到 ARCHIVE 下方 → H13 从此不可见
→ 详情永久缺失，无处可查
```

**实际触发**：CHG-20260307-02 和 CHG-20260307-03 均在完成标 `[x]` 后快速归档，H13 要么未触发要么首次提醒被忽略，导致两个 CHG 的详情缺失直到用户手动发现。

#### 漏洞 3：Stop hook 零 impl_plan 详情检查

**代码位置**：`stop.js:83-87`

```javascript
// 3. 检查 implementation_plan.md 状态一致性
const planActive = readActive(cwd, 'implementation_plan.md');
if (planActive && pendingCount === 0 && doneCount > 0 && /^- \[\/\]/m.test(planActive)) {
  warnings.push(`implementation_plan.md 仍有 [/] 进行中，但任务已全部完成`);
}
```

**问题**：Stop hook 对 impl_plan 仅检查 `[/]` 状态一致性，**完全不检查详情是否存在**。Stop 是会话结束的终极守门人（exit 2 阻止），但它不守 impl_plan 详情这道门。

**对比**：Stop 对 walkthrough 有日期检查（lines 89-115），对 task.md 有归档检查（lines 78-81），唯独 impl_plan 详情无检查。

#### 漏洞 4：Native plan compact 后丢失

**触发链**：
```
用户 EnterPlanMode → Claude 写计划到 ~/.claude/plans/random-name.md
→ plan mode 提示"compact 后再执行"（官方建议）
→ 用户 compact/auto-compact → 计划内容从 AI 上下文丢失
→ session-start.js 注入 artifact 活跃区 → task.md 无任务
→ pre-tool-use.js deny 写代码 → AI 不知道要做什么
→ 计划永久丢失（~/.claude/plans/ 无元数据，文件名随机）
```

**PACEflow 监控盲区**：
| 检查点 | native plan 覆盖？ | 说明 |
|--------|-------------------|------|
| `hasPlanFiles()` | ❌ | 仅检查 `docs/plans/`（Superpowers 计划） |
| `pre-compact.js` | ❌ | 快照 task.md + impl_plan 状态，不快照计划内容 |
| `session-start.js` | ❌ | 注入 5 个 artifact + thoughts，不注入 `~/.claude/plans/` |
| `pre-tool-use.js` | ❌ | 检查 `docs/plans/` 存在性，不检查 `~/.claude/plans/` |

**之前误判**：findings.md 第 10 行标记 `[-] Claude Code plan mode 桥接缺口 — 非问题`，理由是"native plan 内容已在 AI 上下文中"。**这在无 compact 时成立，但 compact 后失效**——compact 清空上下文，plan 内容不在 artifact 中，无法恢复。

**根因分析**：

问题的本质是 **详情完整性检查仅靠 PostToolUse 单点一次性提醒，无终态守门**：

| 保障层 | task.md 归档 | walkthrough 日期 | impl_plan 详情 | native plan |
|--------|-------------|-----------------|---------------|-------------|
| PostToolUse（实时） | H3 归档提醒 | ❌ | H13 一次性 | ❌ |
| Stop（终态） | ✅ 归档检查 | ✅ 日期检查 | ❌ 零检查 | ❌ |
| Pre-compact（快照） | ✅ 状态快照 | ❌ | `hasInProgress` 仅 | ❌ |
| SessionStart（恢复） | ✅ 注入 | ✅ 注入 | ✅ 注入 | ❌ |

**修复方向（初步）**：

1. **Stop 增加 impl_plan 详情检查**（漏洞 1+2+3 的终极修复）：检查 `planFull`（全文含归档区），已完成 CHG 无 `### CHG-...` 详情 → exit 2 阻止
2. **H13 改为每次触发**（漏洞 1）：移除一次性 flag，或改为 per-CHG flag（`impl-detail-{CHG-ID}`）
3. **H13 扫描 `planFull`**（漏洞 2）：索引匹配改用 `readFull` 而非 `readActive`
4. **Native plan 检测**（漏洞 4）：SessionStart 检测 `~/.claude/plans/` 中最近文件 + compact 后注入提醒；或 pre-compact 快照计划内容

### [2026-03-07] PACEflow Plugin 化可行性调研

**背景**：PACEflow v4.8.1 经 25+ CHG 迭代已稳定，当前部署依赖 install.js 手动安装（复制 hooks+skills+合并 settings.json）。调研 Claude Code Plugin 系统是否能简化部署和更新。3 个 subagent 并行调研（架构文档+已安装插件分析+社区资源搜索）。

**核心结论**：技术完全可行，所有组件均有 1:1 映射。

**Plugin 系统关键机制**：
- `.claude-plugin/plugin.json`：仅 `name` 必填，其余可选
- `hooks/hooks.json`：格式与 settings.json 完全一致，自动注册
- `skills/<name>/SKILL.md`：自动发现，命名空间为 `/paceflow:skill-name`
- `${CLAUDE_PLUGIN_ROOT}`：hook 脚本中引用插件内文件的环境变量
- 安装：`claude plugin install paceflow@marketplace-name`
- 更新：bump version + `plugin update` 自动同步
- 缓存：`~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`

**组件映射**：

| 组件 | 当前 | Plugin | 难度 |
|------|------|--------|------|
| 8 Hook 脚本 | settings.json 手动 | hooks.json 自动 | 低 |
| 6 Skills | `~/.claude/skills/` | `skills/name/SKILL.md` | 低 |
| 5 模板 | hooks/templates + skills/templates 双份 | 统一 templates/ | 低（消除同步） |
| pace-utils.js | `require('./pace-utils')` | `require(__dirname + '/pace-utils')` | 低 |
| install.js | 手动运行 | **不再需要** | 消除 |
| verify.js | 手动运行 | **不再需要** | 消除 |

**参考插件分析**：
- superpowers（最佳参考）：hooks.json + 12 skills + agents + commands + shared lib
- obsidian-skills：5 skills + references 子目录
- claude-plugins-official：Monorepo 30+ 插件 + marketplace.json

**需解决的 3 个关键问题**：
1. **VAULT_PATH 参数化**：硬编码用户路径 → `PACE_VAULT_PATH` 环境变量
2. **CLAUDE.md 规则注入**：Plugin 无法自动注入 CLAUDE.md，需 SessionStart hook 或 README 指引
3. **无 PostInstall 事件**（[#11240](https://github.com/anthropics/claude-code/issues/11240)）：初始化依赖 SessionStart 懒创建（当前已有此机制）

**分发方式**：GitHub Marketplace — 推送到 `paceaitian/paceflow` 仓库，用户一条命令安装。

**收益**：
- 安装 50 步 → 1 步
- 更新 install.js --force → plugin update
- 模板双份 → 单份
- 消除 install.js/verify.js 维护成本

**风险**：
- Plugin 生态 Public Beta，缓存失效偶有问题（[#14061](https://github.com/anthropics/claude-code/issues/14061)）
- 开发期间需用 `--plugin-dir` 绕过缓存
- 已有 9000+ 插件，核心 API 稳定

### [2026-03-06] docs/plans/ 旧计划文件导致 PACE 桥接反复 DENY

**背景**：实施 CHG-20260306-02（paceflow-audit skill）时，通过 Claude Code 原生 `EnterPlanMode` 完成规划。实施阶段 Edit 代码文件被 pre-tool-use.js DENY："检测到 PACE 项目但 task.md 中无活跃任务。检测到 docs/plans/ 中有计划文件，请将计划中的任务同步到 task.md 后再写代码。"

**问题**：`hasPlanFiles(cwd)` (pace-utils.js:84-90) 只检查 `docs/plans/` 中是否有 `YYYY-MM-DD-*.md` 文件，**不区分已同步和未同步**。

触发死循环路径：
```
旧 plan 文件残留（如 2026-03-04-superpowers-paceflow-fusion.md，已桥接同步）
→ hasPlanFiles() = true
→ task.md 无活跃任务 → pre-tool-use.js:171-175 DENY + 消息"请将计划同步到 task.md"
→ AI 遵循指令尝试重新同步已归档的计划
→ 同步完成 → 归档 → task.md 再次为空 → 继续 DENY
```

同时 session-start.js:129-141 每次启动都输出 `=== Superpowers 桥接提醒 ===`（噪音但不阻塞）。

**影响范围**：
- pre-tool-use.js DENY 消息误导 AI 重新同步旧计划（阻塞）
- session-start.js 桥接提醒每次启动触发（上下文噪音）
- AI 可能重复执行已完成的桥接操作

**代码定位**：
| 位置 | 行号 | 功能 |
|------|------|------|
| pace-utils.js `hasPlanFiles()` | 84-90 | 文件名格式匹配，不区分新旧 |
| pace-utils.js `listPlanFiles()` | 97-106 | 列出文件，不区分同步状态 |
| pre-tool-use.js DENY 分支 | 155-168 | `paceSignal === 'superpowers'` 时拼接桥接指引 |
| pre-tool-use.js DENY 分支 | 171-175 | 其他信号时追加"请同步计划"提示 |
| session-start.js 桥接提醒 | 129-141 | 启动时输出提醒 |

**待修复**：方案研究中

### [2026-03-06] Claude Code plan mode 桥接缺口（结论更新：部分问题）

Claude Code 原生 `EnterPlanMode` 将计划写入 `~/.claude/plans/`（随机文件名，无元数据），不在 hook 检测范围。

**原结论（2026-03-06，已推翻）**：认为"非问题"——native plan 内容在 AI 上下文中，DENY 后 AI 天然可桥接。CHG-20260306-02 实施中验证通过。

**更新结论（2026-03-07）**：**compact 场景推翻原结论**。Plan mode 官方提示"compact 后再执行"，compact 清空上下文后 plan 内容丢失。PACEflow 4 个检查点（SessionStart/PreToolUse/PreCompact/Stop）均不覆盖 `~/.claude/plans/`。实际触发：v5.0.0 plugin 迁移过程中，plan 写入后 compact 导致计划丢失，用户手动回忆才发现。

**结论**：无 compact 时原分析成立（AI 上下文自然桥接）；compact 后为真实漏洞。详见上方"PACEflow 流程保障漏洞"条目的漏洞 4。

- ✅ Compaction 后 TodoWrite 残留：已通过 A+B+C+D 四层方案缓解（v4.3.6，CHG-20260214-04）。A: SessionStart 三态注入 / B: CLAUDE.md 优先级 / C: PostToolUse 提醒 / D: PreToolUse 拦截校验。待重启后 E2E 验证。
- ✅ PreToolUse:TodoWrite matcher Windows 实测通过（2026-02-14）：additionalContext 注入成功 + 日志记录完整 + exit 0 未阻止执行。方案 D 可行。
- 🔒 PostToolUse:TodoWrite matcher 全平台不触发（#20144 Open），非 Windows 特有 bug。已知限制，无法修复。PreToolUse:TodoWrite 已验证可用，D 方案改用 PreToolUse 替代。
- 🔒 Agent Teams 多 teammate 并发修改 `.pace/` 状态文件（stop-block-count/degraded）存在竞态条件风险。Agent Teams 仍为实验性功能，单 teammate 测试未触发竞态，多 teammate 场景为理论风险。
- 🔒 todowrite-sync.js 无法区分团队任务（TaskCreate/TaskUpdate for Agent Teams）与 PACE 任务操作，会产生不相关的 HINT 误报。影响极低（仅 additionalContext 提醒，不阻止操作）。
- 🔒 Agent Teams 生产实测（2026-02-26，entry-research + pipeline-research 两轮）+ 深度调研（4 subagent）发现：
  - **stop.js 不对 teammate 触发**：官方文档明确 Stop 仅 "main Claude Code agent"。本次日志中的 TW_CLEANUP 是 lead 自己的 Stop 事件。TeammateIdle 是 teammate 的 Stop 等价物。
  - **task-completed.js 语义错位**：触发条件是 Agent Teams 共享任务完成（TaskUpdate 或 teammate 带 in-progress 共享任务空闲时），检查的却是 PACE task.md/walkthrough/findings。本次 0 触发因 teammate 无 in-progress 共享任务。
  - **todowrite-sync.js 7 次假阳性**：teammate TaskCreate 创建团队任务（`~/.claude/tasks/`）→ hook 检测到 `isPaceProject && isWriteOp && totalActive===0` → HINT "task.md 无活跃任务"。设计正确但无法区分 PACE vs 团队任务。
  - **teammate-idle.js 输出格式**：用 `process.stdout.write(plainText)` 而非 JSON `hookSpecificOutput`。TeammateIdle 事件的 stdout 处理规范未明确。
  - **`CLAUDE_CODE_TEAM_NAME` 环境变量**：teammate 进程自动设置此 env var（值为 team name），主会话不设置。可用于 hook 中检测 teammate 身份（`process.env.CLAUDE_CODE_TEAM_NAME`）。GitHub #16126/#24505 请求 stdin 暴露 agent identity，均 Open/stale。
  - **In-process vs Pane-based 行为不同**（#24175）：Windows 默认 in-process — TeammateIdle/TaskCompleted 在 parent 触发，SessionStart 不触发；macOS/Linux pane-based — 反过来。无文档说明。
- ❓ PACEflow hooks 作用域设计——推荐方向 C（混合策略）+ 清理无效 hook：
  - **待移除**：`teammate-idle.js`（teammate 已完成工作，注入无意义）+ `task-completed.js`（触发条件是 Agent Teams 共享任务，非 PACE task.md；3 个检查中 2 个被 stop.js 覆盖，1 个 findings ⚠️ 从未使用）
  - **检测方法**：`process.env.CLAUDE_CODE_TEAM_NAME` 存在即为 teammate
  - **阻止 hook 降级**（stop.js、pre-tool-use.js）：teammate 时降级为 additionalContext 提醒，不 exit 2 / deny
  - **同步 hook 静默**（todowrite-sync.js）：teammate 时直接 return，避免假阳性
  - **无需改动**（session-start.js、post-tool-use.js、config-guard.js、pre-compact.js）：teammate 时自然无害或有用
  - **待决策**：方向 C 的降级+静默改动取决于 Agent Teams 使用频率；两个 hook 移除可优先执行

### [2026-03-06] ticket13 全面审查+验证：审计 vs 验证差异分析

**背景**：对 PACEflow 全部 8 个 hook + 5 个 skill + 模板执行 5-agent 并行审查（代码/流程/执行性/架构/简化），产出 26 项发现（6C+15H+15W+10I）。随后 5-agent 并行验证每项发现。

**验证结果**：

| 判定 | 数量 | 占比 |
|------|------|------|
| ❌ 误报 | 7 | 27% |
| ⚠️ 部分正确（有意设计/低影响） | 12 | 46% |
| ✅ 确认（真实问题） | 7 | 27% |

**确认的 7 项（全为文档/代码风格，0 运行时 bug）**：
1. C-5：pace-workflow.md description 遗漏 Verify
2. C-6：change-management.md PACE 集成表缺 V 阶段
3. H-5：pace-workflow.md 3 处版本号 v4.8.0→v4.8.1
4. H-11：Mermaid label `superpowers plan` 应为 `superpowers`
5. R-1：7 个 hook 14 处 createLogger/resolveProjectCwd fallback 死代码
6. R-3：4 个 hook stdin 异步解析重复代码
7. D-2：pace-utils.js 3 处 `!VAULT_PATH` 判断永远 false

**推翻的 Critical（4/6）**：C-1 两层保护互补非失效、C-2 H9 有 newString 守卫、C-4 existsSync 正确处理空文件、原 C-3 极低影响

**审计误报根因**：
1. **模式匹配非路径追踪**：看到变量名不一致就报 bug，未沿控制流验证是否可达
2. **缺设计意图上下文**：compact 必须重注入、flag 不写入是持续监控、优先级不同是语义区分
3. **未实际 diff**：H-9/H-10 声称模板不一致，实际逐行对比完全一致
4. **严重度膨胀**：Critical 确认率 33%、High 确认率 20%

**结论**：审计→验证两步流程是必要的。单步审计误报率 50-80%，需验证 agent 追踪执行路径筛选真实信号。PACEflow 核心 hook 逻辑经多轮迭代已健壮，确认问题集中在文档同步和代码 DRY。

### [2026-02-19] PACEflow 信息捕获能力自评

**背景**：评估 PACEflow artifact 系统在知识积累方面的真实表现，为后续记忆系统设计提供基线。

**捕获率量化评估**：

| 信息类型 | 捕获率 | 说明 |
|---------|--------|------|
| 做了什么（任务/变更） | ~95% | task.md + walkthrough.md 强制记录 |
| 决策结论 | ~80% | findings.md 摘要好，但"为什么不做"弱 |
| 踩坑经验 | ~70% | 大坑记住，小坑随会话消失 |
| 否定结论（为什么不做 X） | ~40% | "待评估"状态导致重复调研 |
| 跨项目经验迁移 | ~20% | 仅 MEMORY.md 200 行上限 |
| 思考演进轨迹 | ~5% | artifact 只存终态 |

**核心发现**：PACEflow 在"项目内终态信息"的捕获上已经很强（~85%），解决了"不丢东西"。短板集中在三个方向：
1. **否定决策的理由** — walkthrough.md "不处理项"通常一句话带过，3 个月后不够还原决策上下文
2. **跨项目经验迁移** — 项目级 artifacts 无法跨项目，MEMORY.md 容量不足
3. **思考演进轨迹** — 从"调研 X" → "否定 X" → "转向 Y" 的推理链条完全丢失

**结论**："不丢东西"已解决，"越用越聪明"未解决。后者需要上下文匹配+主动注入机制。

### [2026-03-04] getProjectName CWD 漂移导致 vault 幽灵项目

**背景**：ticket12 代码审查修复后，stop hook 持续报"10 个未完成任务"。经排查发现 vault 中存在 `projects/paceflow`（旧）和 `projects/paceflow-hooks`（正确）两个目录，hook 读到了错误的那个。

**问题**：`getProjectName(cwd)` 只取 CWD 最后一级目录名，不感知项目边界：
- `K:\AI\Paceflow-hooks` → `paceflow-hooks` ✅
- `K:\AI\Paceflow-hooks\paceflow`（git 仓库根）→ `paceflow` ❌

当 CWD 漂移到子目录时，会在 vault 创建幽灵项目，artifact 写入分裂。

**触发条件**：
1. git 仓库在项目子目录（本项目 `paceflow/` 即如此）
2. bash `cd` 到子目录后触发 hook
3. Claude Code 内部 CWD 继承 bash shell 状态

**修复**：
- CHG-20260304-03：`resolveProjectCwd()` 向上搜索 `.pace/` 定位项目根（临时方案）
- CHG-20260305-01：改用 `CLAUDE_PROJECT_DIR` 环境变量（根因修复），消除 `.pace/` 搜索的边界问题

**临时处置**：已删除 vault 中旧的 `projects/paceflow/` 目录 + `paceflow/.pace/` 污染目录。

### [2026-03-05] Hook stdin.cwd + CLAUDE_PROJECT_DIR 环境变量发现

**背景**：调查 CWD 漂移问题时，用户提问"为什么不能从 stdin 获取项目的目录"。

**关键发现**：
1. **stdin JSON 包含 `cwd` 字段**：所有 hook 事件的 stdin 都有 `cwd`，等价于 `process.cwd()`（会随 cd 漂移）
2. **`CLAUDE_PROJECT_DIR` 环境变量**：hook 子进程自动设置，值为项目根目录（**不随 cd 漂移**，正斜杠格式）
3. **Bash 子进程不继承**：`$CLAUDE_PROJECT_DIR` 仅 hook 进程可用，Bash 工具的子进程中为空

**stdin 完整字段列表**（PreToolUse 实测）：
`cwd, hook_event_name, permission_mode, session_id, tool_input, tool_name, tool_use_id, transcript_path`

**三者对比**：

| 来源 | 语义 | 随 cd 漂移 | 格式 |
|------|------|-----------|------|
| `process.cwd()` | OS 工作目录 | 是 | 反斜杠 |
| `stdin.cwd` | hook 调用时工作目录 | 是 | 反斜杠 |
| `CLAUDE_PROJECT_DIR` | 项目根目录 | **否** | 正斜杠 |

**结论**：CHG-20260304-03 的 `resolveProjectCwd()` 向上搜索 `.pace/` 是多余 workaround，`CLAUDE_PROJECT_DIR` 天然解决 CWD 漂移。改为 `path.resolve(process.env.CLAUDE_PROJECT_DIR)` 即可（1 行 vs 5 行循环），且无边界问题（父目录有 `.pace/` 不影响）。

### [2026-03-04] Superpowers-PACEflow 集成断层

**背景**：执行 CWD 漂移修复计划时，使用 Superpowers `writing-plans` skill 生成计划 → `subagent-driven-development` skill 执行。首个 subagent 被 PACEflow hooks 阻塞，无法写任何文件。

**问题本质**：Superpowers 的 plan→execute 流程跳过了 PACE A 阶段（Artifact 准备），直接进入 E 阶段（Execute）。两套系统各自完整但缺少桥接。

**三个断点**：

1. **计划不在 implementation_plan.md 中**
   - Superpowers `writing-plans` 输出到 `docs/plans/YYYY-MM-DD-*.md`
   - PACEflow 的变更追踪在 `implementation_plan.md` 变更索引中（CHG-ID 格式）
   - 结果：计划存在但 PACEflow 不知道有活跃变更

2. **TodoWrite 任务未同步到 task.md**
   - Superpowers `subagent-driven-development` 用 TodoWrite 创建任务追踪
   - PACEflow 的 PreToolUse hook 检查 `task.md` 活跃区是否有 `[ ]`/`[/]` 任务
   - 结果：TodoWrite 有任务但 task.md 为空 → hook 判定"无活跃任务"

3. **Subagent 被 hook deny 阻塞**
   - PreToolUse hook 发现无活跃任务 → deny 所有 Write/Edit 操作
   - Subagent 无法创建/修改任何文件 → 卡死
   - 无错误提示给 lead agent（deny 反馈给 subagent 本身，lead 不可见）

**影响范围**：
- 所有使用 Superpowers 计划+执行的场景（subagent-driven 和 executing-plans）
- Agent Teams 场景同理（teammate 也会被 hook 阻塞）

**临时解决方式**（本次手动执行）：
1. 在 `implementation_plan.md` 添加 CHG 条目（`[/]` 进行中）
2. 在 `task.md` 添加对应 T-NNN 任务 + `<!-- APPROVED -->` 标记
3. 然后才能启动 subagent 执行

**可能的桥接方案**（待讨论）：

| 方案 | 描述 | 优点 | 缺点 |
|------|------|------|------|
| A. 手动桥接 | 执行前手动补 CHG + task | 零改动 | 每次都要手动 |
| B. Skill 桥接 | 新建 `pace-bridge` skill，在 Superpowers plan 完成后自动创建 PACE artifacts | 半自动 | 需 AI 判断调用时机 |
| C. Hook 桥接 | PreToolUse 检测 `docs/plans/` 存在时自动降级为 HINT 而非 deny | 全自动 | 削弱 PACE 保护 |
| D. Superpowers 适配 | 修改 writing-plans/subagent-driven skill 内嵌 PACE A 阶段步骤 | 一体化 | Superpowers 是外部插件，不可修改 |

**根本矛盾**：PACEflow 的设计假设是"AI 在写代码前必须经过人工审批（APPROVED）"，而 Superpowers 的设计假设是"计划审批后可以自主执行"。两者在"执行自主权"上有设计冲突。


### [2026-03-02] Obsidian CLI 调研：PACEflow 集成机会分析

**背景**：Obsidian 1.12.4（2026-02-27）正式发布内置 CLI（100+ 命令），评估对 PACEflow 工作流的优化机会。

**CLI 基本信息**：
- 内置于 Obsidian 桌面版，非独立 npm 包/二进制
- **需要 Obsidian 桌面版运行中**（通过 IPC 通信）
- Windows 需 `Obsidian.com` 终端重定向器（1.12.4 安装器自带）
- 核心能力：文件 CRUD、全文搜索、Tasks 操作、Property 管理、`eval` 执行任意 JS（可访问 Dataview API）
- 输出格式：json/csv/tsv/md/text/yaml

**社区 MCP 方案**：
- `obsidian-cli-rest`（2026-02-23 发布）：将 CLI 命令转为 REST API + MCP server（仅 2 工具：search + execute）
- `obsidian-mcp-tools`：语义搜索，但维护者缺失

**六维分析结论**：

| 维度 | 结论 |
|------|------|
| fs 替代 | 不适合 Hook 层（CLI 100-500ms vs fs <5ms），可用于 AI 交互层 |
| 搜索能力 | CLI `search` 显著优于当前 `scanRelatedNotes` frontmatter 解析 |
| 插件操作 | `eval` 可调用 Dataview/Tasks API，但依赖内部 API 稳定性 |
| OneDrive 同步 | CLI 不解决；但 CLI 写入可触发 Obsidian 索引即时更新 |
| Hook 性能 | 不可接受，hooks 必须保持 fs 直接操作 |
| MCP server | `obsidian-cli-rest` 是最佳选项（覆盖全、仅 2 工具不占 context） |

**优化建议（按优先级）**：
1. 配置 `obsidian-cli-rest` 为 Claude Code MCP Server（Impact: HIGH, Effort: LOW）
2. `pace-knowledge` Skill 增加 CLI 命令指引（Impact: MEDIUM, Effort: LOW）
3. Hooks 保持 fs 直接操作不变（架构决策）
4. post-tool-use 写入后异步触发索引刷新（Impact: MEDIUM, Effort: LOW-MEDIUM）
5. session-start 增加 CLI fallback 搜索（Impact: MEDIUM, Effort: MEDIUM）
6. Dataview 查询集成（Impact: MEDIUM, Effort: MEDIUM，稳定性待验证）

**核心结论**：最佳集成点在 **AI 交互层**（MCP server + Skill 指引），而非 **Hook 执行层**。建议 1 可立即实施。

## 已解决问题

- ✅ PACEflow 与 Subagent 兼容性（2026-02-16）：PreToolUse deny 对 subagent 写代码文件生效（实测阻止成功）；TodoWrite hint 对 subagent TaskCreate 生效（additionalContext 注入成功）。GitHub #21460 声称 hooks 不对 subagent 生效，与实测矛盾（可能已修复或仅影响 plugin 级 hooks）。
- ✅ PACEflow 与 Agent Teams 兼容性（2026-02-16）：teammate 是独立 Claude Code 进程，加载相同 settings.json hooks。实测 5/5 hooks 全部生效：SessionStart INJECT、PreToolUse DENY、todowrite-sync HINT、Stop TW_CLEANUP。teammate 写代码文件被成功阻止。

- ✅ PreToolUse + PostToolUse 同时配置是否冲突（GitHub #12445）→ 2026-02-12 验证：无冲突，两者并行运行正常
- ✅ SessionStart hook 同步执行是否导致 Windows 终端冻结 → 2026-02-12 验证：无冻结，Node.js 脚本执行快速

## 错误日志

| 时间 | 错误类型 | 错误描述 | 尝试次数 | 解决方案 | 状态 |
|------|----------|----------|----------|----------|------|
| 2026-02-12 | Path Error | `/bin/bash: K:/AI/...` No such file | 1 | 路径改为 `/c/Users/...` 格式 | ✅ 已解决 |
| 2026-02-13 | Hook Startup Error | settings.json 用 `/c/Users/...` 路径注册 hook，重启报 2 个 startup hook error | 2 | 改为 `C:/Users/...` Windows 原生路径 | ✅ 已解决 |

---

### [2026-02-19] 记忆系统方案对比（claude-mem / claude-mem-lite / 自建）

**背景**：评估现有记忆工具和自建方案，确定最佳知识积累路径。

**工具对比**：

| 维度 | claude-mem (v10.0.4) | claude-mem-lite | 自建方案 |
|------|---------------------|-----------------|---------|
| 架构 | Bun+Python+ChromaDB 守护进程 | Node.js 3 依赖，按需启动 | 按需求定制 |
| LLM 调用 | ~50/session, 每次工具 1 call | ~5-8/session, episode batching | 离线批处理或按需 |
| 搜索 | ChromaDB 向量 | SQLite FTS5+BM25 | FTS5 或 Grep |
| Windows | ✅ 支持 | ❌ POSIX only | ✅ 可控 |
| 安全 | 端口 37777 无认证 (#990) | 无守护进程 | 可控 |
| 许可 | AGPL-3.0 + $CMEM token | MIT | N/A |
| 观察质量 | 低（套话、粒度细） | 未验证 | 取决于提取逻辑 |

**claude-mem 实际评估**：
- 核心价值成立（跨会话持久化+语义搜索），但信噪比低
- 叙事质量差（模板化套话），概念混淆（如 Google 2014 Knowledge Vault 论文）
- 已优化 SKIP_TOOLS（17 工具排除，~60% 噪音削减），降低为安全网定位

**关键决策**：
- ❌ 全量记录无必要 — JSONL 转录已是全量，问题是"怎么查"不是"存不存"
- ❌ claude-mem-lite 暂不可用 — Windows 硬阻断（POSIX shell + Unix 文件锁）
- ✅ 真正需求是**知识积累**而非防遗漏 — 需要在正确时刻自动推送正确经验
- ❌ global-findings.md + AI 判断方案被否决 — AI 判断"是否跨项目通用"~70% 准确率，违反 PACEflow "不信任 AI 判断"的设计哲学
- ✅ 采用 Knowledge Vault 风格：AI 只做搬运工（inbox），人工做质量控制

**方案演进**（决策路径）：
1. 初始方案：global-findings.md 单文件 + AI 判断写入 → 发现 AI 判断不可靠
2. 修正方案：Knowledge Vault inbox 模式 — AI 全量写入 inbox，人工审核分类
3. 关键原则：**写入门槛低（100%进inbox）、质量控制靠人（Obsidian 审核）、检索靠确定性逻辑（标签+关键词匹配）**

**三种路线评估**：
- **A. Obsidian 知识库 + SessionStart 匹配**（推荐）— 零依赖、人机共用、增量式
- **B. JSONL 离线提取 → SQLite**（备选）— 复用已有数据、零实时开销
- **C. 自建完整 MCP server**（过度）— 开发量大，当前量级不需要数据库

**三个短板的补救方案**：

| 短板 | 方案 | 成本 | 预期效果 |
|------|------|------|---------|
| 否定决策理由 (~40%) | post-tool-use.js HINT：状态→保持现状时提醒补理由 | ~10 行 hook | → ~75% |
| 跨项目迁移 (~20%) | Obsidian inbox + 人工审核 + SessionStart 匹配注入 | ~20 行 hook + Obsidian 结构 | → ~70% |
| 思考演进 (~5%) | 决策路径写作约定（重要决策关闭时记录推理链） | 0 代码 | → ~40% |

**待整合方向**：本条目与以下 findings 条目有关联，可能整合为统一方案——
- 跨项目 Findings 统一管理方案调研（同一天）
- 跨会话 Checkpoint 机制调研（2026-02-18）
- HelloAGENTS 对比分析：安装部署体验（2026-02-16）

---

### [2026-02-19] 跨项目 Findings 统一管理方案调研

**痛点**：需要打开各项目的 Claude Code 才能看到 findings.md 待处理项，没有统一入口知道"哪个项目有什么东西要处理"。

**已有工具现状**：
- 项目 `findings.md`：结构化（日期/状态/关联变更），但只在项目内可见
- auto memory `MEMORY.md`：跨会话但非结构化，全量加载到 prompt
- claude-mem MCP：全局跨项目语义搜索，但非结构化状态字段
- CLAUDE.md G-3 `global-findings.md`：约定存在但未实施

**4 种自建方案对比**：

| 方案 | 入口 | 复杂度 | 跨项目复用 | hooks 兼容 |
|------|------|--------|-----------|-----------|
| A. 终端扫描脚本 | `node scan-findings.js` | 低 | ❌ 只读聚合 | 无改动 |
| B. Claude Code Skill `/findings-dashboard` | 任意项目中调用 | 低 | ❌ 只读聚合 | 无改动 |
| C-1. Obsidian 只读聚合 | Obsidian Bases Dashboard | 中 | ❌ 手动复制 | 无改动 |
| C-2. Obsidian 中央库（每条 finding 独立笔记 + frontmatter） | Obsidian Bases Dashboard | 高 | ✅ tag 自动 | 需生成脚本 |
| D. 全局 SessionStart 注入 | 自动（每次启动） | 中 | ❌ 只读 | 需维护项目列表 |

**3 个社区参考方案**：

1. **Knowledge Vault** (naushadzaman/gist) — Obsidian + Claude Code 四支柱体系
   - 核心思路：Obsidian 作为统一知识中心，Claude Code 作为处理引擎
   - `03-resources/` 每条知识独立笔记 + frontmatter tags（`status/to-evaluate`, `status/adopted`）
   - Dataview 查询聚合所有待处理项
   - **可借鉴**：frontmatter tag 状态管理 + Dataview Dashboard 模式

2. **claude-mem** (已安装) — 跨项目语义搜索
   - 自动捕获所有 tool 执行 → AI 压缩 → SQLite+FTS5 索引
   - 3 层渐进式披露（search → timeline → get_observations），~75% token 节省
   - **已有能力**：跨项目搜索 findings 关键词，但缺少结构化状态字段（待评估/已采纳等）
   - **可增强方向**：save_memory 时带 `project` 标签 + 在 title 中编码状态

3. **PILOT** (Kiro agent) — 验证后才记录的学习系统
   - `~/.pilot/learnings/` 按日期独立文件，只保存经过验证的解决方案
   - 语义搜索（Kiro knowledge base）自动匹配历史方案
   - **可借鉴**：学习验证门槛（unverified = guesses, verified = knowledge）

**核心判断**：

问题本质是"跨项目待办可见性"，不是"知识复用"。当前只有 1 个活跃 PACE 项目，跨项目复用是假设需求。

最小可行方案：
- **短期**：方案 A（扫描脚本），10 分钟可实现，扫描所有已知项目目录的 findings.md，提取"待评估"行
- **中期**：方案 C-1（Obsidian 只读聚合），脚本定期同步到 Obsidian Vault，Bases/Dataview 可视化
- **长期**（第二个 PACE 项目出现时再评估）：方案 C-2（Obsidian 中央库）或增强 claude-mem 的结构化能力

**PACEflow 约束**：
- hooks（post-tool-use.js / session-start.js）依赖项目内 `findings.md`，不能移走
- 任何方案都需保持项目 findings.md 作为权威来源，Obsidian/脚本只做聚合

**参考资源**：
- Knowledge Vault: https://gist.github.com/naushadzaman/164e85ec3557dc70392249e548b423e9
- claude-mem: https://corti.com/claude-mem-persistent-memory-for-ai-coding-assistants/
- PILOT (Kiro): https://dev.to/aws-builders/building-persistent-memory-for-kiro-with-bash-hooks-4gm8
- cass_memory_system: https://github.com/Dicklesworthstone/cass_memory_system

**[补充调研] Knowledge Vault 深度研究 + Obsidian Bases 能力分析**：

**社区生态（2025Q4-2026Q1 爆发）**：
- "Claude Code + Obsidian Second Brain" 已形成明确社区生态
- 关键推动者：Peter Yang（Personal OS 概念）/ Eleanor Konik（15M words vault 实战）/ Alex Finn（Claude Code = AI agent）
- Reddit 多个高热度帖子（r/ClaudeAI + r/ObsidianMD），Medium 多篇深度文章

**Eleanor Konik 关键实践（可借鉴）**：
- "不求更快，求更省注意力" — AI 价值在后台自动化而非速度
- **纠正即写入** — 每次纠错都更新 CLAUDE.md/skill（可强化到 PostToolUse hook）
- vault 放上层目录让多项目共享 skills
- Git commit after every change 做安全网

**Obsidian Bases 跨项目聚合能力**：
- ✅ 默认 vault-wide 查询（无需指定 source）
- ✅ `file.inFolder()` / `file.hasTag()` 过滤
- ❌ **不支持跨 Vault 查询**（Obsidian 架构根本限制）
- ❌ **只读 frontmatter properties，不读 note body**（PACEflow 的 `- [x] T-001` 无法被 Bases 查询）
- 性能极快（基于缓存索引），优于 Dataview（运行时扫描）

**PACEflow 核心冲突**：PACEflow 任务状态在 markdown body 而非 frontmatter，Bases 无法直接查询。折中方案：维护平行的 frontmatter 摘要文件，或用 Dataview（可查询 body）替代 Bases。

**修订后的方案建议**：
- **立即可做**：落实 G-3 global-findings.md 双写（零改造）+ 扫描脚本（10 分钟）
- **中期**：Obsidian symlink vault + Dataview Dashboard（避开 Bases 的 frontmatter 限制）
- **长期**：PACEflow artifact frontmatter 层改造（需 PACE P 阶段规划）

### [2026-02-25] Claude Code 2.1.42→2.1.52 变更影响分析（更新）

**背景**：原调研覆盖 2.1.42→2.1.47（2026-02-19），本次扩展到 2.1.52 并验证未落实的行动项。

**版本跨度**：v2.1.47 (2/18) → v2.1.49 (2/19) → v2.1.50 (2/20) → v2.1.51 (2/24) → v2.1.52 (2/24)。v2.1.48 不存在。

**🔴 高影响（7 项）**：

1. **Windows hooks 静默失败修复** (2.1.47)：PreToolUse/PostToolUse 在 Windows 上改用 Git Bash 执行，修复 cmd.exe 导致的静默失败 (#25981)。**隐性验证通过**——PACEflow hooks 一直正常工作。
2. **`last_assistant_message` 字段** (2.1.47)：Stop/SubagentStop stdin 正式加入该字段。可用于检查 AI 最终回复是否真的执行了归档/验证。**未利用**。
3. **SessionStart 延迟执行** (2.1.47)：hook 执行被 defer，启动加速 ~500ms。artifact 注入仍在 AI 首次回复前完成。**隐性验证通过**。
4. **并行文件操作 deny 独立化** (2.1.47)：deny 单个文件不再中断其他并行文件操作。**隐性验证通过**。
5. **新增 ConfigChange hook 事件** (2.1.49)：settings 变更时触发，支持 `decision: "block"` 阻止。可检测用户绕过 PACE 保护。**未利用**。
6. **`disableAllHooks` 安全修复** (2.1.49)：非 managed settings 无法再禁用 managed hooks (#26637)。企业部署安全性提升。
7. **SIMPLE 模式禁用 hooks** (2.1.50)：`CLAUDE_CODE_SIMPLE` 完全禁用 hooks/MCP/CLAUDE.md。团队成员用 SIMPLE 模式时 PACEflow 失效。

**🟡 中影响（6 项）**：

8. **Plan mode compaction 修复** (2.1.47)：compaction 后不再丢失 plan mode 状态 (#26061)。
9. **Bash 权限分类器修复** (2.1.47)：防止 hallucinated descriptions 授予权限。enforce-bash-permissions.ps1 可能可以简化。**未评估**。
10. **新增 WorktreeCreate/WorktreeRemove hook** (2.1.50)：PACEflow 不使用 worktree，暂不需要。
11. **大量内存泄漏修复** (2.1.49-2.1.50)：tree-sitter/Yoga WASM/Agent Teams/LSP/CircularBuffer 等，长会话稳定性提升。
12. **Tool results 持久化阈值降低** (2.1.51)：100K → 50K characters。PACEflow additionalContext 远小于此。
13. **Windows Registry managed settings** (2.1.51)：企业部署 PACEflow 的新选项。

**未验证项状态更新**：

| 项目 | 旧状态 | 新状态 |
|------|--------|--------|
| `last_assistant_message` | P2 未执行 | **✅ v2.1.47 已确认稳定**，待利用 |
| TeammateIdle hook | P3 未执行 | **✅ 官方文档完整记录**，待评估 |
| TaskCompleted hook | P3 未执行 | **✅ 官方文档完整记录**，待评估 |
| Bash 权限分类器 | P1 未执行 | **✅ v2.1.47 已修复**，待评估 enforce-bash-permissions.ps1 |

**补充 v2.1.53-55（2026-02-25 同日发布）**：

纯 Windows 稳定性修复，**无 hooks API/行为变更**：
- v2.1.53：修复 Windows panic ("corrupted value")、多进程 spawn crash、ARM64 2 分钟 crash、WASM crash。**但引入 BashTool EINVAL 回归**。
- v2.1.54：跳过（不存在）。
- v2.1.55：**热修复** BashTool EINVAL (#28333)，v2.1.53 发布后 3 小时紧急发布。

**PACEflow 影响**：hooks 代码无需修改。多进程 spawn crash 修复意味着并行 hook 执行更可靠。Windows 用户必须用 v2.1.55，不要停在 v2.1.53。

**完整建议行动优先级（2.1.42→2.1.55）**：

- **P0**：利用 `last_assistant_message` 增强 stop.js（检查 AI 回复是否真的执行了归档）
- **P1**：评估 ConfigChange hook 防止用户绕过 PACE
- **P1**：评估 enforce-bash-permissions.ps1 是否可简化/移除
- **P2**：TaskCompleted hook 接入（阻止不合格的任务完成）
- **P3**：TeammateIdle hook 接入（Agent Teams 精细控制）
- **文档**：部署说明注明 SIMPLE 模式限制

### [2026-02-18] 跨会话 Checkpoint 机制调研

**背景**：用户分享"显式状态提交"文章，探索 `/progress-save` `/progress-load` 机制与 PACEflow 的集成可能性。

**调研范围**：
1. PopKit (jrc1883/popkit-claude, 4 stars) — session-capture / session-resume / context-restore
2. ClaudePoint (andycufari/ClaudePoint, 232 stars) — 文件系统快照 + MCP server
3. Golev 文章 "Claude Saves Tokens, Forgets Everything" — Compaction 问题全景
4. Reddit/GitHub 社区讨论 — 跨会话上下文处理方案

**PopKit Session Capture/Resume 方案**：
- **STATUS.json** 结构化存储：git state（branch/commit/uncommitted）+ tasks（inProgress/completed/blocked）+ services（devServer/database）+ context（focusArea/blocker/nextAction/keyDecisions）+ projectData（test/build/lint）
- **三级恢复策略**：Continuation(<30min, 快速恢复) / Resume(30min-4h, 简要刷新) / Fresh Start(>4h, 完整验证)
- **自动触发**：Stop hook 调用 Python 脚本 `auto-save-state.py`
- **Skill 指导**：session-capture(保存) + session-resume(恢复) + context-restore(深度恢复)

**ClaudePoint 方案**：
- **机制**：文件系统完整快照（非 git stash），支持创建/恢复/列表/变更对比
- **集成**：MCP server + PreToolUse hooks（批量编辑前自动 checkpoint）+ slash commands（/claudepoint, /undo）
- **防刷保护**：30 秒冷却时间防止 checkpoint 泛滥
- **定位**：解决"代码回滚"，与 PACEflow "流程执行"互补

**Compaction 问题全景**（Golev 文章 + GitHub issues）：
- GitHub #9796: compaction 后 100% 违反项目指令（CLAUDE.md/project-context.md 全部丢失）
- GitHub #13919: compaction 后完全忘记 Skills（不会主动重读 skill 文件）
- GitHub #10960: compaction 后忘记当前仓库和工作目录
- DoltHub 工程博客："Definitely dumber after the compaction"
- **核心问题**：compaction 有损摘要，偏重时近性(recency)而非重要性(importance)
- **社区应对**：a) 逻辑断点主动 /compact; b) 关键上下文存 CLAUDE.md; c) 直接退出重启; d) 让 AI 维护运行日志

**与 PACEflow 现状对比**：

| 能力 | PACEflow SessionStart | PopKit session-capture | ClaudePoint |
|------|----------------------|----------------------|-------------|
| Artifact 内容注入 | ✅ 5 文件活跃区原始内容 | ❌ | ❌ |
| Git 状态捕获 | ❌ | ✅ branch/commit/uncommitted | ✅ 文件系统快照 |
| 恢复策略分级 | ❌ 一律全量注入 | ✅ 三级（时间间隔） | ❌ 手动选择 |
| 项目健康检查 | ❌ | ✅ test/build/lint | ❌ |
| 任务强制执行 | ✅ deny/block | ❌ | ❌ |
| 代码回滚 | ❌ | ❌ | ✅ 完整快照 |

**结论与建议**：
- **PACEflow 核心定位不变**：执行纪律强制（hooks deny/block），不做完整 checkpoint
- **低成本改进**（推荐）：SessionStart 增加 `git branch --show-current` + `git log -1 --oneline` 注入（2-3 行代码）
- **中成本改进**（可选）：Stop hook 生成精简版 `.pace/session-state.json`（focus/nextAction/keyDecisions）
- **推荐搭配**：用户按需安装 ClaudePoint（代码回滚）或 PopKit（完整 session 管理），与 PACEflow 互补
- **不做**：完整文件系统快照、MCP server、恢复策略分级——超出 PACEflow "流程执行"定位

**参考资源**：
- PopKit: https://github.com/jrc1883/popkit-claude
- ClaudePoint: https://github.com/andycufari/ClaudePoint (232 stars)
- Golev 文章: https://golev.com/post/claude-saves-tokens-forgets-everything/
- GitHub #7584: Add Persistent Session Storage
- GitHub #6001: Native Undo/Checkpoint/Restore
- Reddit: "How do you handle context loss between Claude Code sessions?" (2026-01)

### [2026-02-16] OpenSpec 对比分析：三层定位与集成可能

**问题/目标**：评估 Fission-AI/OpenSpec（v1.1.1, 24.3k stars）与 PACEflow 的关系和集成可能性

**来源**：https://github.com/Fission-AI/OpenSpec

**核心定位**：Spec-driven Development (SDD)，每个变更独立文件夹（proposal.md + specs/ + design.md + tasks.md），通过 slash commands 驱动（/opsx:new → /opsx:ff → /opsx:apply → /opsx:archive）

**三层互补模型**：
- **Superpowers** → 怎么想（brainstorming、创意发散、debugging 方法论）
- **OpenSpec** → 做什么（WHEN-THEN 场景化需求、Goals/Non-Goals、结构化 proposal）
- **PACEflow** → 必须做（有任务才能写代码、写完必须验证、deny/block 强制）

**Artifact 结构冲突**：
| 维度 | OpenSpec | PACEflow |
|------|----------|----------|
| 任务文件 | `openspec/changes/xxx/tasks.md` | 项目根 `task.md` |
| 需求文件 | `proposal.md` + `specs/` | `spec.md` |
| 设计文件 | `design.md` | `implementation_plan.md` |
| 归档方式 | 整个文件夹移到 `archive/` | `<!-- ARCHIVE -->` 双区标记 |
| 任务格式 | 分组编号 `1.1` `1.2` | `T-NNN` + 5 种状态标记 |

**集成方案（如需）**：
- `pace-utils.js`：`isPaceProject()` 增加 `openspec/changes/` 信号检测
- `pre-tool-use.js`：支持读取 `openspec/changes/*/tasks.md` 作为任务来源
- `session-start.js`：注入 OpenSpec 活跃变更的上下文
- 改动量中等，需要适配任务格式差异

**结论**：OpenSpec 解决的是需求清晰度问题（之前讨论认为应交给 Superpowers 层而非 PACEflow 层），三层可互补但 Artifact 结构差异大。待评估是否值得投入适配。

---

### [2026-02-16] HelloAGENTS 对比分析：安装部署体验改进

**问题/目标**：对比 hellowind777/helloagents（v2.2.8）与 PACEflow，提取可借鉴的工程改进

**来源**：https://github.com/hellowind777/helloagents

**结论**：工作流设计路线不同（HelloAGENTS 重量级多 CLI / PACEflow 轻量 Claude Code 专用），无可借鉴。但安装部署体验差距明显，提炼 4 项改进：

**改进 1：一键安装脚本**
- 现状：5 步手动操作（复制 hooks → 复制 3 个 skill 目录 → 编辑 settings.json → 复制 CLAUDE.md → 重启）
- 目标：`node paceflow/install.js`（交互式）或 `node paceflow/install.js --all`（全量）
- 范围：自动复制文件 + patch settings.json hooks 段 + 检测冲突并备份
- 约束：保持 Node.js 零依赖

**改进 2：状态检查 / 健康诊断**
- 现状：无。只能靠运行时报错或手动 `diff` + `node -c` 验证
- 目标：`node paceflow/verify.js` 输出每个文件的安装状态（✅ 一致 / ⚠️ 版本落后 / ❌ 缺失）
- 范围：hooks 6 文件 + skills 3 目录 + settings.json hook 条目 + 模板文件

**改进 3：更新 & 卸载**
- 现状：更新靠手动 `cp`，卸载靠手动删文件 + 手动清理 settings.json
- 目标：`node paceflow/install.js --update`（差量更新）+ `node paceflow/install.js --uninstall`（干净移除）
- 范围：hooks + skills + settings.json 条目 + 模板，不动 CLAUDE.md（用户可能已自定义）

**改进 4：冲突处理 / 备份**
- 现状：直接覆盖，不检测冲突
- 目标：安装时检测已存在文件，非 PACEflow 文件备份为 `*.bak.YYYYMMDD` 后再替换
- 范围：settings.json 做 merge（只添加 PACEflow hook 条目，不删除已有 hooks）

**不借鉴项**：npm 包分发、聊天内 `~command`、9 hook 事件（5 个已够）、pyproject.toml 包管理、12 角色 RLM、三层 EHRB、多 CLI 适配

---

### [2026-02-16] PACEflow 与 Subagent/Agent Teams 兼容性调研（更新：Agent Teams 实测）

**问题/目标**：验证 PACEflow hooks 在 Subagent（Task 工具）和 Agent Teams（实验性）环境中是否正常工作

**来源链接**：
- GitHub #21460（[SECURITY] PreToolUse hooks not enforced on subagent tool calls）
- GitHub #16424（Expose Agent Context in Hook Event Payloads）
- GitHub #16126（Add agent identity to PreToolUse hook data）
- GitHub #14859（Agent Hierarchy in Hook Events）
- 参考项目：disler/claude-code-hooks-mastery、KimYx0207/agent-teams-playbook

**关键发现**：

#### 1. Subagent（Task 工具）— 实测验证

| 测试项 | 结果 | 证据 |
|--------|------|------|
| PreToolUse deny 阻止 subagent 写 `.js` | ✅ **生效** | 文件未创建，日志记录 DENY，stderr 反馈到 subagent |
| TodoWrite hint 注入 subagent TaskCreate | ✅ **生效** | additionalContext 成功注入，日志记录 HINT |

**与 #21460 的矛盾**：该 issue 声称 "PreToolUse hooks not enforced on subagent tool calls"，但 2026-02-16 实测 deny 和 additionalContext 均完全生效。可能原因：
- 该 issue 已在近期版本静默修复
- 仅影响 plugin 级 hooks，不影响 settings.json 全局 hooks
- 仅影响特定 subagent 类型

#### 2. Agent Teams Teammate — 实测验证（2026-02-16 新增）

Teammate 是独立 Claude Code 进程，各自加载 `settings.json` 全部 hooks。

| Hook | 是否触发 | 日志 action | 说明 |
|------|----------|------------|------|
| session-start.js | ✅ | INJECT | 注入 5 个 artifact 活跃区到 teammate 上下文 |
| pre-tool-use.js | ✅ | DENY | 阻止 teammate 写 `_teammate_test.js`（无活跃任务） |
| todowrite-sync.js | ✅ | HINT | Lead 的 TaskCreate 触发（误报：团队任务 vs PACE 任务） |
| stop.js | ✅ | TW_CLEANUP | teammate 停止时清理 todowrite-used flag |
| post-tool-use.js | 未触发 | — | Write 被 deny，无 PostToolUse 事件（符合预期） |

**环境变量**：teammate 进程有 `CLAUDECODE=1`、`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`、`CLAUDE_CODE_ENTRYPOINT=cli`，但无法区分 lead vs teammate。

**todowrite-sync 误报问题**：teammate 的 TaskCreate/TaskUpdate 操作的是团队任务（`~/.claude/tasks/{team-name}/`），不是 PACE 的 task.md。但 todowrite-sync.js 无法区分，产生不相关的 HINT。影响极低——仅 additionalContext 提醒，不阻止操作。标记为 🔒 已知限制。

#### 3. Hook Payload 无法区分主 agent、subagent、teammate

PreToolUse stdin JSON 只有 `session_id`、`tool_name`、`tool_input`、`tool_use_id` 等通用字段，**不包含** `agent_id`、`agent_type`、`is_subagent` 等标识字段。Feature request #16424/#16126/#14859 处于 open 状态。

#### 4. 多 teammate 并发竞态 — 理论分析

多个 teammate 同时触发 Stop → 并发读写 `.pace/stop-block-count` 文件 → 计数可能丢失/覆盖。Node.js `fs.readFileSync`/`fs.writeFileSync` 无文件锁。单 teammate 测试未触发竞态。标记为 🔒 已知限制（Agent Teams 仍为实验性功能）。

**结论**：PACEflow 与 Subagent 和 Agent Teams **完全兼容**——全部 hooks 生效，deny 阻止有效。已知限制为 todowrite-sync 误报和多 teammate 理论竞态，均标记为 🔒。

### [2026-02-14] PACE-TodoWrite 同步方案调研

**问题/目标**：解决 compaction 后 TodoWrite 残留导致 AI 重复执行已完成任务的问题，设计多层缓解方案

**来源链接**：
- GitHub #15174（compact hook stdout 注入 bug，v2.1.25+ 已修复）
- GitHub #14258（PostCompact hook 需求，Open）
- GitHub #17237（PreCompact/PostCompact hooks 请求，Open）
- GitHub #3537（缺少 postCompact hook bug，Open）
- GitHub #6975（PreToolUse:TodoWrite matcher，社区验证可用）
- GitHub #20144（PostToolUse:TodoWrite Windows 不触发，Open bug）
- GitHub #4368（PreToolUse updatedInput 功能，v2.0.10+）
- Superpowers #385（注入 >3KB 触发无限 compact 循环）

**关键发现**：

#### 1. SessionStart compact matcher 行为

| 特性 | 结论 |
|------|------|
| compact matcher 可用性 | ✅ v2.1.25+ 确认可用（#15174 早期 bug 已修复） |
| stdout 注入位置 | compaction summary **之后**注入（不被覆盖） |
| 执行时序 | compaction → CLAUDE.md 从磁盘重新加载 → SessionStart:compact → 注入 |
| 注入大小限制 | < 500 tokens 安全（>3KB 可能触发无限 compact 循环，Superpowers #385） |
| CLAUDE.md 重加载 | ✅ 确认 compaction 后从磁盘重新加载（#14258） |

#### 2. TodoWrite Hook 检测能力

| Hook 类型 | matcher | 状态 | 来源 |
|-----------|---------|------|------|
| PreToolUse:TodoWrite | `TodoWrite` | ✅ 社区验证可用 | #6975、Archon #237、Gist FrancisBourre |
| PostToolUse:TodoWrite | `TodoWrite` | ❌ Windows 有 Bug | #20144（Open，已确认） |
| PreToolUse updatedInput | 修改 tool_input | ✅ v2.0.10+ 支持 | #4368 |

- TodoWrite 的 `tool_input` 结构：`{ todos: [{ content, status: "pending|in_progress|completed", activeForm }] }`
- TodoWrite 未在官方 matcher 文档中列出，但 matcher 本质是 regex 匹配 tool_name
- PreToolUse 可通过 `updatedInput` 修改 TodoWrite 参数（理论可行，需实测）

#### 3. 四层缓解方案设计

| 层 | 方案 | 机制 | 可靠性 | 改动量 |
|----|------|------|--------|--------|
| A | SessionStart 注入同步指令 | startup/resume/compact 时读 task.md 活跃任务 → 注入"task.md > TodoWrite"优先级声明 + 当前任务列表 | 确定性注入，建议性遵守 | ~10 行 session-start.js |
| B | CLAUDE.md 优先级规则 | G-3 补充"task.md 是任务权威来源，TodoWrite 与之冲突时以 task.md 为准" | 建议性 ~85% | ~2 行 CLAUDE.md |
| C | PostToolUse task.md 变更提醒 | Edit task.md 后检测新增/完成/归档 → additionalContext 提醒同步 TodoWrite | 确定性注入，建议性遵守 | ~15 行 post-tool-use.js |
| D | PreToolUse:TodoWrite 拦截 | 拦截 TodoWrite 调用，校验与 task.md 一致性 → 不一致时 deny 或 updatedInput | 确定性（需实测） | settings.json + 新脚本 |

**方案 A 详情**：
- startup：读 task.md 活跃区 → 有任务时注入"请用 TodoWrite 创建对应任务"
- resume：同上（可能有未同步的任务）
- compact：注入"⚠️ task.md 是任务权威来源。如 TodoWrite 与 task.md 冲突，以 task.md 为准"+ 当前活跃任务列表
- 注入大小需控制在 < 500 tokens

**方案 C 详情**：
- 检测 task.md 活跃区中 `[ ]`/`[/]` 新增 → 提醒"请用 TodoWrite 同步新任务"
- 检测 `[x]`/`[-]` 标记 → 提醒"请用 TodoWrite 标记对应任务完成"
- 检测全部归档 → 提醒"请清空 TodoWrite"
- 限制：post-tool-use.js 无 diff 信息，只能基于当前状态判断

**方案 D 详情**：
- PreToolUse:TodoWrite 拦截所有 TodoWrite 调用
- 读 task.md 活跃任务列表，比对 TodoWrite 的 todos 数组
- 不一致时可选：deny + 原因反馈 / updatedInput 强制对齐
- 风险：TodoWrite 用于非 PACE 场景（如 Superpowers 自身任务管理）时可能误拦截

**关键结论**：A+B+C 为核心方案（建议性但多层叠加），D 为增强方案（确定性但需验证兼容性）。A 和 B 改动最小且无副作用，应优先实施。

### [2026-02-14] TodoWrite/Tasks 存储机制与 Hook 交互可行性

**问题/目标**：调研 TodoWrite 的底层存储机制，评估 Hook 能否直接操作 TodoWrite 状态

**来源链接**：
- `~/.claude/tasks/<session-id>/N.json` — 实际存储路径
- GitHub #14258（PostCompact hook 需求）
- Superpowers 插件源码（TodoWrite 使用模式分析）

**关键发现**：
- Tasks 存储在 `~/.claude/tasks/<session-id>/N.json`，每个 task 一个 JSON 文件
- TodoWrite 是**内存中的 API 调用**，Hook 无法直接修改内存中的 TodoWrite 状态
- Hook 只能通过 additionalContext/deny/updatedInput **间接影响** AI 的 TodoWrite 行为
- PostCompact hook 不存在（#14258 等待中），无法在 compaction 后立即清理 TodoWrite
- Superpowers 的 TodoWrite 使用是纯建议性的，AI 自主创建和标记完成
- compaction summary 中保留了旧 todo snapshot，这是 TodoWrite 残留的根本原因

### [2026-02-11] Hook 路径格式

**问题/目标**：确定 Windows 上 Claude Code hooks 的正确路径格式

**发现内容**：Claude Code 在 Windows 上用 `/bin/bash` 执行 hook command，`K:/` 盘符路径不被识别，必须使用 Git Bash 风格 `/k/` 或 `/c/` 路径

**来源链接**：GitHub issue #3583

**关键结论**：全局 hooks 使用 `/c/Users/Xiao/.claude/hooks/pace/*.sh` 路径

### [2026-02-13] Hooks 官方文档深度调研

**问题/目标**：全面调研 Claude Code Hooks 的 stdin/stdout/stderr 协议、exit code 含义、blocking 机制、各 hook 事件的技术细节

**来源链接**：
- https://code.claude.com/docs/en/hooks （Hooks Reference）
- https://code.claude.com/docs/en/hooks-guide （Hooks Guide）

**关键发现**：

#### 1. Hook 事件完整列表（14 种）

| 事件 | 触发时机 | 可阻止？ |
|------|----------|----------|
| `SessionStart` | 会话开始/恢复 | 否 |
| `UserPromptSubmit` | 用户提交 prompt 后、Claude 处理前 | 是 |
| `PreToolUse` | 工具调用执行前 | 是 |
| `PermissionRequest` | 权限对话框出现时 | 是 |
| `PostToolUse` | 工具调用成功后 | 否（已执行） |
| `PostToolUseFailure` | 工具调用失败后 | 否（已失败） |
| `Notification` | 发送通知时 | 否 |
| `SubagentStart` | 子代理启动时 | 否 |
| `SubagentStop` | 子代理完成时 | 是 |
| `Stop` | Claude 完成响应时 | 是 |
| `TeammateIdle` | 团队成员即将空闲 | 是 |
| `TaskCompleted` | 任务被标记完成时 | 是 |
| `PreCompact` | 上下文压缩前 | 否 |
| `SessionEnd` | 会话终止时 | 否 |

#### 2. stdin/stdout/stderr 协议

**stdin**：所有 hook 通过 stdin 接收 JSON 数据，包含公共字段：
- `session_id` — 会话 ID
- `transcript_path` — 对话 JSON 路径
- `cwd` — 当前工作目录
- `permission_mode` — 权限模式（default/plan/acceptEdits/dontAsk/bypassPermissions）
- `hook_event_name` — 事件名称
- 加上各事件特有字段（如 `tool_name`、`tool_input`、`tool_response` 等）

**stdout 规则**：
- **exit 0 时**：Claude Code 解析 stdout 中的 JSON 输出
- **大多数事件**：stdout 仅在 verbose 模式（Ctrl+O）显示
- **例外 — SessionStart 和 UserPromptSubmit**：stdout 内容会被添加为 Claude 可见的上下文（context）
- **exit 2 时**：stdout 被忽略，JSON 也被忽略

**stderr 规则**：
- **exit 2 时**：stderr 文本作为错误消息反馈给 Claude（对于可阻止事件）或仅显示给用户（不可阻止事件）
- **其他非零 exit code**：stderr 在 verbose 模式显示，不影响执行
- **exit 0 时**：stderr 不被处理

#### 3. Exit Code 含义

| Exit Code | 含义 | stdout | stderr |
|-----------|------|--------|--------|
| **0** | 成功/允许 | 解析 JSON 输出 | 忽略 |
| **2** | 阻止操作 | 忽略（含 JSON 也忽略） | 反馈给 Claude 或显示给用户 |
| **其他非零** | 非阻止性错误 | 忽略 | 仅 verbose 模式显示 |

**exit 2 的逐事件行为**：

| 事件 | exit 2 效果 |
|------|-------------|
| PreToolUse | **阻止工具调用** |
| PermissionRequest | **拒绝权限** |
| UserPromptSubmit | **阻止 prompt 处理并擦除 prompt** |
| Stop | **阻止 Claude 停止，继续对话** |
| SubagentStop | **阻止子代理停止** |
| TeammateIdle | **阻止成员空闲（继续工作）** |
| TaskCompleted | **阻止任务标记为完成** |
| PostToolUse | 将 stderr 显示给 Claude（工具已执行） |
| PostToolUseFailure | 将 stderr 显示给 Claude |
| Notification | 仅显示给用户 |
| SubagentStart | 仅显示给用户 |
| SessionStart | 仅显示给用户 |
| SessionEnd | 仅显示给用户 |
| PreCompact | 仅显示给用户 |

#### 4. SessionStart hook 详情

- stdout 输出会被添加为 **Claude 可见的上下文**（additionalContext）
- 可用于动态注入项目信息、环境变量等
- 支持 `CLAUDE_ENV_FILE` 环境变量，可持久化环境变量供后续 Bash 命令使用
- matcher 值：`startup`（新会话）、`resume`（恢复）、`clear`（清除）、`compact`（压缩后）
- **不可阻止**（exit 2 仅显示 stderr 给用户）
- JSON 输出支持 `additionalContext` 字段

#### 5. PreToolUse hook 详情

- **可以阻止工具调用**（exit 2 或 JSON permissionDecision: "deny"）
- **可以修改工具参数**（通过 `updatedInput` 字段）
- **可以注入上下文**（通过 `additionalContext` 字段）
- 三种权限决策：
  - `"allow"` — 绕过权限系统直接允许
  - `"deny"` — 阻止工具调用，原因反馈给 Claude
  - `"ask"` — 提示用户确认
- stdin 包含 `tool_name`、`tool_input`、`tool_use_id`
- matcher 匹配工具名：`Bash`、`Edit`、`Write`、`Read`、`Glob`、`Grep`、`Task`、`WebFetch`、`WebSearch` 及 MCP 工具

#### 6. PostToolUse hook 详情

- **不可阻止操作**（工具已执行完成）
- stdout JSON 支持 `decision: "block"` + `reason`：会将原因反馈给 Claude
- 支持 `additionalContext` 字段：追加额外上下文给 Claude
- stdin 包含 `tool_input`（发送给工具的参数）和 `tool_response`（工具返回结果）
- 对 MCP 工具支持 `updatedMCPToolOutput` 替换输出

#### 7. 强制 AI 执行操作的方法

**(a) Stop hook 阻止停止**：
- exit 2 + stderr 消息 → Claude 收到消息后**被迫继续工作**
- JSON `decision: "block"` + `reason` → Claude 必须按 reason 继续
- **必须检查 `stop_hook_active` 字段防止无限循环**

**(b) PostToolUse 反馈**：
- `decision: "block"` + `reason` → 工具执行后将反馈注入 Claude 上下文
- `additionalContext` → 追加上下文信息

**(c) SessionStart 注入指令**：
- stdout 直接作为 Claude 上下文
- 可用于注入"必须执行"的指令（Claude 会看到但无法保证100%遵守）

**(d) UserPromptSubmit 增强**：
- `additionalContext` → 在用户 prompt 基础上追加上下文

**(e) Prompt/Agent 类型 hook**：
- `type: "prompt"` — 单轮 LLM 评估，返回 ok/not ok
- `type: "agent"` — 多轮子代理验证，可使用 Read/Grep/Glob 工具

**(f) TaskCompleted hook**：
- exit 2 → 阻止任务标记完成，stderr 反馈给模型
- 可用于强制执行完成标准（如测试必须通过）

#### 8. 其他重要技术细节

- **Hook 类型**：command（shell 命令）、prompt（单轮 LLM 评估）、agent（多轮子代理）
- **异步 hook**：`async: true` — 后台运行，不阻塞 Claude，结果在下一轮对话交付
- **超时默认值**：command 600 秒，prompt 30 秒，agent 60 秒
- **`once` 字段**：`true` 时仅运行一次（仅 skill 支持）
- **环境变量**：`$CLAUDE_PROJECT_DIR`（项目根）、`$CLAUDE_PLUGIN_ROOT`（插件根）、`$CLAUDE_CODE_REMOTE`（远程环境）
- **配置快照**：hooks 在启动时快照，运行中修改需通过 `/hooks` 菜单审核或重启
- **去重**：相同 handler 自动去重，所有匹配 hook 并行运行
- **JSON 输出必须是纯 JSON**：shell profile 中的 echo 会干扰解析（需要 `[[ $- == *i* ]]` 守卫）
- **`continue: false`**：任何事件都可以使用，强制 Claude 完全停止处理
- **`systemMessage`**：JSON 输出中的警告消息，显示给用户
- **`suppressOutput: true`**：隐藏 stdout 在 verbose 模式中的输出

### [2026-02-11] grep -qF 标记检测

**问题/目标**：`<!-- ARCHIVE -->` 标记检测在 Git Bash 中失败

**发现内容**：`grep -qF '<!-- ARCHIVE -->'` 中的 `--` 被 grep 解释为选项终止符，导致匹配失败

**解决方案**：改用 `grep -qF 'ARCHIVE'`，足够唯一且避免 `--` 问题

### [2026-02-13] Claude Code 工作流强制执行最佳实践研究

**问题/目标**：调研让 Claude Code 可靠执行结构化工作流的最佳实践，重点关注 CLAUDE.md 遵守问题、hooks 强制执行、文件自动创建

**来源链接**：
- https://code.claude.com/docs/en/hooks （Hooks Reference 完整文档）
- https://code.claude.com/docs/en/hooks-guide （Hooks Guide 实践指南）
- https://code.claude.com/docs/en/memory （CLAUDE.md 加载机制文档）
- https://code.claude.com/docs/en/skills （Skills 扩展系统文档）
- https://code.claude.com/docs/en/plugins （Plugins 系统文档）
- https://code.claude.com/docs/en/sub-agents （Subagents 子代理文档）
- https://code.claude.com/docs/en/best-practices （最佳实践官方文档）
- https://github.com/anthropics/claude-code/issues （GitHub Issues 社区反馈）

---

#### 1. CLAUDE.md 不被遵守：这是已知且普遍的问题

**GitHub Issues 确认此问题严重**：

| Issue # | 标题 | 状态 |
|---------|------|------|
| #24761 | Claude 不可靠地遵循 CLAUDE.md 中的多步骤指令 | OPEN |
| #23617 | CLAUDE.md 文件名限制指令被 auto-memory 功能忽略 | OPEN |
| #23478 | 路径规则（.claude/rules/ 带 paths frontmatter）仅在 Read 时加载，Write 时不加载 | OPEN |
| #23063 | Agent 经常丢失 CLAUDE.md 项目规则上下文 | CLOSED (DUPLICATE) |
| #23032 | Claude Code 忽略用户指令和 CLAUDE.md，破坏生产系统 | OPEN |
| #22638 | Claude 反复忽略 CLAUDE.md 规则，执行破坏性 git 命令导致数据丢失 | OPEN |
| #22501 | Claude 忽略 CLAUDE.md 指令，未经确认执行工具 | CLOSED (DUPLICATE) |
| #21604 | Claude Code 用"好心判断"覆盖 CLAUDE.md 明确指令 | OPEN |
| #21112 | Claude Code 忽略 CLAUDE.md 中的会话日志指令 | OPEN |
| #23936 | 高 think effort 导致 Opus 4.6 忽略 skills 和 CLAUDE.md 规则 | OPEN |
| #21925 | 上下文压缩后不重新加载 CLAUDE.md（设计缺陷） | OPEN |

**核心问题模式**：
1. **上下文压缩丢失** — CLAUDE.md 规则在上下文压缩后丢失/不重新加载
2. **Auto-Memory 绕过** — 自动记忆功能绕过 CLAUDE.md 的文件名限制
3. **模型"好心行为"** — Claude 做出"有帮助的判断"覆盖明确指令
4. **路径规则仅 Read 时加载** — Write 工具不触发路径规则加载
5. **高 think effort** — 默认高 think effort 使 Opus 4.6 更可能忽略规则

---

#### 2. 官方最佳实践：如何提高 CLAUDE.md 遵守率

**来源**：https://code.claude.com/docs/en/best-practices

**关键建议**：

**(a) 保持 CLAUDE.md 简洁**
> "Keep it concise. For each line, ask: 'Would removing this cause Claude to make mistakes?' If not, cut it. Bloated CLAUDE.md files cause Claude to ignore your actual instructions!"

- CLAUDE.md 过长是 Claude 忽略规则的最常见原因
- 仅保留 Claude 无法从代码推断的信息
- 删除 Claude 已正确执行的规则

**(b) 使用强调标记**
> "You can tune instructions by adding emphasis (e.g., 'IMPORTANT' or 'YOU MUST') to improve adherence."

**(c) 定期审查和修剪**
> "Treat CLAUDE.md like code: review it when things go wrong, prune it regularly, and test changes by observing whether Claude's behavior actually shifts."

**(d) CLAUDE.md 应包含 vs 不应包含**：

| 应该包含 | 不应该包含 |
|---------|-----------|
| Claude 无法猜测的 Bash 命令 | Claude 通过读代码能发现的内容 |
| 不同于默认的代码风格规则 | 语言标准约定 |
| 测试指令和首选测试运行器 | 详细 API 文档（改用链接） |
| 仓库规范（分支命名、PR 约定） | 频繁变化的信息 |
| 项目特有的架构决策 | 长篇解释或教程 |
| 开发环境怪癖（必需的环境变量） | 代码库文件逐个描述 |
| 常见陷阱或非显而易见的行为 | "写出干净代码"之类的显而易见的实践 |

**(e) Hooks 替代 CLAUDE.md**
> "Unlike CLAUDE.md instructions which are advisory, hooks are deterministic and guarantee the action happens."
> "Use hooks for actions that must happen every time with zero exceptions."

**这是最关键的结论**：CLAUDE.md 是"建议性"（advisory）的，而 hooks 是"确定性"（deterministic）的。如果某件事必须每次都执行，用 hooks 而不是 CLAUDE.md。

---

#### 3. Hooks 强制执行方案（完整方案列表）

**(a) SessionStart hook — 文件自动创建**

最直接的方案：在会话开始时自动创建模板文件并注入上下文。

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/session-init.sh"
          }
        ]
      }
    ]
  }
}
```

SessionStart hook 的特殊能力：
- stdout 直接作为 Claude 上下文（additionalContext）
- 可通过 `CLAUDE_ENV_FILE` 设置环境变量
- matcher 区分 startup/resume/clear/compact
- 不可阻止（exit 2 仅显示 stderr 给用户）

**关键发现**：SessionStart 创建的文件 Claude **可以看到**，因为：
1. SessionStart hook 先于 Claude 处理用户输入执行
2. CLAUDE.md 文件在会话开始时加载
3. 但 SessionStart hook 创建/修改的 CLAUDE.md 可能**不会被重新加载**（因为 CLAUDE.md 在 hook 之前已经加载了）
4. **替代方案**：SessionStart hook 的 stdout 直接注入 Claude 上下文，比修改 CLAUDE.md 更可靠

**(b) PreToolUse hook — 拦截并强制先决条件**

使用 PreToolUse deny 来强制 AI 在执行操作前满足条件：

```bash
#!/bin/bash
# 检查模板文件是否存在，如不存在则阻止写入操作
INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name')

if [ "$TOOL" = "Write" ] || [ "$TOOL" = "Edit" ]; then
  if [ ! -f "$CLAUDE_PROJECT_DIR/spec.md" ]; then
    jq -n '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "必须先创建 spec.md 模板文件。请先执行 /init-project skill。"
      }
    }'
    exit 0
  fi
fi
exit 0
```

**(c) PostToolUse hook — 执行后验证并反馈**

```bash
#!/bin/bash
# 每次文件写入后检查格式合规性
INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ "$FILE" == *"task.md" ]]; then
  if ! grep -q 'ARCHIVE' "$FILE" 2>/dev/null; then
    echo '{"decision":"block","reason":"task.md 缺少 ARCHIVE 分隔标记。请添加 <!-- ARCHIVE --> 标记。"}'
    exit 0
  fi
fi
exit 0
```

**(d) Stop hook — 强制完成检查**

使用 Stop hook 阻止 Claude 在未完成必要步骤时停止：

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "检查 Claude 是否完成了所有任务。检查 task.md 中是否有未完成的 [/] 任务。如果有未完成的任务，回复 {\"ok\": false, \"reason\": \"仍有未完成的任务\"}。$ARGUMENTS"
          }
        ]
      }
    ]
  }
}
```

**(e) TaskCompleted hook — 强制任务完成标准**

```bash
#!/bin/bash
# 阻止任务标记为完成除非所有检查通过
INPUT=$(cat)
SUBJECT=$(echo "$INPUT" | jq -r '.task_subject')

# 检查 artifact 文件是否已更新
if [ ! -f "$CLAUDE_PROJECT_DIR/walkthrough.md" ]; then
  echo "任务 '$SUBJECT' 完成前必须更新 walkthrough.md" >&2
  exit 2
fi
exit 0
```

**(f) 上下文压缩后重新注入（compact matcher）**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "compact",
        "hooks": [
          {
            "type": "command",
            "command": "cat \"$CLAUDE_PROJECT_DIR/spec.md\" && echo '---' && cat \"$CLAUDE_PROJECT_DIR/task.md\""
          }
        ]
      }
    ]
  }
}
```

---

#### 4. CLAUDE.md 加载机制分析

**来源**：https://code.claude.com/docs/en/memory

**加载层级**（从低优先级到高优先级）：

| 类型 | 位置 | 范围 |
|------|------|------|
| 托管策略 | `/Library/Application Support/ClaudeCode/CLAUDE.md`（macOS） | 组织级 |
| 项目记忆 | `./CLAUDE.md` 或 `./.claude/CLAUDE.md` | 项目级（可 git 共享） |
| 项目规则 | `./.claude/rules/*.md` | 项目级（可 git 共享） |
| 用户记忆 | `~/.claude/CLAUDE.md` | 用户级（所有项目） |
| 项目本地 | `./CLAUDE.local.md` | 个人项目级 |
| 自动记忆 | `~/.claude/projects/<project>/memory/` | 自动（每项目） |

**加载时机**：
- 工作目录层级以上的 CLAUDE.md 在**启动时全量加载**
- 子目录的 CLAUDE.md 在 Claude **读取该目录文件时按需加载**
- 自动记忆仅加载 MEMORY.md 的前 200 行
- **更具体的指令优先级高于更广泛的**

**关键发现 — SessionStart hook 和 CLAUDE.md 的时序**：
- CLAUDE.md 在会话开始时加载到 Claude 的系统提示中
- SessionStart hook 也在会话开始时运行
- 但两者的**确切执行顺序**文档中未明确说明
- **最安全的方案**：SessionStart hook 通过 stdout 注入 additionalContext，而非修改 CLAUDE.md 文件

**imports 机制**：
- CLAUDE.md 支持 `@path/to/import` 语法导入其他文件
- 相对路径相对于包含导入的文件解析
- 最大递归深度 5 层
- 首次遇到外部导入时显示审批对话框

---

#### 5. Skills 作为工作流强制执行的补充

**来源**：https://code.claude.com/docs/en/skills

Skills 是 CLAUDE.md 的补充，用于按需加载而非全量加载：

**关键特性**：
- Skills 可以定义自己的 hooks（在 frontmatter 中），这些 hooks 仅在 skill 活跃时运行
- `once: true` 参数使 hook 仅运行一次
- `disable-model-invocation: true` 防止 Claude 自动触发
- `allowed-tools` 限制 skill 可用的工具
- `context: fork` 在独立子代理中运行

**Skill + Hook 组合模式**：

```yaml
---
name: init-project
description: 初始化项目模板文件
disable-model-invocation: true
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-init.sh"
          once: true
---

创建以下模板文件：
1. spec.md — 项目规格
2. task.md — 任务追踪
3. implementation_plan.md — 实施计划
...
```

---

#### 6. Plugins 打包分发方案

**来源**：https://code.claude.com/docs/en/plugins

Plugin 可以将 skills + hooks + agents 打包成一个可安装的单元：

```
my-workflow-plugin/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── init-project/
│       └── SKILL.md
├── hooks/
│   └── hooks.json
└── agents/
    └── reviewer.md
```

**hooks.json 格式**（plugin 级别）：

```json
{
  "description": "工作流强制执行 hooks",
  "hooks": {
    "SessionStart": [...],
    "PreToolUse": [...],
    "PostToolUse": [...],
    "Stop": [...]
  }
}
```

---

#### 7. Prompt/Agent 类型 Hook — 高级验证

**来源**：https://code.claude.com/docs/en/hooks

除 command 类型外，hooks 还支持 prompt 和 agent 类型：

**(a) Prompt hook** — 用快速模型进行单轮验证：
```json
{
  "type": "prompt",
  "prompt": "评估 Claude 是否应该停止。检查 $ARGUMENTS 中的上下文，确认所有任务是否完成。",
  "model": "haiku",
  "timeout": 30
}
```

**(b) Agent hook** — 用子代理进行多轮验证（可使用 Read/Grep/Glob 工具）：
```json
{
  "type": "agent",
  "prompt": "验证所有单元测试通过。运行测试套件并检查结果。$ARGUMENTS",
  "timeout": 120
}
```

---

#### 8. 综合推荐方案

基于以上调研，解决"让 Claude Code 可靠执行结构化工作流"的最佳方案是**多层防御**：

| 层级 | 机制 | 作用 | 可靠性 |
|------|------|------|--------|
| 第 1 层 | SessionStart hook | 创建模板文件 + 注入上下文 | 确定性（100%） |
| 第 2 层 | CLAUDE.md 规则 | 告知 Claude 工作流程 | 建议性（~70-85%） |
| 第 3 层 | PreToolUse hook | 拦截不合规操作 | 确定性（100%） |
| 第 4 层 | PostToolUse hook | 写后验证并反馈 | 确定性（100%） |
| 第 5 层 | Stop hook | 完成前检查清单 | 确定性（100%）|
| 第 6 层 | compact SessionStart | 压缩后重新注入上下文 | 确定性（100%） |
| 第 7 层 | TaskCompleted hook | 阻止不合格的任务完成 | 确定性（100%） |

**核心原则**：
- **不要仅依赖 CLAUDE.md** — 它是建议性的，不是确定性的
- **关键操作用 hooks 保障** — hooks 是确定性执行的
- **SessionStart + compact 双保险** — 确保上下文压缩后规则不丢失
- **PreToolUse 是最强的前置拦截** — 可以阻止任何不合规的工具调用
- **Stop hook 是最后防线** — 确保 Claude 不会在未完成所有步骤时结束

**具体到你的场景（PACE 工作流）的推荐实现**：

1. **SessionStart (startup)** → 脚本检查并创建 spec.md/task.md 等模板文件，stdout 输出当前任务状态
2. **SessionStart (compact)** → 重新注入 spec.md + task.md 核心内容
3. **PreToolUse (Write|Edit)** → 检查 artifact 文件格式合规性（如 `<!-- ARCHIVE -->` 标记存在）
4. **PostToolUse (Write|Edit)** → 验证写入后的文件格式，反馈给 Claude
5. **Stop** → prompt hook 验证 task.md 中无遗漏的任务
6. **CLAUDE.md** → 保持简洁，仅包含最核心的规则
7. **Skills** → 将 PACE 工作流各阶段定义为 skills，按需加载
