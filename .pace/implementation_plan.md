# 实施计划

> **最后更新**: 2026-03-12T20:35:00+08:00

---

## 变更索引

<!-- 格式：- [状态] CHG-ID 标题 #change [tasks:: T-NNN~T-NNN] -->

- [/] CHG-20260313-01 desktop runtime 实施 #change [tasks:: T-412~T-420]
- [x] CHG-20260312-01 desktop 运行时设计规格审查修订 #change [tasks:: T-408~T-411]
- [/] CHG-20260311-01 测试 Superpowers 桥接功能 #change [tasks:: T-404~T-407]
- [x] CHG-20260310-02 ticket18 可操作发现修复 — DRY 重构 + 常量化 + 纠偏协议 + Flag 文档 + install 测试 #change [tasks:: T-397~T-403]
- [x] HOTFIX-20260310-01 config-guard.js S-1 重构遗漏变量名修复 #change [tasks:: T-396]
- [x] CHG-20260309-06 S-3 版本自动化脚本 #change [tasks:: T-394~T-395]
- [x] CHG-20260309-05 S-1 统一 stdin 解析 #change [tasks:: T-390~T-393]
- [x] HOTFIX-20260309-03 walkthrough 省略行列数修复 #change [tasks:: T-389]
- [x] CHG-20260309-04 SessionStart 注入量精简 — 统一截断 spec/walkthrough 索引/findings 索引 #change [tasks:: T-385~T-388]
- [x] CHG-20260309-03 Artifact 归档机制增强 — SessionStart 智能截断 + 归档提醒 #change [tasks:: T-378~T-384]

## 活跃变更详情

<!-- 每个变更索引必须有对应的详情段落 -->

### CHG-20260313-01 desktop runtime 实施

基于已批准的 desktop runtime spec 与已写好的 implementation plan，开始把当前单文件 `desktop.py` 演进为 Hybrid-first primitive runtime，并按计划分阶段完成测试骨架、backend/router/executor、CLI 兼容层和微信脚本迁移。

**T-412 建立 desktop runtime 测试骨架**：
- 新增 `requirements-dev.txt` 与 `.claude/skills/desktop/tests/` 基础测试文件
- 先锁定 result/region/safety 的最小公共契约

**T-413 固化 adapters 边界，抽离旧底层能力**：
- 将截图、输入、窗口操作从 `desktop.py` 拆到 `adapters/`
- 为 CLI 建立可 monkeypatch 的 runtime 入口函数

**T-414 落地 OCR / UIA / template backend 最小实现**：
- 抽出 OCR backend
- 建立最小可用 UIA backend 与 template 占位 backend

**T-415 实现 router 的 find/read/wait 动作分流**：
- 按 spec 固化 OCR/UIA fallback、歧义判定、wait_mode 语义
- 统一 debug 字段与失败上下文

**T-416 实现 executor 的 11 个 primitive 与 safety 校验**：
- 在 `core/executor.py` 暴露统一 primitive API
- 接入 `region`、`safety`、`assert`、`wait_*` 契约

**T-417 切换 desktop CLI 到 runtime 薄封装**：
- 保持旧参数入口兼容
- 内部统一转调 runtime executor

**T-418 迁移微信读取/发送/监控脚本到 runtime**：
- `wechat-read.py`、`wechat-send.py`、`wechat-monitor.py`、`wechat-autochat.py` 改为复用 runtime
- 逐步去掉脚本内直连底层桌面库的逻辑

**T-419 更新 desktop 文档与兼容映射**：
- 更新 `SKILL.md` 与 `REFERENCE.md`
- 补充 primitive/runtime 视角说明、兼容映射和 debug/safety 说明

**T-420 执行测试与 smoke 验证**：
- 运行单元测试、mock 半集成测试与关键 CLI/脚本 smoke case
- 为后续 Verify 阶段准备验证依据

### CHG-20260312-01 desktop 运行时设计规格审查修订

将已批准的 desktop runtime 设计文档从“方向性设计”继续收敛为“可直接实施的规格”，补齐可执行阈值、等待/断言语义、验收标准与兼容迁移说明，然后进入下一轮规格审查。

**T-408 补齐路由阈值与 assert/wait 语义**：
- 明确 `find` 的不稳定命中判定阈值与 fallback 条件
- 明确 `assert` 的一次性观测语义与 `wait_*` 的轮询语义边界

**T-409 补齐验收指标与兼容迁移计划**：
- 为第一阶段补充可验证的成功标准、flaky 判定与性能边界
- 说明旧 CLI / 微信脚本如何逐步迁移到新 primitive runtime

**T-410 发起第二轮规格审查并收敛问题**：
- 在补齐缺口后重新进行 spec review
- 根据 review 结果继续修订直到可接受

**T-411 通知用户审阅规格文件**：
- 在规格审查通过后，请用户 review `docs/superpowers/specs/2026-03-12-desktop-runtime-design.md`
- 用户确认后再切换到 `superpowers:writing-plans`

### CHG-20260311-01 测试 Superpowers 桥接功能

验证 PACEflow 的 Superpowers 桥接功能是否正常工作。

**T-404 创建测试计划文件**：
- 在 docs/plans/ 目录创建测试计划文件

**T-405 验证 Hooks 检测到计划文件**：
- 切换到严格模式，观察 Hooks 响应

**T-406 执行 pace-bridge 桥接**：
- 调用 pace-bridge skill 进行桥接

**T-407 检查 task.md 是否正确生成任务**：
- 验证任务列表是否正确转换

<!-- ARCHIVE -->

### CHG-20260310-02 ticket18 可操作发现修复

ticket18 审查报告 10 项发现中 5 项值得执行。涵盖代码质量（DRY + 常量化）、协议完善（E 阶段纠偏）、文档补全（Flag 生命周期）、测试覆盖（install.js 零测试→核心路径覆盖）。

**T-397 pace-utils.js 新增共享函数 + 常量**：
- 新增 `extractOpenKeys(text)` 函数：从 findings 活跃区提取 `[ ]` 开放项前 8 字 key，返回 `string[]`
- 新增 `ARCHIVE_MARKER = '<!-- ARCHIVE -->'` 字符串常量
- 新增 `ARCHIVE_PATTERN = /^<!-- ARCHIVE -->$/m` 正则常量
- 三者加入 module.exports

**T-398 [P] 4 hook openKeys + ARCHIVE 硬编码替换**：
- session-start.js：L202-205 openKeys 替换为 `extractOpenKeys()` 调用 + ~7 处 ARCHIVE 字符串/正则替换为常量
- post-tool-use.js：L184-187 openKeys 替换 + ~2 处 ARCHIVE 替换
- stop.js：L120-123 openKeys 替换 + ~2 处 ARCHIVE 替换
- pre-tool-use.js：~2 处 ARCHIVE 替换（无 openKeys）
- pace-utils.js 内部：readActive/checkArchiveFormat 改为引用自身常量

**T-399 pace-workflow SKILL.md E 阶段纠偏协议**：
- 在 E 阶段 "执行中维护" 后新增 "执行中纠偏" 段落
- 定义标准流程：检测偏差 → 当前任务标 `[!]` → 回到 A 阶段更新 impl_plan → 用户重新 APPROVED → 恢复 `[/]` 继续执行
- 明确触发条件（方案根本性错误 vs 小范围调整）

**T-400 REFERENCE.md Flag 生命周期表**：
- 新增 "运行时状态文件" section，包含完整 Flag 生命周期表
- 覆盖 8 个 SESSION_SCOPED_FLAGS + stop-block-count + degraded + current-native-plan + synced-plans + pre-compact-state.json
- 列：Flag 名 | 写入方 | 读取方 | 清除方 | 生命周期 | 用途

**T-401 test-install.js 新建 — 核心路径测试**：
- 遵循 test-pace-utils.js 测试模式（native assert + makeTmpDir + cleanup）
- install.js 函数不导出，采用 subprocess 集成测试（`execFileSync('node', ['install.js', ...], { cwd, env })`）
- 测试分组：标准安装（hooks+skills+settings 文件创建验证）/ settings.json 合并（已有用户 hook 保留 + PACE hook 更新）/ 备份（.bak 文件创建验证）/ --dry-run（零文件变更验证）/ --plugin 模式 / --migrate 模式 / 边界情况（无效 JSON settings / 缺失源文件）
- 目标 ~15-20 测试

**T-402 test-pace-utils.js 补充单元测试**：
- extractOpenKeys：空文本 / 无 `[ ]` 项 / 多项提取 / 前 8 字截断
- ARCHIVE_MARKER/ARCHIVE_PATTERN：字符串值断言 / 正则匹配行为

**T-403 全量验证**：
- 语法 8/8 + 单元测试（66 + 新增）+ E2E 61/61 + verify + test-install.js 全通过

### HOTFIX-20260310-01 config-guard.js S-1 重构遗漏变量名修复

CHG-20260309-05 S-1 重构将 config-guard.js stdin 入口改为 `withStdinParsed((stdin, rawInput) => {...})`，但 L46 降级路径 `configObj ? JSON.stringify(configObj) : input` 的 `input` 未同步改为 `rawInput`。正常路径不触发（configObj 非 null），降级路径（JSON 解析失败）导致 `input` 为 undefined → `.test(undefined)` 返回 false → hook 删除检测静默失效。

**T-396 修复 L46 `input` → `rawInput`**：
- config-guard.js L46 `input` → `rawInput`（闭包参数名一致）

### CHG-20260309-06 S-3 版本自动化脚本

新建 `paceflow/bump-version.js` 独立脚本，一条命令同步 5 个文件的版本号。解决当前手动同步 5 文件的遗漏风险（ticket17 审查中版本不一致是 P0 修复项）。

**T-394 新建 bump-version.js**：

用法：`node paceflow/bump-version.js 5.1.0`（或 `v5.1.0`）

版本号标准化：
- `cleanVer = version.replace(/^v/, '')` → `5.1.0`（JSON 文件用）
- `displayVer = 'v' + cleanVer` → `v5.1.0`（Markdown/代码用）
- 格式校验 `/^\d+\.\d+\.\d+$/`，不合法则 exit 1

5 个目标文件更新规则：

| 文件 | 匹配模式 | 替换为 |
|------|----------|--------|
| `hooks/pace-utils.js` | `/PACE_VERSION\s*=\s*'[^']+'/` | `PACE_VERSION = '${displayVer}'` |
| `.claude-plugin/plugin.json` | JSON `.version` | `cleanVer` |
| `.claude-plugin/marketplace.json` | JSON `.plugins[0].version` | `cleanVer` |
| `REFERENCE.md` L1 | `/^# PACEflow v[\d.]+/m` | `# PACEflow ${displayVer}` |
| `REFERENCE.md` L3 | `/\*\*版本\*\*：v[\d.]+/` | `**版本**：${displayVer}` |
| `README.md` L3 | `/\*\*版本\*\*:\s*v[\d.]+/` | `**版本**: ${displayVer}` |

输出：逐文件打印 `旧值 → 新值` 变更摘要 + CLAUDE.md 手动提醒（散文中的版本号不自动修改）。

支持 `--dry-run` 模式：只显示将要变更的内容，不写入文件。

**T-395 测试验证**：
- `node bump-version.js --dry-run 5.0.2`（当前版本→输出无变更或 same→same）
- `node -c bump-version.js` 语法验证
- `node verify.js` 组 7 版本一致性检查通过

### CHG-20260309-05 S-1 统一 stdin 解析

pace-utils.js 新增 3 个 stdin 解析函数，替换 7 个 hook 中 6 个的重复 stdin 模板代码（pre-compact 无 stdin 解析，跳过）。每个 hook 只改入口 5-8 行，业务逻辑零修改。

**T-390 pace-utils.js 新增 3 函数**：

`parseHookStdin(rawInput)` — 内部 try-catch 的纯函数（永不抛异常，`ok` 是唯一错误通道），JSON.parse + 提取统一结构：
- `ok`: boolean — JSON 解析是否成功（config-guard 降级判断 + todowrite-sync 早退用）
- `toolName`: `raw.tool_name || ''`
- `filePath`: `(raw.tool_input?.file_path || '').replace(/\\\\/g, '/')`（方案 A：统一 normalize，hook 无需关心）
- `oldString`: `raw.tool_input?.old_string || ''`
- `newString`: `raw.tool_input?.new_string || ''`
- `content`: `raw.tool_input?.content || ''`（Write 工具独立字段，不与 newString 合并）
- `toolInput`: `raw.tool_input || {}`（todowrite-sync / config-guard 需完整对象）
- `type`: `raw.type || ''`（session-start 区分 startup/compact）
- `lastMessage`: `raw.last_assistant_message || ''`（stop 交叉验证）
- `raw`: parsed 原始对象（config-guard 需 `raw.tool_input || raw` 降级）

`withStdinParsed(callback)` — 异步 wrapper，替代 4 个 hook 的 3 行流模板（无需 catch，parseHookStdin 内部已 catch）：
```
let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { input += chunk; });
process.stdin.on('end', () => { callback(parseHookStdin(input), input); });
```
- callback 签名 `(stdin, rawInput)` — rawInput 供 config-guard 正则降级
- parse 失败时 `ok: false` + 全空字段 + rawInput，不替 hook 做决策

`parseStdinSync()` — 同步 wrapper（仅 catch readFileSync I/O 异常，parseHookStdin 自身不会抛）：
```
try { return parseHookStdin(fs.readFileSync(0, 'utf8')); }
catch(e) { return parseHookStdin(''); }
```

导出新增 3 个函数到 module.exports。

