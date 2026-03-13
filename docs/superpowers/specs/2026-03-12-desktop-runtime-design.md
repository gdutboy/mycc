# Desktop 通用执行器架构设计

- 日期：2026-03-12
- 主题：desktop skill 通用执行器架构
- 状态：已批准，待规格审查

## 1. 背景与目标

当前 `.claude/skills/desktop/desktop.py` 已具备截图、OCR、鼠标键盘控制、窗口激活等能力，并带有微信专用脚本，但整体仍偏向“OCR 驱动的桌面工具箱”，尚未形成统一、可扩展、可调试的通用桌面执行底座。

本设计目标是将 desktop skill 升级为：

> 一个 Hybrid-first 的通用桌面原子执行器。
>
> 以文字目标为主抽象，对外暴露稳定的 primitive API，内部按动作类型在 OCR / UIA / 其他后端之间路由，返回统一结果模型，并为上层应用自动化提供可验证、可调试、可扩展的底座。

## 2. 非目标

第一阶段明确不做以下内容：

- 自学习 selector
- 历史 UI 记忆
- 自动规划多步任务
- 复杂模板匹配体系
- 跨应用事务回滚
- 自适应视觉 grounding
- 自动推断复杂业务意图
- 大量应用专用高层 API

本阶段重点只放在：

- 统一 primitive 接口
- 统一 backend 调度
- 统一结果模型
- 统一 debug 机制
- 为应用扩展预留干净边界

## 3. 架构定位

desktop 应被定义为桌面自动化的 primitive runtime，而不是聊天机器人专用内核，也不是具备完整规划能力的桌面“大脑”。

它的职责是：

- 提供稳定的原子能力
- 接收文字目标并完成识别、定位、读取、点击、输入、等待、验证
- 对底层 OCR / UIA / 模板识别差异进行封装
- 为上层 workflow、skill、应用专用脚本提供统一能力底座

## 4. 总体架构

### 4.1 分层结构

#### L1. Primitive API 层
对外暴露稳定的原子接口：

- `activate_window`
- `capture_region`
- `find`
- `find_in_region`
- `read`
- `read_region`
- `click`
- `type`
- `assert`
- `wait_target`
- `wait_disappear`

这是唯一允许上层 skill / agent / workflow 直接依赖的公共层。

#### L2. Resolver / Router 层
负责：

- 解析目标表达（默认以文字目标为中心）
- 根据动作类型选择识别 backend
- 统一结果格式
- 组织 fallback 流程
- 输出 debug 信息

#### L3. Backend 层
初期定义三类 backend：

- OCR backend
  - 截图
  - OCR 识别
  - 文本定位
  - bbox / center 返回
- UIA backend
  - 找窗口
  - 找控件
  - 读取 name / role / bounds
  - 支持结构化控件操作
- Template backend
  - 第一阶段只定义接口
  - 后续支持图标 / 模板匹配

#### L4. Device / OS Adapter 层
统一封装底层库与操作系统能力：

- screenshot
- mouse / keyboard / clipboard
- window 枚举与激活
- Windows 特有能力适配

避免 `pyautogui`、`pygetwindow`、截图逻辑散落在各处。

### 4.2 核心设计原则

1. **文字目标优先**
   - 默认目标表达为简单字符串，如“发送”“张三”“搜索”。
2. **动作决定识别策略**
   - 不使用单一固定 backend 优先级，而是按动作语义分流。
3. **区域优先于全屏**
   - 优先当前窗口、指定区域、推断子区域，最后才回退全屏。
4. **结果必须标准化**
   - 无论 backend 来源如何，都输出统一 target/result 结构。
5. **执行与验证分离**
   - `click` 不隐式承担成功验证；验证由 `assert` / `wait_*` 显式完成。

## 5. Primitive API 设计

第一阶段固定 11 个原子接口。

### 5.0 通用约定

除非特别说明，所有 primitive 共享以下通用约定：

- `debug: bool = false`
  - `false`：返回简洁结果
  - `true`：返回完整诊断信息
- `timeout_ms: int | null = null`
  - 仅对等待类接口强制生效；其他接口可忽略或用于内部超时控制
