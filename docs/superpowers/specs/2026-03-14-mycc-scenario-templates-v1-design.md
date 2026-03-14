# mycc 场景化模板清单 v1（设计稿）

- 日期：2026-03-14
- 状态：Draft（审查修订中）
- 范围：最小可用 10 条模板（3 内容 + 3 采集 + 3 开发 + 1 通用）
- 目标：在不新增依赖、不重写现有 skill 的前提下，沉淀一套“可读 + 可执行（手动/调度可消费）”的场景模板规范

---

## 1. 设计目标

将现有 skill 能力从“单技能调用”升级为“场景模板调用”，统一以下要素：

1. 触发词（用户怎么说）
2. 输入规范（最小必填）
3. 路由链路（调用哪些 skill）
4. 输出物（产物路径/格式）
5. 验收标准（如何判断完成）
6. 通知策略（是否飞书推送）

**v1 定位**：先做模板标准与执行手册，不做新的自动编排引擎。

---

## 2. 交付物（双轨）

### 2.1 文档主轨（人类可读）

- 文件：`docs/superpowers/specs/2026-03-14-mycc-scenario-templates-v1-design.md`（本文）
- 用途：定义模板规范、模板目录、验收规则、回退策略

### 2.2 YAML 辅轨（可执行骨架）

- 文件：`0-Skill-Platform/mycc-scenario-templates-v1.yaml`
- 用途：供手动执行和 scheduler 参数化引用
- 交付范围：包含 **10 条模板完整定义**（不是仅示例）
- 说明：YAML 文件在实施阶段生成，本设计文档定义其 schema 与样例

---

## 3. v1 边界（YAGNI）

v1 不做：

1. 自动化编排引擎重构
2. 新 skill 开发
3. skill 内部逻辑改造
4. 新依赖引入
5. 跨服务配置变更

v1 只做：

1. 场景模板标准化
2. 模板清单落库（文档 + YAML）
3. 回退与验收规则统一
4. 手动执行与 scheduler 调用契约统一

---

## 4. 执行模式与责任边界

### 4.1 执行模式

- **手动模式（默认）**：主 cc 根据模板字段逐步调用 skill。
- **调度模式（现有 scheduler）**：scheduler 仅负责触发，主 cc 按模板执行（仍非自动编排）。

### 4.2 scheduler 最小契约（v1）

- 配置文件路径：`.claude/skills/scheduler/tasks.md`
- 模板清单路径：`0-Skill-Platform/mycc-scenario-templates-v1.yaml`
- 承载位置：任务“说明”字段内追加 3 行键值（保留原说明语义）
- 解析执行方：`mycc/scripts/src/index.ts` 中 `executeTask(...)`（主 cc）负责读取并执行；scheduler 仅按时间触发，不做多 skill 编排
- 执行历史回写：`0-Skill-Platform/template-run-log.jsonl`（每次执行追加一行 JSON）

在 `tasks.md` 的任务说明中携带：

```text
template_id:tpl-collect-001
inputs:{"topic":"AI+股市"}
notify:{"enabled":true,"channel":"feishu","level":"blue"}
```

解析规则（v1）：
1. 逐行扫描说明字段，命中 `template_id` / `inputs` / `notify` 前缀即取值
2. `template_id` 作为模板主键，必须能在 `0-Skill-Platform/mycc-scenario-templates-v1.yaml` 中命中
3. `inputs` 按 JSON 解析并映射到模板 `inputs[].name`
4. `notify` 按 JSON 解析并做“规则化合并”：
   - 若最终 `enabled=false`：强制清空 `channel`、`level`
   - 若最终 `enabled=true`：必须有 `channel=feishu` 与 `level`
5. 任一 JSON 解析失败（`inputs`/`notify`）即判定失败，直接进入 8.2 回退链路
6. 执行结果回写历史：`task_name/template_id/status/timestamp/error?`
7. 若缺失 `template_id`：按原 scheduler 任务逻辑执行（兼容旧任务）

### 4.3 责任边界

- 模板层：定义“该怎么跑、跑完怎么看”。
- skill 层：负责单步能力执行。
- scheduler：负责“何时触发”，不负责多 skill 自动编排。

---

## 5. 模板 Schema（YAML 规范）

### 5.1 字段定义

| 字段 | 类型 | 必填 | 说明 |
|---|---|---:|---|
| `id` | string | 是 | 模板唯一 ID，如 `tpl-content-001` |
| `name` | string | 是 | 模板名 |
| `category` | enum | 是 | `content`/`collect`/`dev`/`general` |
| `triggers` | object[] | 是 | 触发词定义，见 5.2 |
| `entry_skill` | string | 是 | 主入口 skill |
| `fallback_skill` | string | 否 | 失败回退 skill；允许 `none`（不降级）或具体 skill 名 |
| `inputs` | object[] | 是 | 输入项定义（name/type/required/desc/example） |
| `workflow` | object[] | 是 | 步骤定义（step/skill/purpose） |
| `outputs` | object[] | 是 | 输出定义（type/path_or_channel/required） |
| `acceptance` | string[] | 是 | 可检查验收条目 |
| `notify` | object | 是 | `{enabled:boolean, channel?:"feishu", level?:"blue"|"red"}` |