**T-391 4 个异步 hook stdin 重构**：

pre-tool-use.js（L17-29 → 2 行）：
- 删除 L17-20 流模板 + L22-29 JSON.parse 解析块
- 替换为 `paceUtils.withStdinParsed((stdin) => {`
- 内部 `const { toolName, filePath, oldString, newString } = stdin;`
- filePath 已 normalize（方案 A），L58 `normalizedFile` 只需 `.toLowerCase()` 不再需要 `.replace(/\\/g, '/')`
- 闭合 `});` 保持不变（从 `process.stdin.on('end'` 回调变为 `withStdinParsed` 回调）

post-tool-use.js（L19-34 → 2 行）：
- 同 pre-tool-use 模式
- `const { toolName, filePath, oldString, newString } = stdin;`
- L238 `normFile` 只需 `.toLowerCase()` 不再需要 `.replace(/\\/g, '/')`

todowrite-sync.js（L18-42 → 3 行）：
- 替换为 `paceUtils.withStdinParsed((stdin) => {`
- `const { toolName, toolInput } = stdin;`
- 当前 L40-42 `catch(e) { return; }` → `if (!stdin.ok) return;`（parse 失败早退，等效行为）

config-guard.js（L17-30 → 2 行）：
- 替换为 `paceUtils.withStdinParsed((stdin, rawInput) => {`
- `const configObj = stdin.ok ? (stdin.raw.tool_input || stdin.raw) : null;`（`ok: false` 时 configObj=null 触发正则降级）
- L37 `/"disableAllHooks"\s*:\s*true/.test(input)` → `.test(rawInput)`

**T-392 2 个同步 hook stdin 重构**：

session-start.js（L27-32 → 1 行）：
- 删除 6 行 try-catch readFileSync 块
- 替换为 `const eventType = paceUtils.parseStdinSync().type || 'startup';`

stop.js（L37-43 → 1 行）：
- 删除 7 行 try-catch readFileSync 块
- 替换为 `const lastMessage = paceUtils.parseStdinSync().lastMessage;`

**T-393 测试验证**：
- test-pace-utils.js 新增 `parseHookStdin` section 5-6 case：正常解析（完整字段）/ 空输入→全空+ok:false / 非 JSON→全空+ok:false / 部分字段缺失→默认值 / content 独立于 newString / ok:true 验证
- 语法验证 `for f in paceflow/hooks/*.js; do node -c "$f"; done` 全 8 通过
- E2E 61/61 回归（stdin→stdout/exit code 端到端覆盖解析层）

### HOTFIX-20260309-03 walkthrough 省略行列数修复

T-386 的省略行 `| ... | 消息 | |` 只有 3 列分隔符，但 walkthrough 索引表实际 5 列（日期/完成内容/关联变更/第4列/第5列）。改为 `| ... | 消息 | | | |` 匹配 5 列。

**T-389 修复省略行列数**：
- session-start.js L176 省略行模板从 3 个 `|` 改为 5 个 `|`

### CHG-20260309-04 SessionStart 注入量精简

session-start.js artifact 注入循环（L148-205）增加 3 处截断逻辑，startup/compact 统一无 eventType 分支。目标：降低每次 SessionStart 注入的 token 量。

**T-385 spec.md 截断**：
- L149-159 新增：匹配 `## 技术栈` 标题位置，查找其后下一个 `## ` 标题（`/\n## (?!技术栈)/`），截断到该位置
- 保留：`## 项目概述` + `## 技术栈`（含 `### 工具链` 和 `### 工作流框架` 子段落）
- 省略：`## 编码规范`、`## 目录结构`、`## 依赖列表`

**T-386 walkthrough 索引表截断**：
- L164-178 新增：`/^\| \d{4}-\d{2}-\d{2} \|/gm` 收集所有数据行位置，`lastIndexOf('\n', m.index)` 定位行首
- 数据行 > 10 时：保留表头 2 行 + 省略提示行 + 最近 10 行数据行，切掉中间旧行
- L180-186 详情截断不变（最近 3 个 `## YYYY-MM-DD` 段落）

**T-387 findings 已解决索引跳过**：
- L190-201 新增：`/^- \[(?:x|-)\] .+$/gm` 匹配并 `replace` 删除已解决索引行
- 连续空行清理 `\n{3,}` → `\n\n`，在 `**状态说明**` 行前插入省略计数提示
- L203+ 原有 T-379 详情截断不变（正向匹配 openKeys 保留开放项详情，Corrections 区全量保留）

**T-388 验证**：语法 8/8 + E2E 61/61 + git stash 对比注入量 47,542→20,480 bytes（-57%，432→311 行）

### CHG-20260309-03 Artifact 归档机制增强

**背景**：walkthrough.md 和 findings.md 活跃区无归档保障（task.md 和 impl_plan 已有 PostToolUse+Stop 双层），活跃区无限增长导致 SessionStart 每次注入 700+ 行。三层策略：SessionStart 智能截断（硬保障）+ PostToolUse warnOnce（软提醒）+ Stop warning（末次提醒）。

**修改范围**：session-start.js（3 任务）+ post-tool-use.js（2 任务）+ stop.js（1 任务）+ 验证

---

**T-378 session-start.js walkthrough 智能注入**：
- 当前逻辑：L137-156 通用循环，`readFull()` → 截断 ARCHIVE → 全量输出
- 改动：在 `file === 'walkthrough.md'` 时启用智能截断
- 解析活跃区为"索引表部分"（`## 最近工作` 到首个 `## \d{4}-\d{2}-\d{2}` 之间）和"详情段落"（每个 `## YYYY-MM-DD` 开头的 section）
- 输出：索引表全量 + 仅最近 3 条详情段落（按文件顺序取前 3 个，因为活跃区倒序排列，前 3 即最新）
- 超出部分不输出，添加 `（已省略 N 条旧详情，需要时 Read walkthrough.md）` 提示行

**T-379 session-start.js findings 智能注入**：
- 当前逻辑：同上通用循环全量输出
- 改动：在 `file === 'findings.md'` 时启用智能截断
- 解析活跃区结构：摘要索引区（`## 摘要索引` 下的 `- [状态]` 行）+ 详情区（`### [日期]` 段落）+ Corrections 区（`## Corrections` 段落）
- 索引区：全量输出（所有状态的索引行都保留，供 AI 了解全貌）
- 详情区：只输出 `[ ]` 开放项对应的 `### [日期]` 段落（通过标题前 8 字匹配索引行）；`[x]`/`[-]` 的详情段落跳过
- Corrections 区：全量输出（始终保留）
- 被跳过的详情添加 `（已省略 N 条已解决详情）` 提示行

**T-380 session-start.js impl_plan 智能注入**：
- 当前逻辑：同上通用循环全量输出
- 改动：在 `file === 'implementation_plan.md'` 时启用智能截断
- 解析活跃区：变更索引区（`- [状态] CHG-...` 行）和详情区（`### CHG-...` 段落）
- 索引区：只输出 `[/]` 和 `[ ]` 状态的索引行（进行中+规划中），跳过 `[x]`/`[-]`
- 详情区：只输出与保留索引对应的 `### CHG-ID` 段落
- 被跳过的内容添加 `（已省略 N 条已完成变更）` 提示行

**T-381 post-tool-use.js walkthrough 归档提醒**：
- 触发条件：编辑 `walkthrough.md` 时（`fileName` 匹配）
- 检测：`readActive(cwd, 'walkthrough.md')` 后，用 `/^## \d{4}-\d{2}-\d{2}/gm` 统计详情段落数
- 阈值 > 3 时，warnOnce（flag: `walkthrough-archive-reminded`），提示"活跃区有 N 个详情段落（建议保留最近 3 个），请将旧详情归档到 `<!-- ARCHIVE -->` 下方"
- 复用现有 `warnOnce` helper 和 `.pace/` flag 机制

**T-382 post-tool-use.js findings 归档提醒**：
- 触发条件：编辑 `findings.md` 时
- 检测：`readActive(cwd, 'findings.md')` 后，扫描 `[x]`/`[-]` 索引行，对每行取标题前 8 字，检查活跃区是否有匹配的 `### [日期]` 详情段落
- 存在已解决的详情段落时，warnOnce（flag: `findings-archive-reminded`），提示"findings 活跃区有已解决/已否定的详情段落，请归档到 `<!-- ARCHIVE -->` 下方"
- 复用 `warnOnce` helper

**T-383 stop.js walkthrough/findings 归档检查**：
- walkthrough：`readActive` 后统计 `## YYYY-MM-DD` 详情段落数，> 3 → 追加 warning "walkthrough 活跃区有 N 个详情段落（建议保留最近 3 个）"
- findings：`readActive` 后检测 `[x]`/`[-]` 索引是否有对应活跃区详情段落，有 → 追加 warning "findings 活跃区有已解决详情待归档"
- 两个 warning 累加到现有 `warnings` 数组，参与 `warnings.length > 0 → exit 2` 判定

**T-384 验证**：
- 语法 8/8：`for f in paceflow/hooks/*.js; do node -c "$f"; done`
- E2E：运行 `test-hooks-e2e.js`，确认无回归
- 手动对比：SessionStart 注入前后 token 量（用 `wc -c` 对比 stdout 字节数）
- 验证智能截断：构造含 5+ 详情段落的 walkthrough，确认只注入 3 条

- [x] HOTFIX-20260309-02 compact 格式注入硬编码提取为 FORMAT_SNIPPETS — findings/walkthrough 格式常量化 #change [tasks:: T-377]
- [x] HOTFIX-20260309-01 getProjectName sanitize 空值守卫 — 纯中文目录名过滤后返回空需 fallback #change [tasks:: T-376]
- [x] CHG-20260309-02 Antigravity 审查修复 + 测试补全 + S-1/S-3 规划 — compact 格式注入 + getProjectName sanitize + 3 函数单元测试 + 长期建议 #change [tasks:: T-371~T-375]
- [x] CHG-20260309-01 ticket17 审查修复 — 版本同步 + session-start regex + SKILL 示例 + REFERENCE 函数表 + ts()去重 + readFull 合并 + verify 增强 + 杂项 #change [tasks:: T-362~T-370]
- [x] CHG-20260308-06 paceflow-audit Skill 重构 — 去硬编码预设，改为动态发现式审计 #change [tasks:: T-360~T-361]
- [x] CHG-20260308-05 模板+Skill+Hook 风格统一 — blockquote 提示 + Skill 层修正 + changeStatusHelp + 术语统一 #change [tasks:: T-346~T-359]
- [x] HOTFIX-20260308-01 synced-plans 伴随文件识别 — listUnsyncedPlanFiles 自动视 -design.md 为已同步 + pace-bridge Step 6 修正 #change [tasks:: T-345]
- [x] CHG-20260308-04 检查覆盖增强 + 指引补全 — findings 详情检查 + compact knowledge 注入 + 旧格式 DENY + 快照扩展 + 日期容错 #change [tasks:: T-336~T-344]
- [x] CHG-20260308-03 指引体系增强 — DENY/Stop/HINT 内联格式示例 + SessionStart 格式校验 + 模板注释增强 + Skill 格式速查 #change [tasks:: T-328~T-335]
- [x] CHG-20260308-02 删除 rules/CLAUDE.md — 移除 plugin 中的个人规则模板 #change [tasks:: T-327]
- [x] CHG-20260308-01 ticket16 审查修复 — verify 版本一致性 + E2E 5 测试 + REFERENCE/CLAUDE.md 文档 + Skill 文档锚点 + Hook 代码质量 6 处 + P3 延后 8 处 + 创建阶段详情守门 + native plan 桥接修复 #change [tasks:: T-318~T-326]
- [x] CHG-20260307-04 流程保障增强 — impl_plan 详情 PreToolUse DENY + PostToolUse 持久检查 + Stop 终态兜底 + native plan 同步恢复 #change [tasks:: T-310~T-317]
- [x] CHG-20260307-03 PACEflow v5.0.0 Plugin 化迁移 — plugin.json+hooks.json 新建 + skills 目录重构 + 模板统一 + VAULT_PATH 参数化 + install/verify 适配 #change [tasks:: T-302~T-309]
- [x] CHG-20260307-02 ticket15 审查修复 — H9 HOTFIX 正则 + verify 统计 + 文档同步 6 处 + 代码质量 3 处 #change [tasks:: T-298~T-301]
- [x] CHG-20260307-01 ticket14 审查修复 + synced-plans 桥接状态追踪 — 35 条审查发现(1H+14W+20I) + docs/plans/ 旧文件误触发修复 #change [tasks:: T-290~T-297]
- [x] CHG-20260306-02 paceflow-audit 全面审查 Skill 创建 — Skill 定义 + install/verify SKILL_MAP 同步 #change [tasks:: T-287~T-289]
- [x] CHG-20260306-01 ticket13 审查修复 — getArtifactDir 缓存 + E2E 测试补充 + Skill 文档修正 + 代码简化 #change [tasks:: T-281~T-286]
- [x] CHG-20260305-03 Artifact 排列规则统一 + 详情检查增强 + walkthrough 标题格式 #change [tasks:: T-274~T-280]
- [x] CHG-20260305-02 v4.8.1 全面审查修复（5-reviewer 审查确认 14 项问题） #change [tasks:: T-267~T-273]
- [x] CHG-20260305-01 resolveProjectCwd 改用 CLAUDE_PROJECT_DIR 环境变量 #change [tasks:: T-263~T-266]
- [x] HOTFIX-20260304-02 install.js 补充 pace-bridge skill 映射 #change [tasks:: T-255]
- [x] CHG-20260304-05 Superpowers × PACEflow 融合 — pace-workflow P/A/C/E/V 重写 + pace-bridge auto-APPROVED #change [tasks:: T-256~T-262]
- [x] CHG-20260304-04 Superpowers-PACEflow 桥接 — DENY 精确引导 + TodoWrite DENY 升级 + 桥接 Skill #change [tasks:: T-247~T-254]
- [x] CHG-20260304-03 CWD 漂移修复 — resolveProjectCwd 向上搜索 .pace/ #change [tasks:: T-242~T-246]
- [x] HOTFIX-20260304-01 ticket12 代码审查修复 #change [tasks:: T-240~T-241]
- [x] CHG-20260304-02 ticket12 审查 W+I 级问题修复 #change [tasks:: T-235~T-239]
- [x] CHG-20260304-01 ticket12 审查 C+H 级问题修复 #change [tasks:: T-230~T-234]
- [x] HOTFIX-20260303-01 CHG-20260302-01 代码审查修复 #change [tasks:: T-226~T-229]