- `region: [x, y, width, height] | null = null`
  - 仅对支持区域范围的接口有效
  - 若提供 `region`，则四个值都必须是数字，且 `width > 0`、`height > 0`
  - 若 `region` 结构非法、宽高非正数，或无法映射为有效屏幕矩形，则返回 `invalid_region`
  - 第一阶段对越出屏幕边界的 region 允许执行裁剪；仅当裁剪后无有效面积时返回 `invalid_region`
- `hints: object | null = null`
  - 用于传入 role、window、backend 偏好等高级提示
- `safety: { level?: "green" | "yellow" | "red", confirm_required?: bool, dangerous?: bool, confirmed?: bool } | null = null`
  - 绿色读操作默认 `confirm_required=false`
  - 黄色写操作默认 `confirm_required=false`
  - 红色风险动作默认 `confirm_required=true`
  - 当 `confirm_required=true` 且 `confirmed!=true` 时，执行类接口必须返回 `unsafe_action`
  - 当 `confirmed=true` 时，允许继续执行，并在返回中保留风险标记上下文
  - 第一阶段仅执行类接口真正消费 `safety` 字段；只读类可透传但不触发拦截

### 5.1 窗口类
- `activate_window(title, debug=false)`
- `capture_region(region?, debug=false)`

### 5.2 定位类
- `find(text, region?, hints?, debug=false)`
- `find_in_region(text, region, hints?, debug=false)`

### 5.3 读取类
- `read(region?, hints?, debug=false)`
- `read_region(region, hints?, debug=false)`

### 5.4 执行类
- `click(target_or_xy, debug=false, safety?)`
- `type(text, clear=false, debug=false, safety?)`

### 5.5 验证类
- `assert(text, region?, mode='contains', hints?, debug=false)`
- `wait_target(text, region?, timeout_ms=3000, interval_ms=300, hints?, debug=false)`
- `wait_disappear(text, region?, timeout_ms=3000, interval_ms=300, hints?, debug=false)`

### 5.6 API 契约表

| 接口 | 主要输入 | 默认行为 | 成功返回最小字段 | 失败返回最小字段 | 副作用 |
|------|----------|----------|------------------|------------------|--------|
| `activate_window` | `title` | 标题模糊匹配并激活窗口 | `ok`, `action`, `window` | `ok=false`, `action`, `reason`, `message`, `context` | 改变前台窗口 |
| `capture_region` | `region?` | 截图指定区域，无区域则活动窗口优先 | `ok`, `action`, `image` 或 `image_path` | 同上 | 无 |
| `find` | `text`, `region?`, `hints?` | 文字目标定位 | `ok`, `action`, `target`, `center`, `bbox` | 同上 | 无 |
| `find_in_region` | `text`, `region`, `hints?` | 仅在指定区域定位 | `ok`, `action`, `target`, `center`, `bbox` | 同上 | 无 |
| `read` | `region?`, `hints?` | 读取活动窗口或指定区域 | `ok`, `action`, `text` | 同上 | 无 |
| `read_region` | `region`, `hints?` | 读取指定区域 | `ok`, `action`, `text` | 同上 | 无 |
| `click` | `target_or_xy` | 执行单击，不隐式验证结果 | `ok`, `action`, `point` | 同上 | 鼠标点击 |
| `type` | `text`, `clear?` | 对当前焦点输入文本 | `ok`, `action` | 同上 | 输入/剪贴板 |
| `assert` | `text`, `region?`, `mode` | 基于读取结果断言文本 | `ok`, `action`, `matched` | 同上 | 无 |
| `wait_target` | `text`, `region?`, `timeout_ms`, `interval_ms` | 轮询等待目标出现 | `ok`, `action`, `matched` | 同上 | 无 |
| `wait_disappear` | `text`, `region?`, `timeout_ms`, `interval_ms` | 轮询等待目标消失 | `ok`, `action`, `matched` | 同上 | 无 |

### 5.7 第一阶段暂不纳入的接口

以下能力明确延后：

- drag
- scroll
- hover
- select_menu
- upload_file
- double_click_text
- right_click_text
- `press`
- `hotkey`

说明：