### 5.1.1 fallback_skill 语义

- 缺省值：`none`
- `fallback_skill=none`：失败后不走降级 skill，直接进入红卡
- `fallback_skill=<skill_name>`：首次失败重试后，调用该 skill 做一次降级
- 不允许 `null`、空字符串；写入时统一为 `none`

### 5.2 triggers 结构

`triggers` 每项字段：
- `kind`: `slash | exact | fuzzy`
- `text`: 触发词文本
- `extract`: 可选，参数提取规则标识（`url | topic | none`）

执行口径（v1，可手动执行）：
1. 预处理：输入先做 `trim`，并将连续空白折叠为单空格
2. `slash`：要求完整匹配（如 `/read-gzh`）
3. `exact`：预处理后全等匹配
4. `fuzzy`：预处理后执行“`text` 为用户输入子串”匹配，不做语义向量匹配
5. `extract=url`：使用正则 `https?://[^\s]+` 提取首个链接，再剥离尾随标点（`。 ， ； ！ ？ ) ] }`）
6. `extract=topic`：移除“首次命中触发词”后，剩余文本 `trim` 作为 topic
7. 未命中可提取值时，保持空并触发一次回问

示例：
```yaml
triggers:
  - kind: slash
    text: /read-gzh
    extract: url
  - kind: exact
    text: 读这篇公众号
    extract: url
  - kind: fuzzy
    text: 公众号拆解
    extract: url
```

### 5.3 notify 约束

- `enabled=false`：不得出现 `channel`、`level`
- `enabled=true`：必须有 `channel=feishu` 与 `level`

### 5.4 变量规范

路径变量统一使用：`{YYYY-MM-DD}`（不再使用 `{date}`）。

### 5.5 YAML 示例（完整 1 条）

```yaml
version: "v1"
templates:
  - id: tpl-collect-001
    name: 每日综合简报
    category: collect
    triggers:
      - kind: exact
        text: 每日简报
      - kind: exact
        text: 今天早报
      - kind: slash
        text: /collect
    entry_skill: collect
    fallback_skill: tell-me
    inputs:
      - name: topic
        type: string
        required: false
        desc: 采集主题
        example: AI + 股市 + 时政
    workflow:
      - step: 1
        skill: collect
        purpose: 多源采集并生成 briefing.md
      - step: 2
        skill: tell-me
        purpose: 将 briefing 推送飞书
    outputs:
      - type: file
        path_or_channel: 1-Inbox/_collect/{YYYY-MM-DD}/briefing.md
        required: true
      - type: notification
        path_or_channel: feishu
        required: true
    acceptance:
      - briefing.md 文件存在
      - 简报包含 30 秒速读与行动项
      - 推送成功且返回 success
    notify:
      enabled: true
      channel: feishu
      level: blue
```

---

## 6. 路由规则与冲突处理

### 6.1 匹配优先级

1. slash 精确命中
2. 自然语言 exact 命中
3. fuzzy 命中

### 6.2 category 冲突优先级

`dev > collect > content > general`

### 6.3 同优先级冲突

- 向用户回问 1 次选择
- 若无选择：按 `id` 字典序最小者作为稳定默认

---

> **已冻结决策（v1 模板矩阵锁定）**
> - 仅 10 条模板：7.1 内容创作 3 条 + 7.2 信息采集 3 条 + 7.3 开发协作 3 条 + 7.4 通用 1 条
> - 默认 notify 推送飞书（`enabled: true`，`channel: feishu`，`level` 按需配置）
> - 严格沿用已有 `template_id`、`category`、`workflow` 主链路，不做变更
> - 5.5 YAML 示例不计入模板矩阵数量

## 7. v1 模板目录（10 条）

> 说明：下列为”目录级摘要”；实施时 YAML 必须给出 10 条完整字段定义（按第 5 章 schema）。

## 7.1 内容创作（3）

1. `tpl-content-001` 选题 -> 标题包
   - entry_skill: `outline`
   - fallback_skill: `title`
   - workflow: `outline -> title -> tell-me`

2. `tpl-content-002` 主题 -> 公众号初稿
   - entry_skill: `draft`
   - fallback_skill: `create-system`
   - workflow: `draft -> polish -> gzh`

3. `tpl-content-003` 热点 -> 观点短文
   - entry_skill: `collect`
   - fallback_skill: `draft`
   - workflow: `collect -> draft -> polish`

## 7.2 信息采集（3）

4. `tpl-collect-001` 每日综合简报
   - entry_skill: `collect`
   - fallback_skill: `tell-me`
   - workflow: `collect -> tell-me`