### HOTFIX-20260309-02 compact 格式注入硬编码提取为 FORMAT_SNIPPETS

**背景**：T-371 审查发现 session-start.js L86-87 findings/walkthrough 格式为硬编码字符串，未使用 FORMAT_SNIPPETS 常量，格式变更时需手动同步。

**T-377**：pace-utils.js FORMAT_SNIPPETS 新增 2 字段 + session-start.js 引用替换。

### HOTFIX-20260309-01 getProjectName sanitize 空值守卫

**背景**：T-372 审查发现 getProjectName sanitize（`.replace(/[^a-z0-9-]/g, '')`)后纯中文目录名返回空字符串，导致 `path.join(VAULT_PATH, 'projects', '')` 指向 projects 根目录。

**T-376**：L65 sanitize 结果加 `|| 'unknown-project'` fallback，与 L62 空值守卫行为一致。

### CHG-20260309-02 Antigravity 审查修复 + 测试补全 + S-1/S-3 规划

**背景**：Antigravity 审查报告（9.2/10）发现 W-1 getProjectName 特殊字符、3 个函数缺单元测试、S-1/S-3 长期建议。同时 path-tracer 确认 compact 恢复路径缺 findings/walkthrough 格式注入。

**范围**：~80 行改动，3 个文件（session-start.js + pace-utils.js + test-pace-utils.js）+ findings.md 规划记录。

**T-371 compact 格式注入补全**：
- session-start.js L85 后追加 findings/walkthrough/APPROVED/VERIFIED/impl_plan 详情格式提示（~5 行）

**T-372 getProjectName sanitize**：
- pace-utils.js L65 追加 `.replace(/[^a-z0-9-]/g, '')` 过滤特殊字符

**T-373 补单元测试**：
- formatBridgeHint：null 返回 + 正常返回 + synced 过滤（~15 行）
- createLogger：基本写入 + 512KB 轮转 + 换行对齐（~20 行）
- getProjectName 特殊字符：中文 + @# + 混合（~10 行）

**T-374 S-1/S-3 规划**：
- findings.md 记录统一 stdin 解析方向和版本自动化方向

**T-375 验证**：
- 语法 8/8 + 单元 60/60 + E2E 61/61

**完成标记**: [DONE] 2026-03-09T11:16:00+08:00

### CHG-20260309-01 ticket17 审查修复

**背景**：ticket17 全面审查（5-agent 并行 + Phase 2 验证）确认 27 项发现（1C+5H+14W+7I）。本 CHG 修复全部 P0（1C+5H）+ P1（9W）+ P2（4W）共 19 项。

**范围**：~15 文件，涵盖版本同步、regex bug 修复、Skill 文档示例重写、REFERENCE 函数表补全、代码去重/合并、verify.js 增强、杂项修复。

**T-362**：版本号同步 — REFERENCE.md:1,3,643 + README.md:3 + marketplace.json:11 统一到 v5.0.2
**T-363**：session-start.js 三处修复 — H-1 regex `m` flag + W-3 ARCHIVE match 缓存 + W-4 listUnsyncedPlanFiles 去重
**T-364**：change-management SKILL.md 联动示例重写 — H-2 task.md 示例格式 + H-3 findings.md 示例格式匹配模板和 Hook 正则
**T-365**：REFERENCE.md 更新 — H-4 补 3 个导出函数 + W-10 E2E 57→61 + W-11 PreCompact I/O 描述修正
**T-366**：ts() 去重 — W-1 五文件局部 ts() 替换为 paceUtils.ts 导入
**T-367**：pre-tool-use.js readFull 合并 — W-2 impl_plan 3 次 readFull 合并为 1 次共享变量
**T-368**：config-guard + verify.js 增强 — W-5 plugin 路径正则 + W-6 双向 v 前缀处理 + W-7 marketplace.json 版本检查
**T-369**：杂项修复 — W-8 change-record emoji→文本 + W-9 pace-knowledge 外部引用注释 + W-12 模板注释统一 + W-13 CLAUDE.md 版本标注
**T-370**：验证 — 语法 8/8 + 单元 51/51 + E2E 61/61 + verify 4/8 plugin 模式

**完成标记**: [DONE] 2026-03-09T07:17:00+08:00

### CHG-20260308-06 paceflow-audit Skill 重构

**背景**：当前 paceflow-audit SKILL.md（549 行）包含大量硬编码预设：文件数量（"8+1"、"6"、"7 组检查"）、版本号（v5.0.0）、有意设计列表（7 条背景信息 × 5 个 agent）。这些预设有两个问题：(1) 每次变更后需手动维护，(2) agent 被"喂答案"后无法独立发现真实问题（如 verify.js 实际是 8 组检查但 skill 写 7 组，agent 不会报告因为被告知"7 组"）。

**设计原则**：保留审查框架（5 维度分工、严重度标准、Phase 1-2-3 流程、误报防御方法论），去除所有具体事实预设。Agent prompt 改为指导"如何发现"而非"发现什么"。

**范围**：1 文件（`paceflow/skills/paceflow-audit/SKILL.md`），完全重写。

**T-360 重写要点**：
- 审查范围表：移除硬编码数量，改为 Glob 模式描述（`paceflow/hooks/*.js`、`paceflow/skills/*/SKILL.md` 等）
- Agent 文件分配：从指定具体文件名 → 指定目录/模式，agent 自行 Glob 发现
- 背景信息（防止误报）：从列举 7 条具体设计决策 → 单条指令"读取 CLAUDE.md 开发约定和代码注释中的设计意图标注"
- Agent prompt 审查维度：保留（Bug/协议/流程/安全/质量），这些是方法论不是预设
- Phase 2 验证方法：保留（路径追踪/实际 diff/设计意图查证/最小复现）
- Phase 3 报告格式：保留
- 误报防御四大根因：保留（这是跨审计的通用经验）
- 版本号/行号等具体数字：全部移除

**T-361**：验证语法 + 单元 + E2E + verify 通过

### CHG-20260308-05 模板+Skill+Hook 风格统一

**背景**：Explore agent 全面扫描发现模板层 blockquote 提示缺失、Skill 层风格差异（2 Critical + 4 High + 4 Warning）、模板文案与 Hook FORMAT_SNIPPETS 之间 4 个术语不一致。5-agent 深入审查 + 全量验证后确定 14 个任务。

**范围**：~75 行改动，15 文件（5 模板 + 5 Skill + 3 Hook + 2 文档）。模板层 HTML 注释→blockquote 可见提示；Skill 层补 findings 状态表/VERIFIED 位置/APPROVED 位置修正/状态速查/独立状态标注；Hook 层新增 changeStatusHelp 常量 + 术语统一；emoji 移除。

**T-346~T-359**：见实施计划 `docs/plans/2026-03-08-style-unification.md`

### CHG-20260308-04 检查覆盖增强 + 指引补全

**背景**：CHG-20260308-03 完成指引体系增强后，审视发现 3 个遗留缺口：knowledge 注入 compact 不注入、AI 记录 findings 跳过详情无 hook 检测、旧格式可写入 impl_plan。4-agent 并行研究发现 6 个新缺口，选定 Beta 方案：3 原始 findings + 3 高优先新缺口。

**范围**：~103 行改动，6 文件。新增 `findMissingFindingsDetails` 共享函数；post-tool-use H14 + stop 终态双层 findings 详情检查；compact 路径 knowledge L0 注入 + 格式提示；pre-tool-use 旧格式 DENY；pre-compact 快照扩展 findings/walkthrough；walkthrough 日期前导零容错。

**T-336~T-344**：见实施计划 `docs/plans/2026-03-08-coverage-enhancement.md`

### CHG-20260308-03 指引体系增强

**背景**：webot 项目 30 分钟内被 pre-tool-use.js E 阶段 DENY 连续拦截 8 次，AI 始终无法自愈。根因：DENY 消息"只说不教"（10/11 无格式示例）+ 模板注入一次性 + Skill 链路断裂（格式分散 3-4 个 Skill）。详见 findings.md 条目。

**目标**：三层指引体系优化——L1 确定性强制（不变）+ L2 上下文引导（本次核心增强）+ L3 参考规范（补链）。~220 行修改，0 新文件。

**P0：DENY/Stop/HINT 消息内联格式示例**

**T-328 pace-utils.js — FORMAT_SNIPPETS 硬编码常量**：
- 新增 `FORMAT_SNIPPETS` 对象，包含 task.md 任务格式、impl_plan 索引格式、impl_plan 详情格式、APPROVED/VERIFIED 位置、checkbox 状态说明
- 硬编码（确定性最高、零 I/O、格式极少变更），不从模板动态读取
- 导出供 pre-tool-use/stop/post-tool-use 引用

**T-329 pre-tool-use.js — 10 DENY 消息内联格式示例**：
- 强信号 DENY（L232-236）：追加 task.md 任务条目格式 + `<!-- APPROVED -->` 位置
- C 阶段未批准 DENY（L285）：追加 `<!-- APPROVED -->` 放置位置示例
- E 阶段无 `[/]` DENY（L293-303）：追加 impl_plan 索引 checkbox 格式 + 明确说明 `hook 检测格式为行首 "- [/] "（Markdown checkbox），非表格格式无法识别`
- impl_plan 详情守门 DENY（L142-165, L167-191）：追加详情段落模板（`### CHG-ID 标题` + 描述 + 任务列表）
- Write 覆盖保护 DENY（L87-102）：追加 `请使用 Edit 工具修改已有文件`
- Native plan 桥接 DENY（L194-203）：追加 `详见 paceflow:pace-bridge skill`
- Superpowers 桥接 DENY：保持现有 pace-bridge 引用（已有）
- 所有 DENY 消息末尾统一追加 `格式参考：paceflow:artifact-management skill`

**T-330 stop.js — 14 warning 增强 + stderr 编号列表 + 降级递进**：
- stderr 输出从分号拼接改为 `[1]...\n[2]...` 编号列表（可读性）
- 14 个 warning 消息追加具体修复示例（如"task.md 有未归档 [x] 项"→ 追加归档操作格式）
- 降级递进式消息：第 1 次正常消息，第 2 次追加修复 hint，第 3 次追加降级警告
- impl_plan 详情终态检查消息增强：列出缺失的 CHG-ID + 详情段落格式

**T-331 post-tool-use.js — 13 HINT 消息增强**：
- H3 归档提醒：追加归档操作步骤（Edit 移到 `<!-- ARCHIVE -->` 下方）
- H9 CHG 完成检测：追加 impl_plan 索引状态更新格式
- H10 impl_plan 归档提醒：追加归档位置说明
- H13v2 详情缺失：追加详情段落模板
- 其余 HINT 逐条审查并补充可操作的修复指引

**P1：模板和 SessionStart 格式校验**

**T-332 templates — impl_plan + task.md 模板注释优化**：
- `hooks/templates/artifact-implementation_plan.md` 活跃区：补充索引条目格式示例 + checkbox 状态说明 + 详情段落模板 + 禁止项（禁止表格/emoji 格式）
- `hooks/templates/artifact-task.md` 活跃区：补充任务条目格式示例（`- [ ] T-NNN 标题`）+ CHG 分组格式 + APPROVED/VERIFIED 位置 + 禁止项
- `skills/change-management/templates/change-implementation_plan.md`：同步更新

**T-333 session-start.js — 格式合规检查模块**：
- 新增格式合规检查函数（注入活跃区内容后执行）
- 检测 1：impl_plan 旧表格+emoji 格式（`|` 表格行 或 `✅`/`❌`/`📋` emoji）→ 警告 + 正确格式
- 检测 2：双 `<!-- ARCHIVE -->` 标记 → 警告 + 修复指引
- 检测 3：task.md 任务条目非 checkbox 格式 → 警告 + 正确格式
- 输出到 additionalContext（不阻塞，仅引导）

**P2：Skill 格式速查整合**

**T-334 artifact-management SKILL.md — 格式速查 section**：
- 新增"## 格式速查"section，集中展示：
  - task.md 完整格式（任务条目 + CHG 分组 + APPROVED/VERIFIED 位置 + 状态标记）
  - impl_plan 完整格式（索引条目 + 详情段落 + 归档结构）
  - 常见错误（表格 vs checkbox、emoji vs 状态标记）
- 使 DENY 消息的 `格式参考：paceflow:artifact-management skill` 有明确目标

**T-335 验证 + 生产同步**：
- 语法验证：`for f in paceflow/hooks/*.js; do node -c "$f"; done`
- 单元测试：`node paceflow/tests/test-pace-utils.js`（含 FORMAT_SNIPPETS 导出检查）
- E2E 测试：`node paceflow/tests/test-hooks-e2e.js`（现有 57 测试不回归）
- verify.js：`node paceflow/verify.js`
- 手动验证：模拟 DENY 场景确认消息包含格式示例