- `press` 与 `hotkey` 当前在旧脚本中存在，但第一阶段不纳入统一 primitive 契约，避免 API 面过早膨胀。
- 若上层确有需要，可先继续由适配层或旧 CLI 兼容命令提供，待第二阶段再决定是否上升为标准 primitive。

原因是第一阶段应优先把“找 / 读 / 点 / 输 / 等 / 验证”这条主链路做稳。

## 6. 数据模型与返回格式

### 6.1 统一目标模型（内部）

```json
{
  "text": "发送",
  "role": "button",
  "bbox": [480, 300, 80, 36],
  "center": [520, 318],
  "backend": "ocr",
  "score": 0.92,
  "window": "QQ",
  "region": [300, 200, 900, 700],
  "meta": {}
}
```

字段说明：

- `text`：识别到的文本
- `role`：控件角色，OCR 可为空，UIA 常有值
- `bbox`：矩形范围
- `center`：中心点
- `backend`：`ocr` / `uia` / `template`
- `score`：匹配分数
- `window`：所属窗口
- `region`：检索区域
- `meta`：backend 专有扩展信息

### 6.2 标准返回策略

采用“默认简洁、debug 详细”的双模式返回。

### 6.3 成功 / 失败 Schema 约定

为保证上层调用稳定，第一阶段所有 primitive 必须满足以下最小 schema：

#### 成功返回最小字段

```json
{
  "ok": true,
  "action": "find"
}
```

在此基础上，按动作补充 action-specific 字段：

- `activate_window`：`window`
- `capture_region`：`image` 或 `image_path`
- `find` / `find_in_region`：`target`, `center`, `bbox`
- `read` / `read_region`：`text`
- `click`：`point`
- `type`：可选 `input_length`
- `assert` / `wait_*`：`matched`

#### 失败返回最小字段

```json
{
  "ok": false,
  "action": "find",
  "reason": "not_found",
  "message": "target text not found",
  "context": {}
}
```

失败时要求：

- `reason` 必填，且必须来自标准枚举
- `message` 必填，用于人类可读解释
- `context` 必填，至少包含 window / region / backend_attempts 中可获得的信息

#### debug 扩展字段

仅在 `debug=true` 时允许出现以下扩展字段：

- `backend`
- `matches`
- `chosen`
- `timing_ms`
- `fallback_chain`
- `screenshots`
- `raw_backend_result`

默认模式不返回这些诊断字段，避免输出膨胀。

#### reason 标准枚举

第一阶段统一使用以下失败原因：

- `not_found`
- `ambiguous_target`
- `backend_unavailable`
- `window_not_found`
- `timeout`
- `unsafe_action`
- `invalid_region`
- `invalid_argument`

#### 候选与最终命中规则

- `matches` 表示当前 backend 返回的原始候选集合，仅在 debug 模式暴露
- `chosen` 表示 router 最终选择的候选，仅在 debug 模式暴露
- 默认模式下，成功只返回最小必要字段，不暴露 `matches` / `chosen`
- 第一阶段 **不做跨 backend score 直接比较**；只允许在单 backend 内排序，backend 之间靠动作路由和 fallback 顺序决策

#### 默认返回示例

所有成功返回在默认模式与 debug 模式下都必须包含 `ok` 与 `action`；debug 模式只是在此基础上追加诊断字段，不改变最小成功 schema。

`find("发送")`

```json
{
  "ok": true,
  "action": "find",
  "target": "发送",
  "center": [520, 318],
  "bbox": [480, 300, 80, 36]
}
```

`read_region(...)`

```json
{
  "ok": true,
  "action": "read_region",
  "text": "张三\n你好"
}
```

`assert("发送成功")`

```json
{
  "ok": true,
  "action": "assert",
  "matched": true
}
```

#### 默认失败示例

```json
{
  "ok": false,
  "action": "find",
  "reason": "not_found",
  "message": "target text not found",
  "context": {
    "window": "QQ",
    "region": [300, 200, 900, 700],
    "backend_attempts": ["ocr", "uia"]
  }
}
```

#### debug 成功示例