5. `tpl-collect-002` GitHub AI 趋势播报
   - entry_skill: `gh-trending`
   - fallback_skill: `collect`
   - workflow: `gh-trending -> tell-me`

6. `tpl-collect-003` 公众号链接拆解
   - entry_skill: `read-gzh`
   - fallback_skill: `create-system`
   - workflow: `read-gzh -> create-system(可选)`

## 7.3 开发协作（3）

7. `tpl-dev-001` 需求 -> 单 Agent 实现
   - entry_skill: `dev`
   - fallback_skill: `none`（显式表示“无降级 skill”，失败直接红卡）
   - workflow: `dev`

8. `tpl-dev-002` 需求 -> 多 Agent 并行实现
   - entry_skill: `dev-team`
   - fallback_skill: `dev`
   - workflow: `dev-team`

9. `tpl-dev-003` 测试质量审查
   - entry_skill: `test-review`
   - fallback_skill: `dev`
   - workflow: `test-review -> tell-me`

## 7.4 通用（1）

10. `tpl-general-001` 定时模板任务注册
    - entry_skill: `scheduler`
    - fallback_skill: `tell-me`
    - workflow: `scheduler`（仅注册/更新任务，不负责模板执行）
    - 说明：执行阶段仍由 scheduler 触发后交给主 cc `executeTask(...)` 按模板运行

---

## 8. 失败回退策略（v1 手动/调度统一口径）

### 8.1 失败判定

满足任一即失败：
1. skill 返回异常/报错
2. 单步骤执行超过 300 秒（`step_timeout_sec=300`，机器计时）
3. 必需产物缺失
4. `notify.enabled=true` 且通知失败

### 8.2 回退动作

1. 原参数重试 1 次
   - 手动模式：人工等待 5 秒后再试
   - 调度模式：由执行器（主 cc `executeTask(...)`）等待 5 秒后自动重试
2. 仍失败 -> 调用 `fallback_skill`（若 `fallback_skill=none` 则跳过此步）
3. 仍失败 -> `tell-me` 红卡

### 8.3 幂等规则

- “有效产物”= 必需字段非空 + 满足 acceptance。
- 已有有效产物：重试不得覆盖。
- 产物无效：使用 `-retryN` 后缀（N 从 1 递增）。

### 8.4 红卡格式

- 标题：`【模板执行失败】{template_id}`
- 内容：失败步骤 / 关键报错 / 建议动作 / 时间戳
- 颜色：`red`

---

## 9. 验收标准（固定口径）

### 9.1 单模板验收

每条模板满足：
1. 完整性：所有 required outputs 存在
2. 质量性：关键字段非空
3. 可追踪：记录执行时间、入口 skill、失败点（若有）

### 9.2 关键字段口径

- content：标题 / 正文 / 结论
- collect：摘要 / 来源链接 / 行动项
- dev：改动点 / 验证步骤 / 结果结论
- general：任务 ID / 触发时间 / 状态

### 9.3 全局验收

- 抽样 4 条模板（四类各 1）
- 每条执行 1 次
- v1 通过标准：**4/4 全部通过（100%）**

---

## 10. 与既有治理项联动（c5~c11）

v1 不重实现治理项，仅做“验收证据引用”。

- **强制项（v1 验收门槛）**：仅 `tpl-collect-*` 绑定 `c9~c11`
- **参考项（非门槛）**：`c5~c8` 作为可观测增强项，缺失不阻断模板验收

| 项 | 性质 | 验证证据 |
|---|---|---|
| c5 模型路由 | 参考项 | 执行日志里有模型选择记录 |
| c6 计费看板 | 参考项 | `0-System/cost-log.jsonl` 有新增记录 |
| c7 失败回退 | 参考项 | 失败案例有重试/降级记录（注：模板执行是否回退以第 8 章为硬规则） |
| c8 响应缓存 | 参考项 | 幂等任务有 cache hit 记录 |
| c9 来源白名单 | 强制项（collect） | 采集日志有过滤统计 |
| c10 引用溯源 | 强制项（collect） | 简报关键条目含来源链接 |
| c11 安全过滤 | 强制项（collect） | 过滤日志有命中记录 |

`tpl-collect-*` 必须通过 c9~c11，其他类别模板不以 c5~c11 作为阻断门槛。

---

## 11. 风险与缓解

1. 模板触发冲突
   - 缓解：固定优先级 + 回问 + 稳定默认（id 字典序）
2. 输出标准不一致
   - 缓解：模板层统一 outputs + acceptance
3. 成本链路误用
   - 缓解：输入校验 + fallback 降级

---

## 12. 下一步

1. 生成 `0-Skill-Platform/mycc-scenario-templates-v1.yaml`（10 条完整定义）
2. 抽样执行 4 条模板并记录通过率
3. 根据失败点迭代 v1.1