### CHG-20260308-02 删除 rules/CLAUDE.md ✅

Plugin 中 `rules/CLAUDE.md` 包含用户个人规则（硬编码路径、偏好），不应随 plugin 分发。删除目录 + 清理 install.js/README.md/REFERENCE.md/CLAUDE.md 4 处引用。

### CHG-20260308-01 ticket16 审查修复 ✅

ticket16 全面审查确认 0C+8H+12W+8I，全部修复。

**T-318 verify.js 版本一致性 + 配置一致性**：
- `verify.js` 组 7 `checkPlugin()`：增加 `plugin.json` version 与 `pace-utils.js` PACE_VERSION 比较（strip `v` 前缀后 ===）
- `verify.js` 新增组 8：hooks.json vs settings-hooks-excerpt.json 事件类型/matcher/脚本名一致性检查

**T-319 E2E 测试补充 5 个关键场景**：
- `test-hooks-e2e.js` #53：stop.js V 阶段 — 有 `[x]` 无 `<!-- VERIFIED -->` → exit 2
- `test-hooks-e2e.js` #54：stop.js walkthrough — 无今日日期 → warnings 含提醒
- `test-hooks-e2e.js` #55：pre-tool-use E 阶段 — impl_plan 无 `[/]` → DENY
- `test-hooks-e2e.js` #56：T-325 创建阶段 `[ ]` 索引无详情 → DENY
- `test-hooks-e2e.js` #57：T-325 创建阶段 `[ ]` 索引有详情 → 放行

**T-320 REFERENCE.md + CLAUDE.md 文档修正**（5 项中 4 项已在先前 CHG 修复，本次实际 1 处）：
- `REFERENCE.md:719` 测试数量：55→57（本次实际修复）

**T-321 模板同步 + Skill 文档修正**（5 项中 3 个已在先前 CHG 修复，本次实际 2 处）：
- `pace-workflow/SKILL.md:137`：移除失效锚点 `#并行任务标记-p`
- `change-management/SKILL.md:51`：移除失效锚点 `#变更状态-change-status`

**T-322 Hook 代码质量修复 6 处**：
- `pace-utils.js:334`：日志轮转截断后对齐到换行符（防 UTF-8 多字节截断）
- `pre-tool-use.js:71,91,109`：移除内层 `const fileName` 重复声明，统一用外层变量
- `install.js:84-88`：`dateStamp()` 结果缓存到局部变量
- `config-guard.js:55`：PACE hook 删除检测正则精确化
- `session-start.js:80`：`unlinkSync(snapFile)` 加独立 try-catch
- `post-tool-use.js:39-44`：`warnOnce` 添加 `mkdirSync(PACE_RUNTIME, { recursive: true })`

**T-323 P3 延后项批量处理**：
- `pace-utils.js`：`hasUnsyncedPlanFiles` 委托 `listUnsyncedPlanFiles().length > 0`
- `pace-utils.js`：新增 `ts()` 导出，`pre-tool-use.js`/`post-tool-use.js` 改为 `require` 引用
- `pace-utils.js:297`：`scanRelatedNotes` frontmatter 正则增加 BOM 处理
- `pre-compact.js:51`：HOME/USERPROFILE 都不存在时跳过 nativePlans 检测

**T-325 pre-tool-use.js 创建阶段详情守门**：
- `pre-tool-use.js`：在 impl_plan Edit 检查区增加第四层——`new_string` 含新 `[ ]`/`[/]` CHG/HOTFIX 索引条目时，检查当前 impl_plan 全文是否已有对应 `### CHG-ID` 详情段落，若无则 DENY "请同时写入 ### CHG-ID 详情段落"
- `test-hooks-e2e.js` #56：添加 `[ ]` 索引无详情 → DENY + #57：添加 `[ ]` 索引有详情 → 放行

**T-326 native plan 桥接修复 2 处**（研究团队发现的严重漏洞）：
- `pre-compact.js`：扫描到 `~/.claude/plans/` 最近文件后，自动写入 `.pace/current-native-plan`（选最近修改的文件）。消除对 AI 自觉的依赖，让 compact 后 pre-tool-use DENY 能自动生效
- `session-start.js`：startup 路径（非 compact）也检测 `.pace/current-native-plan`，存在时注入提醒。修复跨会话盲区（当前仅 compact 分支检测）

**T-324 验证**：语法 8/8 + 单元 41/41 + E2E 57/57 + verify 4/8（plugin 模式预期）

### CHG-20260307-04 流程保障增强 ✅

impl_plan 详情完整性从一次性 PostToolUse 提醒升级为三层保障 + native plan compact 恢复。

1. **pace-utils.js** — 新增 `findMissingImplDetails(planFull)` 共享函数（扫描全文 `[x]` 索引 vs `### CHG-ID` 详情段落）+ `getNativePlanPath(cwd)` 读取 `.pace/current-native-plan` + `SESSION_SCOPED_FLAGS` 移除 `impl-detail-reminded`（不再需要一次性 flag）
2. **pre-tool-use.js** — v5.0.1 impl_plan 详情守门：Edit `implementation_plan.md` 将 `[/]→[x]` 时，检查是否有 `### CHG-ID` 详情段落，缺失则 DENY + native plan 桥接引导：`.pace/current-native-plan` 存在且 task.md 无活跃任务时 DENY 写代码
3. **post-tool-use.js** — H13v2 持久化检查：每次编辑 `implementation_plan.md` 后触发（替代一次性 `warnOnce`），调用 `findMissingImplDetails(readFull(...))` 扫描全文
4. **stop.js** — impl_plan 详情终态检查：`planActive` 存在时 `readFull` 全文扫描已完成 CHG 缺失详情 → exit 2 阻止退出
5. **pre-compact.js** — 捕获 `~/.claude/plans/` 最近 60 分钟 `.md` 文件路径到快照 `snapshot.nativePlans`
6. **session-start.js** — compact 恢复注入 native plan 提示（快照 `nativePlans` + `.pace/current-native-plan` 两路径）
7. **E2E 测试** — 4 新测试（#49 DENY 无详情 / #50 ALLOW 有详情 / #51 Stop block / #52 H13v2 持久警告）+ 修复 #43 适配 H13v2

### CHG-20260307-03 PACEflow v5.0.0 Plugin 化迁移 ✅

完整 Plugin 化迁移，实现一条命令安装（`claude plugin install paceflow@paceaitian-paceflow`）。

1. **Plugin 元数据** — 新建 `.claude-plugin/plugin.json`（name/version/author）+ `hooks/hooks.json`（8 hook 自动注册，替代 settings.json 手动配置）+ `.claude-plugin/marketplace.json`（GitHub marketplace 分发）
2. **Skills 目录重构** — 6 个扁平 `.md` → `name/SKILL.md` 目录结构（Plugin 标准自动发现格式）
3. **模板统一** — `skills/templates/` 5 个冗余 artifact 模板删除，2 个 change 模板迁入 `skills/change-management/templates/`，`hooks/templates/` 为唯一源
4. **VAULT_PATH 参数化** — `pace-utils.js` 移除硬编码 fallback（`|| 'C:/Users/...'` → `|| ''`），改用 `PACE_VAULT_PATH` 环境变量
5. **install.js 改造** — 新增 `--plugin` 模式（复制到 plugin 缓存）+ `--migrate` 模式（清理旧 settings.json hooks + 旧 skills 目录）+ `cleanupOldTemplates()` 清理生产环境旧模板
6. **verify.js 适配** — 新增第 7 组 Plugin 结构检查（plugin.json + hooks.json + skills 目录结构）+ SKILL_DIRS 替换 SKILL_MAP
7. **Skill 内容微调** — 6 个 SKILL.md 模板引用路径更新（`skills/templates/` → `hooks/templates/`）+ paceflow-audit Agent4 路径修正
8. **文档更新** — README.md（Plugin 安装为主 + 手动安装折叠）+ REFERENCE.md（架构树/版本/常量/install/verify 7 处更新）+ CLAUDE.md（架构树已正确）
9. **部署** — `install --force` 4 更新 + 5 旧模板清理 → `--migrate` 清理 legacy → `marketplace add` + `plugin install` 一条命令安装

### CHG-20260307-02 ticket15 审查修复 ✅

5-agent 并行审查 54 发现 → Phase 2 验证 → 14 确认修复。

1. **post-tool-use.js** — H9 HOTFIX 正则 4 处（`CHG-` → `(?:CHG|HOTFIX)-`）
2. **verify.js** — `groupStatus` 统计重构（分离 pass/warn/fail 计数）
3. **todowrite-sync.js** — `pendingTasks` → `activeTasks` 重命名（语义准确）
4. **install.js** — 备份文件名加时间戳（避免覆盖）
5. **pace-utils.js** — `scanRelatedNotes` 引号兼容（单引号/双引号 frontmatter）
6. **文档** — CLAUDE.md skill 5→6 + REFERENCE.md E2E 43→48 + paceflow-audit "5-6"→"6" + artifact-management task.md 消歧 + impl_plan 模板归档标题

### CHG-20260307-01 ticket14 审查修复 + synced-plans 桥接状态追踪 ✅

ticket14 5-agent 审查报告 35 条发现（1H+14W+20I）修复 + docs/plans/ 旧文件误触发根因修复。

1. **pace-utils.js** — 新增 `hasUnsyncedPlanFiles()`/`listUnsyncedPlanFiles()`/`formatBridgeHint()` 三函数（synced-plans 区分已同步文件）+ `SESSION_SCOPED_FLAGS` 常量集中化 + `listPlanFiles` TOCTOU 修复（try-catch stat）+ `countByStatus` 正则预编译 + `createLogger` 内联化 + `getProjectName` toLocaleLowerCase
2. **stop.js + post-tool-use.js** — H-1 `isPaceProject` guard（`.pace/disabled` → exit 0 / 无输出）+ `PACE_VERSION` import 移除 + `warnOnce` helper 函数 + config-guard JSON 冗余移除
3. **pre-tool-use.js** — synced-plans call-site（`hasUnsyncedPlanFiles` 替换 `hasPlanFiles`）+ `formatBridgeHint` 集中化 + DENY 精确化（全 done → 归档提示 vs 无任务 → P-A-C 流程）+ 注释修正
4. **session-start.js + todowrite-sync.js** — synced-plans call-site + `SESSION_SCOPED_FLAGS` 替换硬编码数组 + `formatBridgeHint` 替换内联消息
5. **Skill 文档** — pace-bridge Step 6 synced-plans 写入 + artifact-management task.md Write 保护 + change-management HOTFIX-ID 格式 + version frontmatter
6. **REFERENCE.md** — 10 处修正（架构树 6 skill + SessionStart flag + PostToolUse H13 + 运行时文件 + 常量表 + 函数表 + verify 6 组 + E2E 48+）
7. **README.md** — 4 处修正（架构树 6 skill + SessionStart stdin + TodoWrite DENY + synced-plans + 版本历史倒序）
8. **测试** — 单元 +4（hasUnsyncedPlanFiles 4 场景）+ E2E +5（synced-plans 2 + H-1 guard 2 + DENY 精确化 1），共 36/36 + 48/48

### CHG-20260305-03 Artifact 排列规则统一 + 详情检查增强 + walkthrough 标题格式 ✅

三类改进：排列规则文档化 + hook 详情检查增强 + walkthrough 标题可读性 + verify.js 第 6 组 + 数据迁移。

1. **artifact-management.md** — 补排列规则定义（索引/详情/归档均 descending）+ 修正 change-management 引用路径
2. **walkthrough 模板**（hooks/templates + skills/templates 两处同步）— `## 上一次详情` → `## YYYY-MM-DD 摘要` 格式
3. **stop.js** — walkthrough 检查增强：索引表日期识别（`\d{4}-\d{2}-\d{2}` 正则）+ 有索引无详情分层提醒（无 `##` 标题 → 严重 / 有标题但缺当天 → 轻度）
4. **post-tool-use.js** — H13 impl_plan 详情缺失检测（索引 `[x]`/`[-]` 但 ARCHIVE 无对应 `### CHG-` 标题 → HINT）+ H10 HOTFIX 正则扩展（`/^- \[[x\-]\] (?:CHG|HOTFIX)-/`）+ readFull 导入
5. **session-start.js** — 新增 `impl-detail-reminded` flag 清理
6. **verify.js** — 新增第 6 组 Skill 文件一致性检查（SKILL_MAP 5 项，源码 vs 生产 SKILL.md 字节比较）
7. **数据迁移** — impl_plan 索引 11 条倒序 + findings 索引 30 条倒序 + walkthrough 活跃区 10 个详情标题改写

`getProjectName(cwd)` 在 CWD 漂移到子目录时返回错误项目名，导致 vault 创建幽灵项目。

1. **pace-utils.js** — 新增 `resolveProjectCwd()` 函数，从 `process.cwd()` 向上搜索 `.pace/` 目录（最多 5 层），fallback 到 `process.cwd()`
2. **7 个 hook** — `const cwd = process.cwd()` 替换为 `paceUtils.resolveProjectCwd ? paceUtils.resolveProjectCwd() : process.cwd()`（fallback 保证生产环境兼容）
3. **测试** — 单元 3 个（当前目录/子目录/无 .pace）+ E2E 2 个（stop.js/session-start.js CWD 漂移场景）
4. **验证** — 语法 8/8、单元 29/29、E2E 37/37、verify 5/5、install 8 更新