```json
{
  "ok": true,
  "action": "find",
  "backend": "ocr",
  "target": "发送",
  "region": [300, 200, 900, 700],
  "matches": [
    {
      "text": "发送",
      "bbox": [480, 300, 80, 36],
      "center": [520, 318],
      "score": 0.92,
      "role": null
    },
    {
      "text": "发送给朋友",
      "bbox": [700, 450, 120, 32],
      "center": [760, 466],
      "score": 0.61,
      "role": null
    }
  ],
  "chosen": {
    "text": "发送",
    "bbox": [480, 300, 80, 36],
    "center": [520, 318],
    "score": 0.92
  },
  "timing_ms": 428
}
```

#### 确认后放行成功示例

```json
{
  "ok": true,
  "action": "click",
  "point": [520, 318],
  "context": {
    "safety_level": "red",
    "dangerous": true,
    "confirm_required": true,
    "confirmed": true
  }
}
```

#### debug 失败示例

```json
{
  "ok": false,
  "action": "click",
  "reason": "unsafe_action",
  "message": "confirmation required before dangerous action",
  "context": {
    "requires_confirmation": true,
    "safety_level": "red",
    "backend_attempts": []
  },
  "timing_ms": 12
}
```

## 7. 路由与动作分流规则

### 7.1 `activate_window`
只走窗口层：

- 窗口枚举
- 标题模糊匹配
- 恢复最小化
- 激活前台

不走 OCR 与 UIA 文本识别。

### 7.2 `read` / `read_region`
默认策略：

1. 若 `hints.backend` 明确指定 `uia` 或 `ocr`，则直接使用指定 backend；指定 backend 不可用时返回 `backend_unavailable`，不自动切换到其他 backend
2. 未指定 backend 时，先尝试 UIA 探测
3. 当区域内存在至少 1 个满足以下条件的 UIA 节点时，判定为“可直接读取的 UIA 控件”，UIA 优先：
   - `is_visible=true`
   - `role` 属于 `Edit` / `Text` / `Document` / `ListItem` / `TreeItem` 之一
   - 节点存在 `name` 或 `value` 之一，且标准化后非空
4. 若 UIA 探测未命中符合条件的节点，则回退 OCR

补充约束：

- `read` 在无显式 `region` 时优先读取活动窗口范围
- `read_region` 不得自行修改调用方传入的 region，只允许按 8.1 规则在失败路径向外扩张
- 第一阶段 UIA 读取结果统一折叠为纯文本，不暴露控件树作为默认返回

原因：结构化输入框、列表、树控件适合 UIA；普通页面文案、图片内文本适合 OCR。

### 7.3 `find(text)`
默认策略：

1. 若 `hints` 明确控件类型（如 button/edit/list），则 UIA 优先
2. 若只是裸文本目标，如“发送”，则 OCR 优先
3. OCR 命中后只在 **单 backend 内** 做排序，不与 UIA 分数混算
4. 当 OCR 满足以下任一条件时，判定为“不稳定命中”，转入 UIA fallback：
   - 没有标准化后的 exact match
   - top1 `score < 0.85`
   - top1 与 top2 分差 `< 0.08`
   - 存在 2 个及以上候选在标准化后文本完全相同
5. UIA fallback 后：
   - 若仅有一个候选，直接返回
   - 若仍有多个高相近候选，返回 `ambiguous_target`
6. 多 backend 均失败则返回失败，不盲目执行

补充约束：

- 第一阶段标准化文本仅包含：去首尾空白、全角半角常见空格归一、大小写归一（英文）
- 第一阶段 **不做模糊语义匹配**，例如“发送消息”不会自动等价于“发送”
- 若 `region` 已显式给定，则不得再反向缩小搜索区域，只允许按 8.1 规则向外扩张

### 7.4 `click(target_or_xy)`
支持两种输入：

- 坐标：`click([x, y])`
- 目标：`click(target)`，其中 `target` 至少必须包含 `center: [x, y]`

输入契约：