### HOTFIX-20260308-01 synced-plans 伴随文件识别

**背景**：listUnsyncedPlanFiles 未识别 `-design.md` 等伴随文件为已同步，导致误触发桥接提醒。

**T-345 主要改动**：
- listUnsyncedPlanFiles 自动视 `-design.md` 为已同步
- pace-bridge Step 6 修正

### CHG-20260306-02 paceflow-audit 全面审查 Skill 创建

**背景**：项目缺少标准化的全面审查流程，需要创建 5-agent 并行审查框架。

**T-287~T-289 主要改动**：
- 新建 paceflow-audit SKILL.md（5-agent 并行审查框架 + Phase 2 C/H 验证筛选 + Phase 3 去重分级报告 + 误报防御四大根因）
- install.js/verify.js SKILL_MAP 同步 6 项

### CHG-20260306-01 ticket13 审查修复

**背景**：ticket13 审查（5-agent 审计 26 发现中 7 确认修复）暴露 getArtifactDir 性能问题和 Skill 文档偏差。

**T-281~T-286 主要改动**：
- pace-utils.js getArtifactDir 模块级缓存（消除 77 次冗余 existsSync）
- post-tool-use.js 合并重复文件读取（impl_plan 3→1 次、findings 2→1 次）
- E2E 3 新测试（H9/H10/H13）
- Skill 文档修正 + 7 hook 14 处 fallback 死代码移除

### CHG-20260305-02 v4.8.1 全面审查修复

**背景**：5-reviewer 并行审查发现 26 项问题，验证后 14 项确认修复。

**T-267~T-273 主要改动**：
- todowrite-sync.js isWriteOp 添加 TaskUpdate + flag 写入后移
- README.md/REFERENCE.md 版本号 v4.8.1 + Skills 数量 + pace-bridge 手动安装
- pace-workflow.md worktree 描述改为 CLAUDE_PROJECT_DIR
- install.js 新增 cleanupOldTemplates() 函数（4 类清理）

### CHG-20260305-01 resolveProjectCwd 改用 CLAUDE_PROJECT_DIR 环境变量

**背景**：发现 hook stdin 含 cwd 字段 + CLAUDE_PROJECT_DIR 环境变量不随 cd 漂移，可替换向上搜索 .pace/ 的复杂方案。

**T-263~T-266 主要改动**：
- pace-utils.js resolveProjectCwd() 从向上搜索 .pace/（5 行循环）改为 1 行 env var 读取
- 删除 paceflow/.pace/ 污染目录
- 回退 DIAG 诊断行

### HOTFIX-20260304-02 install.js 补充 pace-bridge skill 映射

**背景**：install.js SKILL_MAP 遗漏 pace-bridge，导致该 Skill 不会被安装到生产环境。

**T-255 主要改动**：
- install.js SKILL_MAP 补充 pace-bridge 映射项

### CHG-20260304-05 Superpowers x PACEflow 融合

**背景**：pace-workflow SKILL.md P/A/C/E/V 五阶段需要与 Superpowers 流程（brainstorm→plan→execute）深度融合。

**T-256~T-262 主要改动**：
- pace-workflow.md P/A/C/E/V 五阶段全部重写（P=brainstorming 6 步、A=invoke pace-bridge、C=auto-APPROVED、E=worktree+TDD、V=verification-before-completion）
- pace-bridge 增强 auto-APPROVED 说明 + 转换摘要格式

### CHG-20260304-04 Superpowers-PACEflow 桥接

**背景**：Superpowers 用户使用 Claude Code plan mode 时，产生的 native plan 与 PACEflow artifacts 脱节，需要三层拦截引导桥接。

**T-247~T-254 主要改动**：
- SessionStart 桥接提醒 + TodoWrite DENY 升级 + PreToolUse DENY 精确桥接步骤
- 新建 pace-bridge SKILL.md
- pace-utils.js 新增 listPlanFiles 函数
- E2E 40/40 + 单元 32/32

### CHG-20260304-03 CWD 漂移修复

**背景**：getProjectName(cwd) 在 CWD 漂移到子目录时返回错误项目名，导致 vault 创建幽灵项目。

**T-242~T-246 主要改动**：
- pace-utils.js 新增 resolveProjectCwd() 向上搜索 .pace/ 目录（最多 5 层）
- 7 个 hook process.cwd() 替换为 resolveProjectCwd()
- 单元 3 个 + E2E 2 个漂移测试

### CHG-20260304-02 ticket12 审查 W+I 级问题修复

**背景**：ticket12 全面审查 43 项中 W+I 级问题修复。

**T-235~T-239 主要改动**：
- 4 Skill 文档 vault 存储/版本/交叉引用更新
- REFERENCE.md/README.md v4.8.0 同步
- scanRelatedNotes 4 单元测试

### CHG-20260304-01 ticket12 审查 C+H 级问题修复

**背景**：ticket12 全面审查 43 项（3C+10H+18W+12I）中 C+H 级关键问题修复。

**T-230~T-234 主要改动**：
- 8 个 hook 日志轮转统一 createLogger
- session-start 顶层 try-catch + stop.js 空 walkthrough 防御
- pre-tool-use isPaceProject 缓存 + readActive 替换 + 变量重命名
- config-guard JSON.parse 替代正则 + install.js 备份+错误处理

### HOTFIX-20260304-01 ticket12 代码审查修复 ✅

5-agent 并行代码审查发现 2 个确认 bug：

1. **pre-tool-use.js:205** — I-9 变量重命名不完整，`displayCount2`（未定义）应为 `displayCountForHint`，导致第三级软提醒日志 ReferenceError
2. **pre-compact.js:13** — W-8 日志轮转统一遗漏，未使用 `createLogger`，是唯一未统一的 hook

### HOTFIX-20260303-01 CHG-20260302-01 代码审查修复 ✅

- **H-1** post-tool-use.js:182-184 路径比较添加 `.toLowerCase()`（Windows 大小写不敏感，pre-tool-use.js 已有同类修复）
- **H-2** post-tool-use.js:188 spawn 参数从 `` `file=${relPath}` `` 改为 `--file relPath`（空格安全）
- **W-1** post-tool-use.js:178,197 注释澄清 flag 写入语义（无论 CLI 成功与否，每会话一次）
- **W-2** test-hooks-e2e.js 新增测试 #35（artifact 在 vault 外不触发 CLI refresh）
- **I-1** test-hooks-e2e.js 章节编号 9→10
- **I-2** pace-knowledge.md Fallback 策略描述修正（hook 层 H12 确实用了 CLI）
- 验证：语法 8/8 + E2E 35/35 + 单元 22/22 + verify 5/5
- [x] CHG-20260302-01 Obsidian CLI 集成 — MCP Server 配置 + Skill 增强 + 索引刷新 #change [tasks:: T-219~T-225]
- [x] CHG-20260301-01 PACEflow v4.8.0 — Artifact 存储迁移到 Obsidian Vault #change [tasks:: T-210~T-218]
- [x] CHG-20260228-03 E2E 测试 VAULT_PATH 隔离 #change [tasks:: T-209]
- [x] CHG-20260228-02 PACEflow 基础设施解耦 + 模板格式引导 #change [tasks:: T-204~T-208]
- [x] CHG-20260228-01 v4.7.0 全系统审查修复 #change [tasks:: T-192~T-203]
- [x] CHG-20260227-02 Corrections 双写机制：findings.md → knowledge/ 自动提醒 #change [tasks:: T-187~T-191]
- [x] CHG-20260227-01 PostToolUse impl_plan 详情归档提醒 #change [tasks:: T-184~T-186]
- [x] CHG-20260226-02 PACEflow v4.7.0 — Agent Teams 兼容性（Direction C） #change [tasks:: T-178~T-183]
- [x] CHG-20260226-01 Findings 状态流转：Skill 补链 + Hook 实时检查 + SessionStart 过期提醒 #change [tasks:: T-173~T-177]
- [x] CHG-20260225-09 Hook E2E 测试脚本 #change [tasks:: T-170~T-172]
- [x] CHG-20260225-08 V 阶段收尾：verify.js 更新 + 生产同步 + walkthrough #change [tasks:: T-167~T-169]
- [-] CHG-20260225-07 PACEflow 批次 4 — 评估与打包 #change [tasks:: T-165~T-166]
- [x] CHG-20260225-06 PACEflow v4.6.0 批次 3 — 扩展 hook #change [tasks:: T-161~T-164]
- [x] CHG-20260225-05 PACEflow v4.5.0 批次 2 — 核心 hook 改进 #change [tasks:: T-157~T-160]
- [x] CHG-20260225-04 PACEflow v4.5+ 批次 1 — 基础设施 #change [tasks:: T-153~T-156]
- [x] CHG-20260225-03 PreToolUse impl_plan [/] 检查 + pace-workflow 补充 v4.4.3 #change [tasks:: T-149~T-152]
- [x] CHG-20260225-02 PostToolUse 优化：去重+降频+自签检测 v4.4.2 #change [tasks:: T-148]
- [x] CHG-20260225-01 pace-knowledge skill + PreToolUse 模板提醒 #change [tasks:: T-147]
- [x] CHG-20260224-04 Artifact 索引格式迁移 — 表格 → checkbox #change [tasks:: T-142~T-146]
- [-] CHG-20260224-03 Obsidian 知识中枢第三阶段 — vault-sync #change [tasks:: T-139~T-141]
- [x] CHG-20260224-02 Obsidian 知识中枢第二阶段 #change [tasks:: T-134~T-138]
- [x] CHG-20260214-08 系统审视改进 v4.4.0 #change [tasks:: T-104~T-108]
- [x] CHG-20260214-07 3-Agent 审查修复 v4.3.9 #change [tasks:: T-100~T-102]
- [x] CHG-20260214-06 Stop hook TodoWrite 清理提醒 #change [tasks:: T-098]
- [x] CHG-20260214-05 ticket6 审查修复 v4.3.8 #change [tasks:: T-089~T-097]
- [x] CHG-20260214-04 PACE-TodoWrite 同步方案 A+B+C+D #change [tasks:: T-082~T-088]
- [x] CHG-20260214-03 ticket5 空项目激活方案 v4.3.5 #change [tasks:: T-075~T-081]
- [x] CHG-20260214-01 W6 Tasks API 同步提醒 #change [tasks:: T-066~T-067]
- [x] CHG-20260213-04 W5 findings 降级 + I4 .pace/ 目录 #change [tasks:: T-063~T-065]
- [x] CHG-20260213-03 ticket4 审查修复 #change [tasks:: T-055~T-062]
- [x] CHG-20260213-02 v4.3.3 全面审查修复 #change [tasks:: T-040~T-054]
- [x] CHG-20260215-03 V 阶段强制 + Write artifact 保护 #change [tasks:: T-036~T-039]
- [x] CHG-20260215-02 C 阶段 hook 强制检查 #change [tasks:: T-033~T-035]
- [x] CHG-20260215-01 v4.3.1 审查修复 + DRY 重构 #change [tasks:: T-024~T-032]
- [x] CHG-20260214-02 PreToolUse v4.3.1 修复 #change [tasks:: T-019~T-023]
- [x] CHG-20260214-01 PACE + Superpowers 空项目集成 #change [tasks:: T-010~T-018]
- [x] CHG-20260213-01 PACE 三层架构补全 #change [tasks:: T-006~T-009]
- [x] CHG-20260212-02 Hooks V 阶段覆盖扩展 #change [tasks:: T-004~T-005]
- [x] CHG-20260212-01 Hooks 功能测试 #change [tasks:: T-001~T-003]
- [x] CHG-20260211-01 Hooks 配置 #change [tasks:: T-000]

**状态说明**: `[ ]` 规划中 | `[/]` 进行中 | `[x]` 完成 | `[-]` 废弃 | `[!]` 暂停

---

## 活跃变更详情

### CHG-20260307-01: ticket14 审查修复 + synced-plans 桥接状态追踪

**状态**: [/] 进行中
**来源**: ticket14.md（5-agent 审查 35 条发现：1H+14W+20I）+ findings.md（docs/plans/ 旧文件误触发）
**范围**: 31 项修复 + 4 项跳过（W-code-5 ROI 不高 / I-opt-2~3 保持独立性 / I-style-3 已在 ticket13 修复）

---

#### 修复项汇总

**P0 必修（4 项）**：
- H-1: stop.js + post-tool-use.js 加 `isPaceProject()` 前置检查（.pace/disabled 豁免缺口）
- W-dry-1: 4 个 hook 移除未使用的 PACE_VERSION 导入
- W-code-1: readActive/readFull TOCTOU 竞态修复（existsSync+readFileSync → try readFileSync）
- W-dry-2: 提取 `formatBridgeHint()` 到 pace-utils（4 处重复 → 1 函数）

**P1 建议修复（9 项）**：
- W-code-2: createLogger 日志轮转字节/字符统一
- W-code-3: getProjectName 盘符根路径守卫
- W-code-4: SESSION_SCOPED_FLAGS 常量集中管理
- W-code-6: pre-tool-use.js 注释修正
- W-dry-3: hasPlanFiles/listPlanFiles 双重 readdirSync 消除
- W-dry-4: warnOnce() 辅助函数提取（post-tool-use 4 处去重）
- W-flow-1: DENY 消息语义精确化（全 [x]/[-] 时提示归档而非 P-A-C）
- W-skill-1~3: 3 个 Skill 文档修正

**P2 文档同步（15 项）**：
- I-doc-1~13: REFERENCE.md + README.md 全面更新
- I-opt-1: countByStatus 正则预编译
- I-opt-4: stop.js 无意义别名删除
- I-style-1: config-guard JSON.stringify 冗余
- I-style-2: change-management version frontmatter

**synced-plans 修复（findings 活跃问题）**：
- pace-utils.js: hasUnsyncedPlanFiles() + listUnsyncedPlanFiles()
- pre-tool-use.js: hasPlanFiles → hasUnsyncedPlanFiles（行 173）
- session-start.js: hasPlanFiles → hasUnsyncedPlanFiles（行 130）+ listPlanFiles → listUnsyncedPlanFiles（行 133）
- pace-bridge.md: Step 6 写入 .pace/synced-plans

**跳过项（4 项）**：
- [-] W-code-5: config-guard 删除检测正则（ROI 不高，仅 advisory）
- [-] I-opt-2: Hook 初始化样板合并（保持独立可调试性）
- [-] I-opt-3: install/verify 共享 SKILL_MAP（独立 CLI 工具，共享增加耦合）
- [-] I-style-3: Mermaid label（已在 ticket13 CHG-20260306-01 修复）

**不修改（5 项有意设计）**：
- `[!]` 计入 hasApproval — 有意设计
- artifact 重定向/Write 保护不走 denyOrHint() — 安全约束不应降级
- compact 后降级状态被重置 — 软重启语义
- 同名项目 vault 冲突 — 已知限制
- vault 不可达时静默失败 — 符合 exit 0 约定

---

#### 任务分解

**T-290: pace-utils.js 集中修复**
修改点：
1. synced-plans: 新增 `hasUnsyncedPlanFiles(cwd)` + `listUnsyncedPlanFiles(cwd)`
2. W-code-1: readActive/readFull 改为 try readFileSync catch return null（消除 TOCTOU + 减少 stat syscall）
3. W-code-2: createLogger 日志轮转统一用 `Buffer.byteLength` 截断
4. W-code-3: getProjectName 增加 `/^[A-Z]:\\\\?$/i` 守卫返回 `'unknown-project'`
5. W-code-4: 导出 `SESSION_SCOPED_FLAGS` 常量数组
6. W-dry-2: 新增 `formatBridgeHint(cwd, artDir)` 函数（从 4 处调用点提取）
7. W-dry-3: `hasPlanFiles(cwd)` 改为复用 `listPlanFiles(cwd).length > 0`
8. I-opt-1: countByStatus 正则预编译为模块级常量
9. exports 更新

**T-291: stop.js + post-tool-use.js 修复**
修改点：
1. H-1: stop.js 逻辑开头加 `if (!isPaceProject(cwd)) process.exit(0)`
2. H-1: post-tool-use.js stdin.on('end') 内加 `if (!isPaceProject(cwd)) return`
3. W-dry-1: 两个 hook 移除 PACE_VERSION 导入
4. W-dry-4: post-tool-use.js 提取 `warnOnce(runtimeDir, flagName, warnings, message)` 辅助函数
5. I-opt-4: stop.js 移除 `const artifactFiles = ARTIFACT_FILES` 无意义别名
6. I-style-1: config-guard.js JSON.stringify 再 JSON.parse 冗余简化

**T-292: pre-tool-use.js 修复**
修改点：
1. synced-plans: 行 173 `hasPlanFiles(cwd)` → `hasUnsyncedPlanFiles(cwd)`
2. W-dry-1: 移除 PACE_VERSION 导入
3. W-dry-2: 桥接提示调用点替换为 `formatBridgeHint(cwd, artDir)`
4. W-flow-1: 全 [x]/[-] 时 DENY 消息改为"请先归档已完成任务，再定义新任务"
5. W-code-6: 行 217 注释修正为"当前无代码文件，不触发"

**T-293: session-start.js + todowrite-sync.js 修复**
修改点：
1. synced-plans: session-start 行 130 `hasPlanFiles(cwd)` → `hasUnsyncedPlanFiles(cwd)`
2. synced-plans: session-start 行 133 `listPlanFiles(cwd)` → `listUnsyncedPlanFiles(cwd)`
3. W-code-4: session-start 行 23 硬编码 flag 列表替换为 `SESSION_SCOPED_FLAGS` 导入
4. W-dry-1: todowrite-sync 移除 PACE_VERSION 导入
5. W-dry-2: 两处桥接提示调用点替换为 `formatBridgeHint()`

**T-294: Skill 文档修正**
修改点：
1. pace-bridge.md: 新增 Step 6（写入 .pace/synced-plans）+ W-skill-2 补 TodoWrite DENY 触发场景
2. artifact-management.md: W-skill-1 task.md 表格补 `禁止 Write 覆盖` 标注
3. change-management.md: W-skill-3 补 HOTFIX-ID 格式定义 + I-style-2 移除 version frontmatter

**T-295: 文档同步**
修改点：
1. REFERENCE.md: I-doc-1 函数表补 resolveProjectCwd/listPlanFiles + I-doc-2 TodoWrite I/O + I-doc-3 flag 列表 + I-doc-4 运行时文件表 + I-doc-5 PostToolUse 功能表 + I-doc-6 install.js 描述 + I-doc-7 verify.js 组数 + I-doc-10 blockCount 字段 + I-doc-13 SessionStart 输入
2. README.md: I-doc-8 hooks 目录注释 + I-doc-9 架构树 + I-doc-11 版本历史排序 + I-doc-13 SessionStart 输入
3. MEMORY.md: I-doc-12 版本号 v4.7.0→v4.8.1

**T-296: 测试补充**
新增测试：
1. 单元测试: hasUnsyncedPlanFiles/listUnsyncedPlanFiles（空目录/全已同步/部分未同步/无 synced-plans 文件）
2. E2E: pre-tool-use synced-plans 场景（旧 plan 已同步不再 DENY）
3. E2E: session-start synced-plans 场景（旧 plan 已同步不再提醒）
4. E2E: H-1 stop.js .pace/disabled 场景（应 exit 0 放行）
5. E2E: H-1 post-tool-use .pace/disabled 场景
6. E2E: W-flow-1 全完成 DENY 消息验证

**T-297: 验证 + 生产同步**
- 语法 8/8 + 单元测试 + E2E 测试 + verify 6/6 + install --force + findings 状态更新

---

#### 依赖关系

```
T-290 (pace-utils) → T-291 (stop/post-tool-use)
                   → T-292 (pre-tool-use)
                   → T-293 (session-start/todowrite-sync)
T-294 (Skill 文档) — 无代码依赖，可并行
T-295 (文档同步) — 无代码依赖，可并行
T-290~T-293 完成 → T-296 (测试)
T-296 → T-297 (验证)
```

### CHG-20260302-01: Obsidian CLI 集成 — MCP Server 配置 + Skill 增强 + 索引刷新 ✅

**状态**: ✅ 完成
**来源**: findings.md「Obsidian CLI 调研：PACEflow 集成机会分析」
**核心原则**: 最佳集成点在 AI 交互层（MCP server + Skill），Hook 层保持 fs 直接操作不变

---

#### 背景

Obsidian 1.12.4（2026-02-27）正式发布内置 CLI（100+ 命令），通过 IPC 与桌面版通信。社区插件 `obsidian-cli-rest`（2026-02-23）将 CLI 命令封装为 REST API + MCP server。PACEflow 当前通过 Node.js `fs` 模块直接读写 vault 文件，存在两个痛点：
1. `scanRelatedNotes()` 仅扫描 thoughts/+knowledge/ 两个目录的 frontmatter `projects` 字段，无全文搜索
2. fs 写入不触发 Obsidian 索引更新，新建/修改的笔记在 Obsidian 中不即时可见

#### 架构决策

- **Hook 层（pace-utils/session-start/pre-tool-use/post-tool-use/stop）**：保持 fs 直接操作，不引入 CLI 依赖。原因：延迟（fs <5ms vs CLI 100-500ms）、可靠性（CLI 依赖 Obsidian 运行）
- **AI 交互层**：通过 MCP server 提供 CLI 能力，AI 可在对话中按需使用
- **Skill 层**：更新 pace-knowledge 指引，优先使用 CLI 命令操作知识库笔记

---

#### 任务分解

**T-219: 安装并验证 Obsidian CLI**
- 确认 Obsidian 已更新到 1.12.4+
- 在 Settings → General 启用 CLI
- 验证 `obsidian version` 在终端可用
- 验证核心命令：`obsidian search query="paceflow"`、`obsidian read file="projects/paceflow-hooks/task.md"`、`obsidian tasks`
- Windows 注意：不能以管理员权限运行终端（IPC 通信会失败）
- **交付物**：CLI 可用，记录实测结果

**T-220: 安装 obsidian-cli-rest 插件**
- 通过 Obsidian Community Plugins 安装 `obsidian-cli-rest`（作者 dsebastien）
- 配置 API Key 认证
- 验证 REST API 端点：`curl http://127.0.0.1:27124/health`
- 验证 MCP endpoint：`http://127.0.0.1:27124/mcp`
- **交付物**：REST API + MCP endpoint 可用

**T-221: 配置 Claude Code MCP Server**
- 在 `~/.claude/settings.json`（或 `settings.local.json`）添加 MCP server 配置
- 传输协议：StreamableHTTP，指向 `http://127.0.0.1:27124/mcp`
- 配置 API Key 认证头
- 重启 Claude Code 验证 MCP 工具可用
- 测试 MCP 工具：search 搜索 vault、execute 执行 CLI 命令
- **交付物**：Claude Code 可通过 MCP 调用 Obsidian CLI

**T-222: 更新 pace-knowledge Skill**
- `skills/pace-knowledge.md` 添加「Obsidian CLI 命令参考」段落：
  - `obsidian property:set` 替代手动 frontmatter 编辑（更安全，不破坏 YAML）
  - `obsidian search query="..."` 替代 Grep 搜索 vault（使用 Obsidian 内置索引）
  - `obsidian create`/`obsidian append` 创建/追加笔记
  - `obsidian tasks` 查询任务状态
- 添加前置条件说明：需 Obsidian 运行 + CLI 已启用 + obsidian-cli-rest 已安装
- 添加 fallback 说明：Obsidian 未运行时回退到 fs 直接操作
- **交付物**：Skill 文档更新，同步到生产

**T-223: post-tool-use.js 异步索引刷新（可选增强）**
- 在 artifact 文件写入成功后（PostToolUse:Write|Edit），异步触发 Obsidian 索引刷新
- 实现方式：`child_process.spawn('obsidian', ['vault'], { detached: true, stdio: 'ignore' }).unref()`（fire-and-forget，不等结果）
- 前置检测：`which obsidian` 或 `obsidian version` 确认 CLI 可用，不可用时静默跳过
- **关键约束**：
  - 绝不阻塞 hook 返回（spawn + unref + detached）
  - 仅对 ARTIFACT_FILES 的 Write/Edit 触发，其他文件不触发
  - CLI 不可用时静默跳过，不 log、不报错
  - 每会话最多触发 1 次（flag 文件 `.pace/cli-refresh-done`）
- 需评估：`obsidian vault` 是否真的触发索引刷新，可能需要 `obsidian eval code="app.vault.adapter.reconcileInternalFile('...')"`
- **交付物**：post-tool-use.js 修改 + E2E 测试

**T-224: E2E 测试 + 单元测试**
- E2E：验证 post-tool-use.js 索引刷新逻辑（CLI 不可用时静默跳过）
- 集成验证：完整工作流——session-start 注入 → AI 通过 MCP 搜索 vault → 写入 artifact → 索引刷新
- **交付物**：测试通过

**T-225: 生产同步 + 验证 + 文档**
- `node paceflow/install.js --force` 同步到生产
- `node paceflow/verify.js` 健康检查
- CLAUDE.md 更新（如需）
- walkthrough.md 记录
- findings.md 关联条目状态 `[ ]` → `[x]`
- **交付物**：生产环境同步，验证通过

---

#### 依赖关系

```
T-219 (CLI 安装) → T-220 (插件安装) → T-221 (MCP 配置)
                                     → T-222 (Skill 更新)
T-219 ──────────────────────────────→ T-223 (索引刷新)
T-221 + T-222 + T-223 ─────────────→ T-224 (测试)
T-224 ─────────────────────────────→ T-225 (收尾)
```

#### 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| Obsidian 未运行时 CLI 不可用 | MCP 工具失败 | Skill 文档标注 fallback；Hook 不依赖 CLI |
| obsidian-cli-rest 极新（6 天前发布） | 插件可能有 bug | T-220 充分验证；备选方案：直接 Bash 调用 CLI |
| `obsidian vault` 不触发索引刷新 | T-223 无效 | 需实测确认，替代方案 `eval code="..."` |
| Windows 管理员权限导致 IPC 失败 | CLI 全部不可用 | 文档标注；hook 不受影响（fs 操作） |

#### 可选扩展（本次不实施）

- session-start.js 增加 CLI fallback 搜索（增加复杂度和启动延迟）
- Dataview 查询集成（依赖插件内部 API 稳定性）

### CHG-20260301-01 PACEflow v4.8.0 — Artifact 存储迁移到 Obsidian Vault

**背景**：Artifact 文件从项目 CWD 迁移到 Obsidian Vault，实现跨项目统一管理和 Obsidian 原生浏览。

**T-210~T-218 主要改动**：
- pace-utils.js 新增 getProjectName + getArtifactDir 路径解析器（vault 优先→CWD fallback→新项目默认 vault）
- 7 个 hook 路径修正 + Write/Edit artifact 到 CWD 时 deny + 重定向到 vault
- migrate-artifacts.js 迁移脚本，执行迁移 8 项目（junction→实际目录+artifact 复制）
- E2E 4 新测试 + 单元 6 新测试