- 若传入数组，则必须恰好为长度 2 的数字数组 `[x, y]``；否则返回 `invalid_argument`
- 若传入对象，则必须包含 `center` 字段，且 `center` 必须是长度 2 的数字数组；否则返回 `invalid_argument`
- 若对象同时包含 `bbox`、`text`、`backend` 等字段，执行层可透传到 debug/context，但真正执行点击时只消费 `center`
- 第一阶段 `click` 不接受裸字符串目标，不接受 `{x, y}` 结构，也不接受缺少 `center` 的半结构化对象

`click` 本身不负责“找文本”，也不负责业务成功验证。

### 7.5 `type(text, clear=false)`
默认只处理：

- 可选清空
- 文本输入/粘贴
- 返回执行状态

是否先寻找输入框由上层完成。

### 7.6 `assert(text)`
第一阶段支持三种模式：

- `contains`
- `equals`
- `not_contains`

语义约束：

- `assert` 是 **一次性观测**，不自带轮询；若需要等待，必须使用 `wait_target` 或 `wait_disappear`
- `assert` 默认基于 `read` / `read_region` 的最终文本结果判断，不直接复用 `find` 的候选集合
- `contains`：标准化后文本包含目标字符串即成功
- `equals`：标准化后文本与目标字符串完全相等即成功
- `not_contains`：标准化后文本不包含目标字符串即成功
- 第一阶段标准化规则与 7.3 保持一致，不额外引入模糊分词、近义词或 OCR 纠错词典
- `assert` 成功返回 `matched=true`；失败返回 `ok=false`，`reason=not_found`，并在 `context` 中附带实际读取文本摘要

### 7.7 `wait_target` / `wait_disappear`
统一逻辑：

- 按固定 `interval` 轮询
- 超过 `timeout` 返回超时
- 内部复用 `find` / `assert`
- 返回最终观测结果与失败上下文

进一步约定：

- `wait_target` 的成功条件：在超时前任意一次轮询中，若 `hints.wait_mode='read'`，则 `assert(text, mode='contains')` 成功即成功；其余情况统一走定位路径，以 `find(text)` 成功为成功条件
- `wait_disappear` 的成功条件：在超时前任意一次轮询中，当前观测满足“目标不存在”即可成功；第一阶段将“目标不存在”定义为：若 `hints.wait_mode='read'`，则 `assert(text, mode='not_contains')` 成功；其余情况统一走定位路径，以 `find(text)` 返回 `not_found` 为成功条件
- 第一阶段 `wait_disappear` 采用**单次判定成功**策略，不要求连续 N 次失败确认；若后续发现真人桌面场景过于 flaky，再在第二阶段引入稳定窗口参数
- `wait_target` 成功时返回 `matched=true`
- `wait_disappear` 成功时返回 `matched=false`，表示最后一次成功观测中目标已不存在
- `wait_target` / `wait_disappear` 的最后一次观测结果必须写入 `context.last_observation`
- 若超时，统一返回 `ok=false`, `reason='timeout'`
- 第一阶段固定使用轮询模型，不引入事件订阅、窗口消息监听或 UIA watcher
- `interval_ms` 必须满足 `interval_ms >= 100`；否则返回 `invalid_argument`
- `timeout_ms` 必须满足 `timeout_ms >= interval_ms`；否则返回 `invalid_argument`

## 8. 容错与失败恢复

通用执行器不应无脑重试，但应具备轻量恢复能力。

### 8.1 区域回退策略

- 先在指定 region 内查找
- 失败后扩大到活动窗口
- 仍失败再扩大到全屏

### 8.2 backend fallback

- 当调用方**未显式指定** `hints.backend` 时，允许按动作路由规则执行 backend fallback
- 当调用方**显式指定** `hints.backend` 时，必须以该指定为最高优先级；若该 backend 不可用或未命中，直接返回对应失败，不再自动切换到其他 backend
- OCR 失败可尝试 UIA
- UIA 不可用可回退 OCR
- 记录 `backend_attempts`

### 8.3 歧义目标处理

当多个候选结果接近时，不自动拍板，而返回：

```json
{
  "ok": false,
  "action": "find",
  "reason": "ambiguous_target",
  "message": "multiple similar candidates found",
  "context": {
    "backend_attempts": ["ocr", "uia"],
    "candidates": []
  }
}
```

由上层 agent / workflow 做下一步决策。

### 8.4 执行动作不隐式成功

- `click` 后不默认算成功
- `type` 后不默认算业务完成
- 需要上层显式接 `assert` 或 `wait_*`

## 9. Debug 与诊断机制

debug 机制是核心能力，不是附属功能。

### 9.1 `debug=true`
所有 primitive 应支持 debug 模式，返回：

- backend
- region
- timing_ms
- matches
- chosen
- fallback_chain
- failure reason

### 9.2 失败上下文保留

失败时应尽量保留：

- 当前活动窗口
- 使用的 region
- backend 尝试顺序
- 候选数量与 top matches
- 标准化失败原因

必要时支持保存：

- 临时截图
- 标注 bbox 的 debug 图

### 9.3 标准化失败原因

第一阶段失败 reason 的唯一权威枚举定义以 6.3 为准；其他章节不得新增或删减枚举值。

统一使用以下 reason：

- `not_found`
- `ambiguous_target`
- `backend_unavailable`
- `window_not_found`
- `timeout`
- `unsafe_action`
- `invalid_region`
- `invalid_argument`

## 10. 安全边界

primitive 层必须支持风险标记与安全分级。

### 10.1 绿色操作

- screenshot
- OCR
- read
- find
- activate_window
- capture_region

### 10.2 黄色操作

- click
- type
- press
- hotkey

### 10.3 红色操作

- 发消息
- 删除
- 提交
- 支付
- 覆盖文件
- 关闭有未保存内容的窗口

补充约束：

- 第一阶段 primitive 层**不做业务语义自动推断**，不会因为 `click` 的目标看起来像“发送”按钮就自动升级为红色动作
- primitive 层只消费调用方显式传入的 `safety` 参数，并按其执行拦截或放行
- 业务语义级别的红色判定由上层 skill / workflow / 应用编排层负责

primitive 层至少需要支持：

- `dangerous=true`
- `confirm_required=true`
- 风险标记输出

当执行类 primitive 收到 `confirm_required=true` 且当前调用链未提供确认许可时，统一返回：

```json
{
  "ok": false,
  "action": "click",
  "reason": "unsafe_action",
  "message": "confirmation required before dangerous action",
  "context": {
    "requires_confirmation": true,
    "safety_level": "red"
  }
}
```

由上层 skill 或 workflow 决定是否真正继续执行。

## 11. 测试策略

### 11.1 纯单元测试

覆盖不依赖真实桌面的逻辑：

- 路由规则
- 结果标准化
- 区域扩展与收缩
- 分数排序
- 歧义判定
- debug 输出结构

### 11.2 半集成测试

通过 mock backend 输出来验证 primitive 层行为：

- `find` 候选选择逻辑
- `click(result)` 中心点提取
- `wait_target` 的轮询与超时逻辑
- `assert` 的模式判断

### 11.3 真人桌面 smoke test

只保留少量关键链路验证：

- 激活窗口
- 找文字
- 点击
- 输入
- 读取区域
- 等待目标出现 / 消失

### 11.4 第一阶段验收指标

为避免“功能看起来能跑”但缺乏收口标准，第一阶段验收必须落到可观察指标。

#### 接口覆盖验收

- 11 个 primitive 均有独立测试入口
- 每个 primitive 至少覆盖 1 个成功用例与 1 个失败用例
- 所有失败用例都必须验证 `reason` 与 `message` 字段存在
- 等待类接口必须覆盖超时分支与非法参数分支

#### 返回契约验收

- 默认模式下不得泄露 `matches`、`chosen`、`raw_backend_result` 等 debug 字段
- `debug=true` 时必须返回 `backend` 与至少一种诊断字段（`matches` / `fallback_chain` / `timing_ms`）
- 同一类失败在不同 backend 下必须落到同一组 reason 枚举，不允许 backend 自定义 reason 污染公共契约

#### 稳定性验收

- 对纯单元测试与 mock 半集成测试，连续执行 20 次必须 20 次通过
- 对真人桌面 smoke test，连续执行 10 次，允许最多 1 次因外部桌面抖动失败；超过即判定为 flaky
- 若某条 smoke case 需要人工重新聚焦窗口、手动调整分辨率或临时关闭动画后才通过，不计入“通过”，应判定为环境敏感用例

#### 性能边界验收

第一阶段不追求极致性能，但必须满足以下上界：

- 单次 `find` / `read` 在活动窗口区域内的 median 响应时间目标为 `<= 800ms`
- `debug=true` 相比默认模式允许变慢，但 median 不应超过默认模式的 `2x`
- `wait_*` 在超时前的实际轮询次数误差不得超过 `±1` 次
- `timeout_ms=3000, interval_ms=300` 时，整体返回时间应落在 `3000ms ~ 3400ms` 范围内

说明：

- 以上性能指标主要用于发现明显回退，不作为跨机器绝对 benchmark
- 真人桌面测试记录必须同时保存机器配置、分辨率、缩放比与目标应用版本

#### 安全边界验收

- 绿色读操作不得因为 `safety` 缺失而失败
- 黄色/红色执行操作在 `confirm_required=true` 时必须显式返回待确认状态或 `unsafe_action`，不得直接执行
- 风险标记必须能传递到上层 workflow，不能在 primitive 层吞掉

## 12. 应用扩展原则

应用专用能力必须建立在 primitive 之上，不允许反向污染底层。

建议按应用独立组织：

```text
apps/wechat/
apps/qq/
apps/feishu/
```

应用层只负责：

- 业务步骤编排
- 应用特定 hints / region
- 少量应用规则

例如 QQ 发送消息，应由应用层用 primitive 组合完成，而不是在底层增加 `send_qq_message` 之类的特化接口。

### 12.1 兼容迁移计划

第一阶段不要求一次性推倒旧 CLI 与现有微信脚本，而采用“runtime 先落地，应用层逐步迁移”的策略。

#### 迁移阶段 1：保留旧入口，内部抽公共能力

目标：不打断现有使用方式。

- `desktop.py` 现有 CLI 参数继续保留
- 把截图、OCR、窗口激活、鼠标键盘控制逐步抽到 `adapters/` 与 `backends/`
- 旧命令仍可直接调用，但底层尽量复用新的 runtime 组件

这一阶段允许出现“双入口、同底层”的过渡形态。

#### 迁移阶段 2：为 primitive 提供稳定调用面

目标：让新脚本优先面向 primitive 编写。

- 在 `core/executor.py` 暴露统一 primitive 调用接口
- CLI 层从“直接拼底层库调用”转为“薄封装到 primitive”
- 新增能力只允许落在 primitive/runtime 层，不再向旧脚本追加同类实现

验收标准：新增一个应用动作时，至少 80% 逻辑应通过 primitive 组合完成，而不是在 CLI 分支里重新实现。

#### 迁移阶段 3：迁移微信专用脚本

目标：验证 runtime 能承载真实应用。

- `wechat-read.py` 优先迁移到 `read` / `read_region` + 应用 hints
- `wechat-send.py` 优先迁移到 `find` + `click` + `type` + `assert` / `wait_*` 组合
- `wechat-monitor.py` 继续允许保留旧实现，但新监控逻辑优先调用 primitive

迁移要求：

- 对外 CLI 名称与调用方式尽量不变
- 迁移期间必须保留回退路径，出现阻塞时可暂时回落旧实现
- 回退只允许发生在应用层，不允许绕过公共 safety / result schema

#### 迁移阶段 4：扩展到 QQ / 飞书

目标：证明 runtime 是“通用底座”而非“微信重写工程”。

- QQ / 飞书应用层仅新增编排代码、应用 hints 与少量 region 策略
- 若某应用必须依赖 UIA 专属能力，应通过 backend/hints 扩展，而不是污染 primitive 公共接口
- 只有当两个以上应用都稳定需要同一能力时，才允许讨论把它升级为新的 primitive

#### 迁移矩阵与退役门槛

| 旧入口 | 目标 primitive 组合 | 阶段 | 验收用例 | 回退条件 | 退役条件 |
|------|----------------------|------|----------|----------|----------|
| `desktop.py --find TEXT` | `find(text, region?, hints?)` | 阶段 2 | 指定 3 个典型窗口场景可稳定返回 target/center/bbox | 新 runtime 在真人 smoke 中 flaky > 10% | CLI 默认实现切到 primitive 且连续 2 个版本无回退 |
| `desktop.py --screenshot --ocr` | `capture_region(...)` + `read(...)` | 阶段 2 | 能返回截图产物与文本读取结果 | OCR backend 在目标机器不可用 | 新返回契约被上层消费稳定，旧分支零调用 1 个版本 |
| `desktop.py --activate TITLE` | `activate_window(title)` | 阶段 2 | 模糊匹配激活 3 类窗口成功 | 某类窗口恢复/激活失败率过高 | 默认路径切换后 smoke 连续 10 次通过 |
| `wechat-read.py` | `read_region(...)` / `read(...)` + wechat hints | 阶段 3 | 聊天区读取结果与旧脚本人工比对一致 | UIA/OCR 混合读取导致聊天区文本缺失 | 新实现作为默认路径稳定 2 个版本 |
| `wechat-send.py` | `find` + `click` + `type` + `assert` / `wait_target` | 阶段 3 | 完成“定位联系人→输入→发送→验证”主链路 | 发送验证不稳定或 safety 语义不满足 | 新实现覆盖主流程且旧实现仅保留 emergency fallback |
| `wechat-monitor.py` | `read_region(...)` + `wait_target(...)` + 应用编排 | 阶段 3 | 监控到指定触发词并产出一致事件 | 长轮询导致 CPU/误报不可接受 | 新监控链路稳定运行 1 个版本周期 |

补充规则：

- 每个旧入口切换为新默认实现前，必须至少保留 1 个可人工回退的版本窗口
- 一旦满足退役条件，旧实现应在下一版本删除，而不是长期双轨维护
- 若回退发生，问题归因必须记录到 walkthrough 或后续 findings，避免永久停留在“临时回退”状态

#### 明确不做的兼容承诺

为控制复杂度，第一阶段不承诺以下事项：

- 不保证旧 CLI 输出字段与新 runtime 返回字段完全一致
- 不保证所有历史脚本在未改动的情况下自动享受新 debug schema
- 不为已判定过时的临时脚本提供长期兼容层
- 不为单一应用专门增加“快捷 primitive”

原则是：兼容用户入口，逐步收敛内部实现；不兼容历史技术债。

## 13. 目录结构建议

```text
.claude/skills/desktop/
  desktop.py
  backends/
    ocr_backend.py
    uia_backend.py
    template_backend.py
  core/
    models.py
    router.py
    executor.py
    window.py
    region.py
    safety.py
  adapters/
    screen.py
    input.py
    windows.py
  apps/
    wechat/
      read.py
      send.py
      monitor.py