### CHG-20260228-03 E2E 测试 VAULT_PATH 隔离

**背景**：E2E 测试直接使用真实 VAULT_PATH，可能污染用户 Obsidian Vault。

**T-209 主要改动**：
- test-hooks-e2e.js VAULT_PATH 重定向到临时目录，隔离测试环境

### CHG-20260228-02 PACEflow 基础设施解耦 + 模板格式引导

**背景**：createTemplates 内嵌基础设施逻辑（junction + .gitignore），需拆分为独立函数；Write 新建 artifact 时缺乏格式引导。

**T-204~T-208 主要改动**：
- pace-utils.js 拆分 ensureProjectInfra(cwd) 独立函数（幂等：.pace/.gitignore + junction 健康检查+损坏重建）
- session-start.js paceSignal 为真时无条件调用 ensureProjectInfra
- pre-tool-use.js Write 新建 artifact 文件时注入对应模板内容到 additionalContext
- E2E 3 新测试 + 版本号 v4.7.1

### CHG-20260228-01: v4.7.0 全系统审查修复 ✅

**状态**: ✅ 完成
**来源**：`paceflow/docs/review-2026-02-28.md`（3 reviewer 并行审查报告）
**修复范围**：3 Critical + 1 High + 14 Warning + 6 文档过时，11/12 任务完成（T-203 延后）

**修改文件**：
- `paceflow/hooks/stop.js`（T-194：matchAll 取最后日期 + 无日期分支）
- `paceflow/hooks/config-guard.js`（T-197：exit 2→additionalContext + 正则收紧）
- `paceflow/hooks/pace-utils.js`（T-198：VAULT_PATH env + countCodeFiles 缓存 + symlinkSync + CRLF）
- `paceflow/hooks/pre-tool-use.js`（T-199：ARTIFACT_FILES 导入 + PROTECTED_ARTIFACTS 派生）
- `paceflow/skills/templates/change-implementation_plan.md`（T-195：Emoji→Checkbox 重写）
- `paceflow/skills/change-management.md`（T-196：4 处修正）
- `paceflow/CLAUDE.md`（T-200：v4.7.0 + 7 脚本 + 4 Skill）
- `paceflow/REFERENCE.md`（T-201：pace-knowledge 4.4 + 版本引用）
- `paceflow/tests/test-hooks-e2e.js`（T-202：config-guard 测试适配）

**关联任务**: T-192 ~ T-203

### CHG-20260227-02: Corrections 双写机制 — findings.md → knowledge/ 自动提醒 ✅

**状态**: ✅ 完成
**目标**: Correction 写入 findings.md 时自动提醒双写到 knowledge/，实现跨项目经验复用

**修改文件**:
- `paceflow/hooks/post-tool-use.js`（+3 行 H11：检测 `### Correction:` 写入 → HINT 双写 knowledge/）
- `C:/Users/Xiao/.claude/CLAUDE.md` + `paceflow/rules/CLAUDE.md`（G-3 增强 corrections 双写规则）
- `paceflow/hooks/templates/findings.md` + `paceflow/skills/templates/artifact-findings.md`（补 Corrections 区）
- `findings.md`（现有 3 条 correction 补 `[knowledge::]` 标注）
- `knowledge/ai-verification-discipline.md`（新建：2 条跨项目 correction 提炼）

**关联任务**: T-187 ~ T-191

### CHG-20260227-01: PostToolUse impl_plan 详情归档提醒 ✅

**状态**: ✅ 完成
**目标**: 检测索引已 `[x]`/`[-]` 但详情 `### CHG-...` 仍在活跃区 → 提醒更新状态并归档

**修改文件**:
- `paceflow/hooks/post-tool-use.js`（+12 行 H10 检查：读 impl_plan 活跃区，索引↔详情交叉对比，每会话首次 flag）
- `paceflow/hooks/session-start.js`（+1 行重置 `impl-archive-reminded` flag）

**关联任务**: T-184 ~ T-186

### CHG-20260226-02: PACEflow v4.7.0 — Agent Teams 兼容性（Direction C） ✅

**状态**: ✅ 完成
**目标**: 移除 2 个无效 hook + 给 3 个 hook 添加 teammate 检测（阻止→降级/静默），实现 Agent Teams 混合策略

**背景**：Agent Teams 实测（2026-02-26）发现 teammate-idle.js 和 task-completed.js 基于错误语义假设从未正常工作（详见 findings.md Correction）。Direction C 混合策略：lead 维护 PACE 纪律，teammate 降级/静默。

**检测方法**：`process.env.CLAUDE_CODE_TEAM_NAME`——teammate 进程自动设置此环境变量（值为 team name），主会话不设置。

**删除文件**:
- `paceflow/hooks/task-completed.js`（触发条件是 Agent Teams 共享任务，非 PACE task.md）
- `paceflow/hooks/teammate-idle.js`（teammate 已完成工作时注入约束提醒无意义）

**修改文件**:
- `paceflow/hooks/pace-utils.js`（+3 行 `isTeammate()` + 版本号 v4.6.0→v4.7.0 + exports 更新）
- `paceflow/hooks/stop.js`（+8 行 teammate 降级：exit 2 → exit 0 + additionalContext JSON stdout）
- `paceflow/hooks/pre-tool-use.js`（+6 行 teammate 降级：deny → additionalContext，覆盖 3 处 deny 分支）
- `paceflow/hooks/todowrite-sync.js`（+3 行 teammate 检测：early return 静默）
- `paceflow/config/settings-hooks-excerpt.json`（删除 TeammateIdle + TaskCompleted 两个事件段）
- `paceflow/verify.js`（EXPECTED_HOOKS 9→7，移除两个脚本名）
- `paceflow/tests/test-hooks-e2e.js`（删除 5 个旧测试 + 新增 3 个 teammate 检测测试）

**关联任务**: T-178 ~ T-183

### CHG-20260226-01 Findings 状态流转 — Skill 补链 + Hook 实时检查 + SessionStart 过期提醒

**背景**：findings.md 状态流转缺乏 Hook 层检查和 Skill 层指引，已采纳条目无法自动检测完成度。

**T-173~T-177 主要改动**：
- Skill 补链 2 处（artifact-management + change-management findings 状态说明）
- SessionStart 过期提醒（findings 活跃区超过 7 天未更新的条目）
- PostToolUse H9 CHG 完成检查（索引 `[x]` 时扫描 findings 关联条目）

### CHG-20260225-09 Hook E2E 测试脚本

**背景**：Hook 缺乏系统化端到端测试，变更后依赖手动验证，回归风险高。

**T-170~T-172 主要改动**：
- 新建 test-hooks-e2e.js（27 个测试覆盖 9 hook 的 stdin/stdout/exit code）
- install 26/26 一致 + verify 5/5

### CHG-20260225-08 V 阶段收尾 — verify.js 更新 + 生产同步 + walkthrough

**背景**：批次 1~3 完成后的验证收尾工作。

**T-167~T-169 主要改动**：
- verify.js EXPECTED_HOOKS 5→9
- install.js --force 生产同步（10 安装+8 更新）
- walkthrough 记录

### CHG-20260225-03 PreToolUse impl_plan [/] 检查 + pace-workflow 补充 v4.4.3

**背景**：E 阶段执行代码前缺乏 impl_plan 状态检查，AI 可跳过将索引标为 `[/]` 的步骤。

**T-149~T-152 主要改动**：
- pre-tool-use.js E 阶段新增 `[/]` 前提 DENY（impl_plan 无 `[/]` 索引时阻止写代码）
- pace-workflow SKILL.md A/C 阶段补充说明

### CHG-20260225-02 PostToolUse 优化 — 去重+降频+自签检测 v4.4.2

**背景**：PostToolUse 提醒过于频繁，导致 AI 注意力分散；APPROVED/VERIFIED 可能被 AI 自签。

**T-148 主要改动**：
- H3/H7 改为每会话首次提醒（flag 文件机制）
- 删除 H4/H5 低价值提醒
- 新增 APPROVED/VERIFIED 自签检测（last_assistant_message 包含标记时警告）

### CHG-20260225-01 pace-knowledge skill + PreToolUse 模板提醒

**背景**：obsidian-knowledge skill 改名为 pace-knowledge，PreToolUse 缺乏知识库笔记模板引导。

**T-147 主要改动**：
- Skill 改名 + frontmatter 更新 + artifact-management 交叉引用
- pre-tool-use.js v4.4.1 新增知识库模板提醒（Write 到 thoughts/knowledge 时注入 additionalContext）

### CHG-20260225-06: PACEflow v4.6.0 批次 3 — 扩展 hook ✅

**状态**: ✅ 完成
**目标**: 新增 ConfigChange/TeammateIdle/TaskCompleted 三个 hook 事件
**注**: teammate-idle.js 和 task-completed.js 后被 CHG-20260226-02 移除（基于错误语义假设）

**新建文件**:
- `paceflow/hooks/config-guard.js`（~35 行）— disableAllHooks 阻止 + PACE hook 删除提醒
- `paceflow/hooks/teammate-idle.js`（~30 行）— 已被 CHG-20260226-02 删除
- `paceflow/hooks/task-completed.js`（~40 行）— 已被 CHG-20260226-02 删除

**修改文件**:
- `paceflow/hooks/pace-utils.js`（版本号 → v4.6.0）
- `paceflow/config/settings-hooks-excerpt.json`（新增 3 事件）

**关联任务**: T-161 ~ T-164

### CHG-20260225-05: PACEflow v4.5.0 批次 2 — 核心 hook 改进 ✅

**状态**: ✅ 完成
**目标**: stop.js 交叉验证 + PreCompact 快照恢复 + 否定决策捕获增强

**新建文件**:
- `paceflow/hooks/pre-compact.js`（~40 行）— 收集 artifact 状态快照写入 .pace/pre-compact-state.json

**修改文件**:
- `paceflow/hooks/stop.js`（+15 行 stdin 解析 + "任务完成"交叉验证）
- `paceflow/hooks/session-start.js`（+15 行 compact 事件读取快照恢复）
- `paceflow/hooks/post-tool-use.js`（+10 行 H8 扩展 [-] 理由 < 10 字检测）
- `paceflow/hooks/pace-utils.js`（版本号 → v4.5.0）
- `paceflow/config/settings-hooks-excerpt.json`（新增 PreCompact 事件）

**关联任务**: T-157 ~ T-160

### CHG-20260225-04: PACEflow v4.5+ 批次 1 — 基础设施 ✅

**状态**: ✅ 完成
**目标**: 创建单元测试、健康检查、安装脚本三个基础设施工具 + [P] 并行任务文档

**新建文件**:
- `paceflow/tests/test-pace-utils.js`（~80 行）— 16 个测试覆盖 isPaceProject/countByStatus/readActive/checkArchiveFormat
- `paceflow/verify.js`（~70 行）— 语法验证+源码-生产一致性+settings 完整性+版本号+模板同步
- `paceflow/install.js`（~100 行）— installHooks+installSkills+patchSettings，支持 --dry-run/--force

**修改文件**:
- `paceflow/skills/artifact-management.md`（+5 行 [P] 并行任务标记说明）
- `paceflow/skills/pace-workflow.md`（+3 行 E 阶段 [P] 分配说明）

**关联任务**: T-153 ~ T-156
**不升 PACE_VERSION**（工具/文档，不改 hook 行为）

### CHG-20260225-07: PACEflow 批次 4 — 评估与打包 ❌

**状态**: ❌ 废弃
**目标**: bash 权限评估 + Plugin 打包方案

**关联任务**: T-165 ~ T-166
**推迟到所有 hook 稳定后执行**

### CHG-20260224-04: Artifact 索引格式迁移 — 表格 → checkbox + inline fields ✅

**状态**: [x] 完成
**目标**: findings.md 摘要索引 + implementation_plan.md 变更索引从 markdown 表格改为 checkbox + inline fields，兼容 Obsidian Tasks/Dataview 跨项目查询

**格式设计**:

findings.md 新格式：
```
- [x] Hook 路径格式 — Git Bash 不认 K:/ 盘符 #finding [date:: 2026-02-11] [change:: CHG-01]
- [-] OpenSpec 对比分析 — 保持现状：Artifact 结构差异大 #finding [date:: 2026-02-16]
- [ ] ⚠️ 某个未解决问题 #finding [date:: 2026-02-14]
```

implementation_plan.md 新格式：
```
- [x] CHG-20260224-02 Obsidian 知识中枢第二阶段 #change [tasks:: T-134~T-138]
- [-] CHG-20260224-03 vault-sync 知识自动流转 #change [tasks:: T-139~T-141]
- [/] CHG-20260224-04 Artifact 索引格式迁移 #change [tasks:: T-142~T-146]
```

**状态映射**:
- findings: `[x]`=已采纳/已验证/已实施 | `[-]`=保持现状/已否定 | `[ ]`=参考中/待评估
- impl_plan: `[ ]`=规划中 | `[/]`=进行中 | `[x]`=完成 | `[-]`=废弃 | `[!]`=暂停

**Hook 改动**: 2 行（`planActive.includes('🔄')` → `/^- \[\/\]/m.test(planActive)`）
**模板改动**: 4 个文件（hooks/templates + skills/templates）
**数据迁移**: 当前项目 24+22 条 + 其他 6 项目按需

### CHG-20260224-02 Obsidian 知识中枢第二阶段

**背景**：第一阶段 Vault 骨架建好后，需要为每个 PACE 项目创建 Junction 并实现 thoughts 笔记自动注入。

**T-134~T-138 主要改动**：
- 6 个 PACE 项目创建 Junction（mklink /J）
- pace-utils.js 新增 VAULT_PATH 常量 + scanRelatedNotes 函数（扫描 thoughts/+knowledge/ frontmatter）
- session-start.js 追加 thoughts 注入段（非 compact 时调用 scanRelatedNotes 注入 L0 摘要）
- Home.md 新增 6 个项目入口（共 7 个项目）

### CHG-20260214-08 系统审视改进 v4.4.0

**背景**：findings.md 状态标记不够细致，版本号分散在各文件，日志过于冗余。

**T-104~T-108 主要改动**：
- findings.md 引入 `🔒` 已知限制状态，post-tool-use.js 统计 unresolved
- PACE_VERSION 集中化到 pace-utils.js（v4.4.0），6 个脚本 import 引用
- 6 个脚本日志精简（仅保留 DENY/BLOCK/ERROR 等非常规事件）

### CHG-20260214-07 3-Agent 审查修复 v4.3.9

**背景**：3-Agent 审查发现 pre-tool-use.js 版本不同步和两个 hook 缺顶层 try-catch。

**T-100~T-102 主要改动**：
- pre-tool-use.js 版本号同步到 v4.3.9 + 同步到生产
- pre-tool-use.js/post-tool-use.js 添加顶层 try-catch（异常时 exit 0 静默放行）
- stop.js 移除未使用的 readFull import

### CHG-20260214-06 Stop hook TodoWrite 清理提醒

**背景**：Stop hook 退出时未提醒清理 TodoWrite 残留，compaction 后可能导致重复执行。

**T-098 主要改动**：
- stop.js 新增 TodoWrite 残留清理提醒（flag 文件方案，3 文件联动）

### CHG-20260214-05 ticket6 审查修复 v4.3.8

**背景**：ticket6 审查发现 todowrite-sync 多个边界条件 bug 和代码质量问题。

**T-089~T-097 主要改动**：
- todowrite-sync.js TodoWrite 清空操作早期返回 + 全归档提醒 + 活跃区扫描限制
- post-tool-use.js 删除 TaskCreate/TaskUpdate 死代码
- pace-utils.js 新增 countByStatus 统一正则
- settings-hooks-excerpt.json 追加 TodoWrite 配置段
- 版本升级到 v4.3.8

### CHG-20260214-03 ticket5 空项目激活方案 v4.3.5

**背景**：空项目（无代码文件）无法激活 PACE，Superpowers 流程在新项目中失效。

**T-075~T-081 主要改动**：
- pre-tool-use.js 懒创建模板 + off-by-one 前瞻修复
- session-start.js D2 模板发现信号
- 豁免机制（.pace/disabled）
- 版本升级到 v4.3.5

### CHG-20260214-01 W6 Tasks API 同步提醒

**背景**：Claude Code Tasks API（TaskCreate/TaskUpdate）写入与 task.md 不同步。

**T-066~T-067 主要改动**：
- post-tool-use.js 新增 TaskCreate/TaskUpdate → task.md 同步提醒

### CHG-20260213-04 W5 findings 降级 + I4 .pace/ 目录

**背景**：findings.md 检查过于严格导致误报，运行时文件散落在项目根目录。

**T-063~T-065 主要改动**：
- findings 检查降级为软提醒（不阻止退出）
- 运行时文件集中到 .pace/ 目录（stop-block-count、degraded 等）

### CHG-20260213-03 ticket4 审查修复

**背景**：ticket4 第二轮审查（5-Agent）发现 5C+8W+5I 共 18 个问题。

**T-055~T-062 主要改动**：
- codeCount 阈值修正（>= 2 → >= 3）
- Superpowers deny 增加 hasPlanFiles() 检测
- 4 个脚本顶层 require try-catch（pace-utils 加载失败→exit 0 降级）
- hasApproval 正则修复（移除反斜杠误匹配）
- stop-block-count 改为 cwd 维度隔离

### CHG-20260214-04: PACE-TodoWrite 同步方案 A+B+C+D ✅

**目标**：解决 compaction 后 TodoWrite 残留快照导致 AI 重复执行已完成任务的问题，确立 task.md 为任务权威来源

**实施方案**：四层缓解
- **A**: session-start.js 三态 TodoWrite 同步指令注入（hasPending→同步 / hasCompleted→归档后清 / 无任务→清空）
- **B**: CLAUDE.md G-3 补充 task.md > TodoWrite 优先级规则
- **C**: post-tool-use.js 编辑 task.md 后 TodoWrite 同步提醒（复用 doneCount 避免重叠）
- **D**: todowrite-sync.js PreToolUse:TodoWrite 拦截校验（顶层任务比对 + 3 项阈值）

**关联任务**：T-082 ~ T-088
**方案文件**：`findings.md`
**改动文件**：
- `session-start.js`：三态注入 + taskFullCached 缓存消除三重 I/O
- `post-tool-use.js`：task.md 编辑后 TodoWrite 同步提醒
- `todowrite-sync.js`（新建）：PreToolUse:TodoWrite 拦截 + 全局 try-catch + 锚定正则
- `CLAUDE.md`：G-3 task.md > TodoWrite 优先级
- `settings.json`：TodoWrite hook 指向正式脚本
**结果**：8/8 完成（含 T-088 E2E 验证 + v4.3.7 三工具名修复），5/5 语法验证通过

### CHG-20260213-02: v4.3.3 全面审查修复 ✅

**目标**：修复 4-Agent 全面审查发现的 23 个问题（6🔴 + 10🟡 + 7🔵）

**关联任务**：T-040 ~ T-054
**ticket 文件**：`ticket3.md`
**完成时间**：2026-02-13T23:30:00+08:00
**结果**：13/15 任务完成（2 个跳过），5/5 JS 语法验证通过
**改动文件**：
- `pace-utils.js`：W10 try-catch
- `pre-tool-use.js`：C1 Write保护 + C5 codeCount + W5 [!]批准
- `post-tool-use.js`：W1 正则 + W8 日期正则 + W3 stdin 重构
- `stop.js`：W1 正则 + W7 V/归档优先级 + W8 日期正则 + W4 降级反馈
- `session-start.js`：W2 复用 readActive() + 降级标记清除
- `pace-workflow/SKILL.md`：C2 Superpowers 同步规则
- `CLAUDE.md`：C3 Bash 绕过禁令（G-4）
- `change-management/templates/implementation_plan.md`：C4 双区结构同步
- `change-management/examples/example_workflow.md`：S6 双区结构示例
- 删除：4 个 .sh 遗留文件
**跳过**：T-048（runChecks 提取，逻辑已分化）、T-052（CONFIG_EXTS，保持现状）

### CHG-20260215-03: V 阶段强制 + Write artifact 保护 ✅

**目标**：Write 覆盖 artifact 拦截（100%）+ V 阶段 VERIFIED 标记强制（~90%）

**关联任务**：T-036 ~ T-039
**完成时间**：2026-02-15T04:30:00+08:00
**改动文件**：
- `pre-tool-use.js`：DENY_WRITE_ARTIFACT（Write + 已存在 protected artifact → 100% deny）
- `stop.js`：`[x]` 完成项 + 无 `<!-- VERIFIED -->` → block
- `CLAUDE.md`：G-8 关键格式新增 `<!-- VERIFIED -->`
- `pace-workflow/SKILL.md`：V 阶段新增获验后操作 + hook 强制说明
**结果**：2/2 语法验证通过

### CHG-20260215-02: C 阶段 hook 强制检查 ✅

**目标**：通过 `<!-- APPROVED -->` 标记强制 C 阶段用户确认，将确定性从 ~70% 提升到 ~90%+

**关联任务**：T-033 ~ T-035
**完成时间**：2026-02-15T04:00:00+08:00
**改动文件**：
- `pre-tool-use.js`：重构活跃区读取 + 新增 hasApproval 检查（DENY_C_PHASE）
- `CLAUDE.md`：G-8 关键格式新增 `<!-- APPROVED -->` 标记
- `pace-workflow/SKILL.md`：C 阶段流程新增获批后操作 + v4.3.2 Hook 强制说明
**结果**：语法验证通过，版本升级到 v4.3.2

### CHG-20260215-01: v4.3.1 审查修复 + DRY 重构 ✅

**目标**：修复 4-agent 审查发现的残留问题（2 个 bug + 3 个 DRY 违反 + 5 个文档不同步）

**关联任务**：T-024 ~ T-032
**ticket 文件**：`ticket2.md`
**完成时间**：2026-02-15T03:30:00+08:00
**改动文件**：
- `pace-utils.js`：新增 readActive/readFull/checkArchiveFormat 导出
- `pre-tool-use.js`：B1 正则修复 + B2 路径修复 + D1 CODE_EXTS
- `post-tool-use.js`：D1 countCodeFiles + D3 删除重复函数
- `session-start.js`：D2 ARTIFACT_FILES
- `stop.js`：D2 ARTIFACT_FILES + D3 删除重复函数
- `CLAUDE.md`：G-8 Hook/AI 判断分离 + G-9 补 `[-]`
- `pace-workflow/SKILL.md`：激活流程图 + v4.3.1 行为说明
- Obsidian 设计文档：6 处更新（frontmatter/§五/§九/§十/§十一/§十二）
**结果**：5/5 JS 语法验证通过

### CHG-20260214-02: PreToolUse v4.3.1 修复 ✅

**目标**：修复 v4.3 三级触发的 4 个问题（模板绕过、硬编码不一致、消息错误、项目外误伤）

**关联任务**：T-019 ~ T-023
**完成时间**：2026-02-13T18:30:00+08:00
**改动文件**：
- `templates/task.md`：移除占位任务条目
- `artifact-management/templates/task.md`：同步移除占位任务
- `pre-tool-use.js`：hasActiveTasks 检测 + artifact 信号 deny + 项目外豁免 + codeCount 消息
- `stop.js`：artifactFiles 补 findings.md + countCodeFiles() 替换硬编码
**结果**：6/6 场景测试通过（A~F），日志验证全部动作正确

### CHG-20260214-01: PACE + Superpowers 空项目集成 ✅

**目标**：解决空项目中 Superpowers 流程（brainstorm→plan→execute）无法激活 PACE 的问题

**实施方案**: Obsidian 设计文档 §十二（draft-v4.3）

**Phase 1（P0 — 代码改动）**：
1. 新建 `pace-utils.js` 公共模块：`isPaceProject()` 四信号判断
2. 改造 `session-start.js`：多信号检测替换 `codeFileCount >= 3`
3. 改造 `pre-tool-use.js`：三级触发（superpowers deny / code-count deny / soft-warn）
4. 改造 `post-tool-use.js`：多信号检测替换 else 分支
5. 改造 `stop.js`：多信号检测替换 else 分支

**Phase 2（P1 — Skill/配置）**：
6. 更新 `pace-workflow/SKILL.md` 激活判定
7. 更新 `CLAUDE.md` G-8 启用条件

**关联任务**：T-010 ~ T-018
**完成时间**：2026-02-14T04:45:00+08:00
**结果**：isPaceProject() 7/7 测试场景通过，5 个 JS 文件语法验证通过

### CHG-20260213-01: PACE 三层架构补全 ✅

**目标**：修复 pace-fulltest 暴露的三层架构失效问题

**实施方案**：
1. G-10 补充 PACE 启用后的执行流程（P-A-C-E-V）和关键格式定义
2. G-11 增加故障转移条款（不依赖 hook 提醒也必须主动检查）
3. PostToolUse 增加无 artifact 警告（3+ 代码文件但无 task.md）和 ARCHIVE 格式验证
4. Stop 增加完整性检查（walkthrough 存在性、孤立 artifact、代码文件检测）

**关联任务**：T-006 ~ T-009
**完成时间**：2026-02-13T00:28:00+08:00
**结果**：全部验证通过，pace-fulltest 的错误格式被正确检测

### CHG-20260212-02: Hooks V 阶段覆盖扩展 ✅

**目标**：扩展 PostToolUse 和 Stop hook，覆盖 implementation_plan.md、walkthrough.md、findings.md 的检查

**实施方案**：
1. PostToolUse：检测 task.md [x] 时联动检查 impl_plan 🔄 状态和 walkthrough 时间戳
2. Stop：增加 impl_plan、walkthrough、findings 的综合检查

**关联任务**：T-004（PostToolUse 扩展）、T-005（Stop 扩展）
**完成时间**：2026-02-12T23:28:00+08:00
**结果**：全部验证通过，修复了 indexOf ARCHIVE 误匹配 bug，更新 G-11 规则

### CHG-20260212-01: Hooks 功能测试 ✅

**目标**：验证 4 个全局 hooks 是否正常工作

**实施方案**：
1. 重启 Claude Code 触发 SessionStart hook
2. 执行 Write/Edit 操作触发 PreToolUse + PostToolUse hooks
3. 结束会话触发 Stop hook
4. 验证 PreToolUse + PostToolUse 是否存在 #12445 冲突

**关联任务**：T-001（PreToolUse）、T-002（PostToolUse）、T-003（SessionStart）
**完成时间**：2026-02-12T22:50:00+08:00
**结果**：4 个 hooks 全部验证通过，#12445 冲突不存在，Bash→Node.js 迁移完成，日志功能已添加

### CHG-20260211-01: Hooks 配置 ✅

**目标**：创建 4 个 hook 脚本并配置到 settings.json
**完成时间**：2026-02-11T21:12:00+08:00
**结果**：4 个脚本创建完成，已迁移到全局 `~/.claude/hooks/pace/`