```

设计要求：

- 通用能力归 `core/` 与 `backends/`
- 操作系统与库适配归 `adapters/`
- 应用逻辑归 `apps/`
- 旧有微信脚本可逐步迁移，不要求一次性重写

## 14. 第一阶段成功标准

### 14.1 通用层
稳定支持以下 11 个 primitive：

- `activate_window`
- `capture_region`
- `find`
- `find_in_region`
- `read`
- `read_region`
- `click`
- `type`
- `assert`
- `wait_target`
- `wait_disappear`

### 14.2 后端层

- OCR backend 可实际可用
- UIA backend 至少具备最小可用版本
- Template backend 保留接口与占位实现

### 14.3 应用层

- 现有微信专用脚本仍可继续工作
- 新架构能逐步承载微信重写
- 为 QQ / 飞书等后续接入留出路径

### 14.4 调试层

- `debug=true` 返回完整候选信息
- 失败可定位 backend、region 与失败原因
- 关键失败可保留截图

## 15. 结论

desktop 的第一阶段演进方向应为：

- **Hybrid-first**
- **原子接口优先**
- **文字目标优先**
- **默认简洁 / debug 详细**
- **按动作类型分流 backend**
- **应用层只做编排，不污染底层**

该设计能够兼容现有 OCR 能力，同时为 UIA 和后续模板匹配留出统一入口，并把 desktop 从“工具脚本集合”升级为“可扩展的桌面自动化底座”。
