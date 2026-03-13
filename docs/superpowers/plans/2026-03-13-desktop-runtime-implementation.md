# Desktop Runtime Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有 `.claude/skills/desktop/desktop.py` 的单文件 OCR 桌面工具，演进为符合已批准 spec 的 Hybrid-first primitive runtime，并保留旧 CLI / 微信脚本的渐进迁移路径。

**Architecture:** 先把现有截图、输入、窗口控制从 `desktop.py` 抽到 adapters，再建立 OCR / UIA / template backends 与 `core/` 下的 models、router、executor。对外先提供稳定的 Python primitive API，再把旧 CLI 和微信脚本改成薄封装，确保兼容入口不变、底层逐步统一。

**Tech Stack:** Python 3、`pyautogui`、`pygetwindow`、`mss`、`Pillow`、`winocr`、Windows UI Automation（新增最小 UIA backend）、`pytest`（新增测试框架）

---

## File Structure

### Existing files to modify

- Modify: `.claude/skills/desktop/desktop.py`
  - 从“大单文件 CLI + 实现”收敛为“CLI 入口 + 兼容命令分发”。
- Modify: `.claude/skills/desktop/SKILL.md`
  - 更新对外调用说明，从旧命令集合补充到 primitive/runtime 视角。
- Modify: `.claude/skills/desktop/REFERENCE.md`
  - 更新兼容命令、primitive 对照表、debug/safety 说明。
- Modify: `.claude/skills/desktop/wechat-read.py`
  - 改为复用 runtime 的 `activate_window` / `read` / `read_region`。
- Modify: `.claude/skills/desktop/wechat-send.py`
  - 改为复用 `find` / `click` / `type` / `assert` / `wait_*`。
- Modify: `.claude/skills/desktop/wechat-monitor.py`
  - 改为复用 `read_region` / `wait_target` / runtime 轮询语义。
- Modify: `.claude/skills/desktop/wechat-autochat.py`
  - 至少把感知/发送动作切到 runtime，避免继续直接操作底层库。

### New runtime files to create

- Create: `.claude/skills/desktop/core/models.py`
  - 统一 target/result/debug/context 数据模型与 reason 常量。
- Create: `.claude/skills/desktop/core/region.py`
  - region 校验、裁剪、活动窗口/全屏回退逻辑。
- Create: `.claude/skills/desktop/core/safety.py`
  - `safety` 解析、确认拦截、风险上下文透传。
- Create: `.claude/skills/desktop/core/router.py`
  - 按动作类型选择 backend、处理 fallback、歧义判定、wait 路径分流。
- Create: `.claude/skills/desktop/core/executor.py`
  - 暴露 11 个 primitive 的统一 Python API。
- Create: `.claude/skills/desktop/core/__init__.py`
- Create: `.claude/skills/desktop/adapters/screen.py`
  - screenshot、活动窗口截图、图像基础预处理。
- Create: `.claude/skills/desktop/adapters/input.py`
  - click/type/press/hotkey/clipboard。
- Create: `.claude/skills/desktop/adapters/windows.py`
  - 列窗、活动窗口、窗口激活、窗口边界读取。
- Create: `.claude/skills/desktop/adapters/__init__.py`
- Create: `.claude/skills/desktop/backends/ocr_backend.py`
  - OCR 读取、定位、候选提取与标准化。
- Create: `.claude/skills/desktop/backends/uia_backend.py`
  - 最小可用 UIA backend：读控件文本、按 hints 查找控件。
- Create: `.claude/skills/desktop/backends/template_backend.py`
  - 第一阶段占位实现，返回 `backend_unavailable` 或空结果。
- Create: `.claude/skills/desktop/backends/__init__.py`

### New tests to create

- Create: `.claude/skills/desktop/tests/conftest.py`
- Create: `.claude/skills/desktop/tests/test_models.py`
- Create: `.claude/skills/desktop/tests/test_region.py`
- Create: `.claude/skills/desktop/tests/test_safety.py`
- Create: `.claude/skills/desktop/tests/test_ocr_backend.py`
- Create: `.claude/skills/desktop/tests/test_uia_backend.py`
- Create: `.claude/skills/desktop/tests/test_router_find.py`
- Create: `.claude/skills/desktop/tests/test_router_read.py`
- Create: `.claude/skills/desktop/tests/test_executor_primitives.py`
- Create: `.claude/skills/desktop/tests/test_cli_compat.py`
- Create: `.claude/skills/desktop/tests/test_wechat_scripts.py`

### New support files to create

- Create: `.claude/skills/desktop/tests/fixtures/`
  - 放 mock backend 输出样例，不放真实截图。
- Create: `.claude/skills/desktop/requirements-dev.txt`
  - 明确测试依赖，至少包含 `pytest`。

---

## Chunk 1: 测试骨架与基础模型

### Task 1: 建立 desktop runtime 测试骨架

**Files:**
- Create: `.claude/skills/desktop/requirements-dev.txt`
- Create: `.claude/skills/desktop/tests/conftest.py`
- Create: `.claude/skills/desktop/tests/test_models.py`
- Create: `.claude/skills/desktop/tests/test_region.py`
- Create: `.claude/skills/desktop/tests/test_safety.py`
- Create: `.claude/skills/desktop/core/__init__.py`
- Create: `.claude/skills/desktop/core/models.py`
- Create: `.claude/skills/desktop/core/region.py`
- Create: `.claude/skills/desktop/core/safety.py`

- [ ] **Step 1: 写 `requirements-dev.txt` 与最小测试入口**

```text
pytest>=8,<9
```

在 `conftest.py` 里准备 mock target/result 工厂，避免每个测试文件重复组装 JSON。

- [ ] **Step 2: 写失败测试，锁定基础契约**

`test_models.py` 至少覆盖：

```python
def test_success_result_keeps_minimum_schema():
    result = success_result("find", target="发送", center=[1, 2], bbox=[0, 0, 2, 2])
    assert result["ok"] is True
    assert result["action"] == "find"
    assert result["target"] == "发送"
    assert "matches" not in result
```

```python
def test_failure_result_always_includes_context():
    result = failure_result("find", "not_found", "target text not found", {})
    assert result == {
        "ok": False,
        "action": "find",
        "reason": "not_found",
        "message": "target text not found",
        "context": {},
    }
```

`test_region.py` 至少覆盖：

```python
def test_invalid_region_when_width_or_height_not_positive():
    with pytest.raises(InvalidRegionError):
        normalize_region([0, 0, 0, 10], [0, 0, 1920, 1080])
```

```python
def test_region_is_clipped_to_screen_bounds():
    assert normalize_region([-10, -10, 30, 30], [0, 0, 100, 100]) == [0, 0, 20, 20]
```

`test_safety.py` 至少覆盖：

```python
def test_confirm_required_blocks_unconfirmed_action():
    result = ensure_action_allowed("click", {"confirm_required": True, "level": "red"})
    assert result["ok"] is False
    assert result["reason"] == "unsafe_action"
```

```python
def test_confirmed_action_passes_with_context():
    context = ensure_action_allowed(
        "click",
        {"confirm_required": True, "confirmed": True, "dangerous": True, "level": "red"},
    )
    assert context == {
        "safety_level": "red",
        "dangerous": True,
        "confirm_required": True,
        "confirmed": True,
    }
```

- [ ] **Step 3: 运行测试，确认全部先失败**

Run:
`python -m pytest .claude/skills/desktop/tests/test_models.py .claude/skills/desktop/tests/test_region.py .claude/skills/desktop/tests/test_safety.py -v`

Expected: FAIL，提示缺少 `core.models` / `core.region` / `core.safety` 或对应函数。

- [ ] **Step 4: 写最小实现**

在 `models.py` 中先实现：
- `REASONS`
- `success_result()`
- `failure_result()`
- `debug_result()` 的最小壳

在 `region.py` 中先实现：
- `InvalidRegionError`
- `normalize_region(region, screen_bounds)`
- `has_positive_area(region)`

在 `safety.py` 中先实现：
- `ensure_action_allowed(action, safety)`
- `normalize_safety_context(safety)`

- [ ] **Step 5: 再跑一次测试，确认转绿**

Run:
`python -m pytest .claude/skills/desktop/tests/test_models.py .claude/skills/desktop/tests/test_region.py .claude/skills/desktop/tests/test_safety.py -v`

Expected: PASS。

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/desktop/requirements-dev.txt .claude/skills/desktop/core/__init__.py .claude/skills/desktop/core/models.py .claude/skills/desktop/core/region.py .claude/skills/desktop/core/safety.py .claude/skills/desktop/tests/conftest.py .claude/skills/desktop/tests/test_models.py .claude/skills/desktop/tests/test_region.py .claude/skills/desktop/tests/test_safety.py
git commit -m "test: add desktop runtime core test harness"
```

### Task 2: 固化 adapters 边界，抽离旧底层能力

**Files:**
- Create: `.claude/skills/desktop/adapters/__init__.py`
- Create: `.claude/skills/desktop/adapters/screen.py`
- Create: `.claude/skills/desktop/adapters/input.py`
- Create: `.claude/skills/desktop/adapters/windows.py`
- Modify: `.claude/skills/desktop/desktop.py`
- Test: `.claude/skills/desktop/tests/test_cli_compat.py`

- [ ] **Step 1: 先写兼容测试，锁定旧行为**

```python
def test_cli_find_uses_runtime_entrypoint(monkeypatch, capsys):
    monkeypatch.setattr(".claude.skills.desktop.desktop.run_find", lambda text, region=None: {"ok": True, "action": "find", "target": text, "center": [10, 20], "bbox": [0, 0, 20, 10]})
    main(["--find", "发送"])
    out = capsys.readouterr().out
    assert '"action": "find"' in out
```

```python
def test_cli_click_still_accepts_xy(monkeypatch, capsys):
    monkeypatch.setattr(".claude.skills.desktop.desktop.run_click", lambda xy: {"ok": True, "action": "click", "point": list(xy)})
    main(["--click", "1", "2"])
    assert '"point": [\n    1,\n    2\n  ]' in capsys.readouterr().out
```

- [ ] **Step 2: 运行兼容测试，确认失败**

Run:
`python -m pytest .claude/skills/desktop/tests/test_cli_compat.py -v`

Expected: FAIL，因为 `desktop.py` 还没有 runtime 风格的入口函数。

- [ ] **Step 3: 抽 adapters，不改行为**

把现有 `desktop.py` 中的这些函数迁移出去：
- `screenshot()` → `adapters/screen.py`
- `move_mouse()` / `click()` / `right_click()` / `type_text()` / `press_key()` / `hotkey()` → `adapters/input.py`
- `list_windows()` / `get_active_window()` / `activate_window()` / 活动窗口 bounds 读取 → `adapters/windows.py`

`desktop.py` 暂时只 import 调用，不改变 CLI 参数名。

- [ ] **Step 4: 为 `desktop.py` 增加薄入口函数**

至少加这些可 monkeypatch 的小入口：
- `run_find(text, region=None)`
- `run_click(xy)`
- `run_activate(title)`
- `run_read(region=None)`

哪怕此时内部仍先调旧逻辑，也要把 CLI 和实现分开。

- [ ] **Step 5: 跑兼容测试**

Run:
`python -m pytest .claude/skills/desktop/tests/test_cli_compat.py -v`

Expected: PASS。

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/desktop/adapters/__init__.py .claude/skills/desktop/adapters/screen.py .claude/skills/desktop/adapters/input.py .claude/skills/desktop/adapters/windows.py .claude/skills/desktop/desktop.py .claude/skills/desktop/tests/test_cli_compat.py
git commit -m "refactor: extract desktop platform adapters"
```

---

## Chunk 2: Backend 与路由核心

### Task 3: 建立 OCR backend 与 template 占位 backend

**Files:**
- Create: `.claude/skills/desktop/backends/__init__.py`
- Create: `.claude/skills/desktop/backends/ocr_backend.py`
- Create: `.claude/skills/desktop/backends/template_backend.py`
- Test: `.claude/skills/desktop/tests/test_ocr_backend.py`

- [ ] **Step 1: 先写 OCR backend 失败测试**

```python
def test_ocr_find_returns_normalized_matches(fake_ocr_result):
    backend = OCRBackend(screen=FakeScreen(), ocr=FakeOCR(fake_ocr_result))
    result = backend.find("发送", region=[0, 0, 100, 100])
    assert result[0]["text"] == "发送"
    assert result[0]["backend"] == "ocr"
    assert result[0]["center"] == [50, 20]
```

```python
def test_template_backend_reports_unavailable():
    backend = TemplateBackend()
    result = backend.find("图标")
    assert result["ok"] is False
    assert result["reason"] == "backend_unavailable"
```

- [ ] **Step 2: 运行测试，确认失败**

Run:
`python -m pytest .claude/skills/desktop/tests/test_ocr_backend.py -v`

Expected: FAIL，backend 类不存在。

- [ ] **Step 3: 写最小 backend 实现**

`ocr_backend.py` 先实现：
- OCR 结果行/词 → 标准 `matches`
- 文本标准化（trim / 空格归一 / 英文大小写归一）
- `find()` / `read()` 两个最小入口
- 不做跨 backend 分数比较

`template_backend.py` 先实现占位类：
- `find()` / `read()` 直接返回 `backend_unavailable`

- [ ] **Step 4: 跑测试确认通过**

Run:
`python -m pytest .claude/skills/desktop/tests/test_ocr_backend.py -v`

Expected: PASS。

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/desktop/backends/__init__.py .claude/skills/desktop/backends/ocr_backend.py .claude/skills/desktop/backends/template_backend.py .claude/skills/desktop/tests/test_ocr_backend.py
git commit -m "feat: add desktop ocr backend and template stub"
```

### Task 4: 建立 UIA backend 最小可用版本

**Files:**
- Create: `.claude/skills/desktop/backends/uia_backend.py`
- Test: `.claude/skills/desktop/tests/test_uia_backend.py`

- [ ] **Step 1: 先写 UIA backend 测试**

```python
def test_uia_read_prefers_visible_text_like_controls():
    backend = UIABackend(tree=FakeTree([
        {"role": "Edit", "name": "hello", "value": "", "is_visible": True, "bounds": [0, 0, 10, 10]},
    ]))
    text = backend.read(region=[0, 0, 100, 100])
    assert text == "hello"
```

```python
def test_uia_find_can_filter_by_role_hint():
    backend = UIABackend(tree=FakeTree([
        {"role": "Button", "name": "发送", "is_visible": True, "bounds": [10, 10, 80, 30]},
    ]))
    matches = backend.find("发送", hints={"role": "button"}, region=[0, 0, 100, 100])
    assert matches[0]["role"].lower() == "button"
```

- [ ] **Step 2: 运行测试，确认失败**

Run:
`python -m pytest .claude/skills/desktop/tests/test_uia_backend.py -v`

Expected: FAIL，因为 `UIABackend` 不存在。

- [ ] **Step 3: 写最小实现**

`uia_backend.py` 只做第一阶段需要的最小能力：
- 枚举可见节点
- 读取 `name` / `value`
- role/hints 过滤
- bounds → `bbox` / `center`
- backend 标记为 `uia`

不要在这一任务引入复杂 watcher、事件订阅、树快照缓存。

- [ ] **Step 4: 跑测试确认通过**

Run:
`python -m pytest .claude/skills/desktop/tests/test_uia_backend.py -v`

Expected: PASS。

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/desktop/backends/uia_backend.py .claude/skills/desktop/tests/test_uia_backend.py
git commit -m "feat: add desktop uia backend mvp"
```

### Task 5: 实现 router 的 find/read 路由与 fallback 规则

**Files:**
- Create: `.claude/skills/desktop/core/router.py`
- Test: `.claude/skills/desktop/tests/test_router_find.py`
- Test: `.claude/skills/desktop/tests/test_router_read.py`

- [ ] **Step 1: 先写 `find` 路由测试**

```python
def test_find_prefers_ocr_for_plain_text_targets():
    router = build_router(ocr=FakeOCRBackend(match_score=0.92), uia=FakeUIABackend())
    result = router.find("发送")
    assert result["ok"] is True
    assert result["action"] == "find"
    assert result["bbox"] == [0, 0, 80, 36]
```

```python
def test_find_falls_back_to_uia_when_ocr_top1_score_too_low():
    router = build_router(ocr=FakeOCRBackend(match_score=0.70), uia=FakeUIABackend(single_match=True))
    result = router.find("发送")
    assert result["ok"] is True
    assert result["context"]["backend_attempts"] == ["ocr", "uia"]
```

```python
def test_find_returns_ambiguous_target_for_multiple_close_candidates():
    router = build_router(ocr=FakeOCRBackend(duplicate_exact_matches=True), uia=FakeUIABackend(ambiguous=True))
    result = router.find("发送", debug=True)
    assert result["ok"] is False
    assert result["reason"] == "ambiguous_target"
```

- [ ] **Step 2: 先写 `read` 路由测试**

```python
def test_read_prefers_uia_for_visible_text_controls():
    router = build_router(uia=FakeUIABackend(read_text="hello"), ocr=FakeOCRBackend(read_text="ocr hello"))
    result = router.read(region=[0, 0, 100, 100])
    assert result["text"] == "hello"
```

```python
def test_read_returns_backend_unavailable_when_explicit_backend_missing():
    router = build_router(uia=None, ocr=FakeOCRBackend(read_text="hello"))
    result = router.read(region=[0, 0, 100, 100], hints={"backend": "uia"})
    assert result["ok"] is False
    assert result["reason"] == "backend_unavailable"
```

- [ ] **Step 3: 运行路由测试，确认失败**

Run:
`python -m pytest .claude/skills/desktop/tests/test_router_find.py .claude/skills/desktop/tests/test_router_read.py -v`

Expected: FAIL，因为 router 还不存在。

- [ ] **Step 4: 写最小 router 实现**

按 spec 落下这些硬规则：
- 裸文本 `find` 默认 OCR 优先
- hints 带 role 时 UIA 优先
- OCR exact match / score / top1-top2 差值 / duplicate exact match 阈值判断
- `read` 在无显式 backend 时优先尝试 UIA 探测
- 显式 `hints.backend` 时禁止自动 fallback
- debug 模式补 `backend` / `matches` / `chosen` / `timing_ms` / `fallback_chain`

- [ ] **Step 5: 跑测试确认通过**

Run:
`python -m pytest .claude/skills/desktop/tests/test_router_find.py .claude/skills/desktop/tests/test_router_read.py -v`

Expected: PASS。

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/desktop/core/router.py .claude/skills/desktop/tests/test_router_find.py .claude/skills/desktop/tests/test_router_read.py
git commit -m "feat: add desktop routing and fallback rules"
```

---

## Chunk 3: Executor、CLI 与应用迁移

### Task 6: 实现 11 个 primitive executor API

**Files:**
- Create: `.claude/skills/desktop/core/executor.py`
- Test: `.claude/skills/desktop/tests/test_executor_primitives.py`

- [ ] **Step 1: 先写 executor 测试**

```python
def test_click_rejects_invalid_argument_without_center():
    executor = build_executor()
    result = executor.click({"text": "发送"})
    assert result["ok"] is False
    assert result["reason"] == "invalid_argument"
```

```python
def test_wait_target_uses_read_mode_when_hint_specified():
    executor = build_executor(router=FakeRouter(assert_sequence=[False, True]))
    result = executor.wait_target("发送成功", hints={"wait_mode": "read"}, timeout_ms=300, interval_ms=100)
    assert result["ok"] is True
    assert result["matched"] is True
```

```python
def test_wait_disappear_returns_timeout_with_last_observation():
    executor = build_executor(router=FakeRouter(find_sequence=[{"ok": True}, {"ok": True}, {"ok": True}]))
    result = executor.wait_disappear("发送中", timeout_ms=300, interval_ms=100)
    assert result["ok"] is False
    assert result["reason"] == "timeout"
    assert "last_observation" in result["context"]
```

- [ ] **Step 2: 运行测试，确认失败**

Run:
`python -m pytest .claude/skills/desktop/tests/test_executor_primitives.py -v`

Expected: FAIL，因为 executor 不存在。

- [ ] **Step 3: 写最小 executor**

实现以下 public methods：
- `activate_window`
- `capture_region`
- `find`
- `find_in_region`
- `read`
- `read_region`
- `click`
- `type`
- `assert_`（Python 命名避开关键字，对外 action 仍是 `assert`）
- `wait_target`
- `wait_disappear`

关键要求：
- 成功/失败 schema 必须统一
- `click` 只接受 `[x, y]` 或带 `center` 的对象
- `interval_ms >= 100`
- `timeout_ms >= interval_ms`
- `wait_*` 写入 `context.last_observation`

- [ ] **Step 4: 跑测试确认通过**

Run:
`python -m pytest .claude/skills/desktop/tests/test_executor_primitives.py -v`

Expected: PASS。

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/desktop/core/executor.py .claude/skills/desktop/tests/test_executor_primitives.py
git commit -m "feat: add desktop primitive executor api"
```

### Task 7: 把旧 CLI 改成 runtime 薄封装

**Files:**
- Modify: `.claude/skills/desktop/desktop.py`
- Modify: `.claude/skills/desktop/REFERENCE.md`
- Test: `.claude/skills/desktop/tests/test_cli_compat.py`

- [ ] **Step 1: 先补 CLI 兼容测试**

```python
def test_cli_find_output_uses_standard_schema(capsys):
    main(["--find", "发送"])
    out = capsys.readouterr().out
    assert '"ok": true' in out.lower()
    assert '"action": "find"' in out
```

```python
def test_cli_screenshot_ocr_path_still_works(monkeypatch, capsys):
    monkeypatch.setattr(".claude.skills.desktop.desktop.run_capture_and_read", lambda *args, **kwargs: {"ok": True, "action": "read", "text": "hello"})
    main(["--screenshot", "tmp.png", "--ocr"])
    assert '"text": "hello"' in capsys.readouterr().out
```

- [ ] **Step 2: 运行测试，确认失败**

Run:
`python -m pytest .claude/skills/desktop/tests/test_cli_compat.py -v`

Expected: FAIL，因为 CLI 还在直接调旧函数、输出格式不统一。

- [ ] **Step 3: 改 `desktop.py` 为薄封装**

要求：
- CLI 参数名尽量保持不变
- 内部调用 `core.executor.DesktopExecutor`
- 旧的 `--find` / `--activate` / `--click` / `--type` / `--windows` 等行为继续可用
- 新增 JSON 输出统一层，不再混用裸字符串与 JSON

- [ ] **Step 4: 更新参考文档**

在 `REFERENCE.md` 增加：
- 旧 CLI → primitive 对照表
- debug 模式说明
- safety 确认语义说明
- 不再推荐直接在脚本中复制底层逻辑

- [ ] **Step 5: 跑兼容测试**

Run:
`python -m pytest .claude/skills/desktop/tests/test_cli_compat.py -v`

Expected: PASS。

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/desktop/desktop.py .claude/skills/desktop/REFERENCE.md .claude/skills/desktop/tests/test_cli_compat.py
git commit -m "refactor: route desktop cli through runtime executor"
```

### Task 8: 迁移微信脚本到 primitive 组合

**Files:**
- Modify: `.claude/skills/desktop/wechat-read.py`
- Modify: `.claude/skills/desktop/wechat-send.py`
- Modify: `.claude/skills/desktop/wechat-monitor.py`
- Modify: `.claude/skills/desktop/wechat-autochat.py`
- Test: `.claude/skills/desktop/tests/test_wechat_scripts.py`

- [ ] **Step 1: 先写迁移测试**

```python
def test_wechat_read_uses_read_region(monkeypatch):
    calls = []
    monkeypatch.setattr("wechat_read.executor.read_region", lambda region, hints=None, debug=False: calls.append((region, hints)) or {"ok": True, "action": "read_region", "text": "张三\n你好"})
    output = run_wechat_read()
    assert "张三" in output
    assert calls
```

```python
def test_wechat_send_uses_find_click_type_and_wait(monkeypatch):
    trace = []
    monkeypatch.setattr("wechat_send.executor.find", lambda *a, **k: trace.append("find") or {"ok": True, "action": "find", "center": [1, 2], "bbox": [0,0,1,1], "target": "输入框"})
    monkeypatch.setattr("wechat_send.executor.click", lambda *a, **k: trace.append("click") or {"ok": True, "action": "click", "point": [1, 2]})
    monkeypatch.setattr("wechat_send.executor.type", lambda *a, **k: trace.append("type") or {"ok": True, "action": "type"})
    monkeypatch.setattr("wechat_send.executor.wait_target", lambda *a, **k: trace.append("wait") or {"ok": True, "action": "wait_target", "matched": True})
    run_wechat_send("hello")
    assert trace == ["find", "click", "type", "wait"]
```

- [ ] **Step 2: 运行测试，确认失败**

Run:
`python -m pytest .claude/skills/desktop/tests/test_wechat_scripts.py -v`

Expected: FAIL，因为微信脚本还没切到 runtime。

- [ ] **Step 3: 迁移脚本，但保留 CLI 入口**

迁移原则：
- `wechat-read.py`：区域计算可以保留，但 OCR/读取必须走 `read_region`
- `wechat-send.py`：输入和验证链路必须走 primitive
- `wechat-monitor.py`：轮询框架可保留，但观测动作走 `read_region` 或 `wait_target`
- `wechat-autochat.py`：至少把读取/发送动作统一到 runtime，不再直接 `pyautogui` + `winocr`

- [ ] **Step 4: 跑测试确认通过**

Run:
`python -m pytest .claude/skills/desktop/tests/test_wechat_scripts.py -v`

Expected: PASS。

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/desktop/wechat-read.py .claude/skills/desktop/wechat-send.py .claude/skills/desktop/wechat-monitor.py .claude/skills/desktop/wechat-autochat.py .claude/skills/desktop/tests/test_wechat_scripts.py
git commit -m "refactor: migrate wechat scripts onto desktop primitives"
```

### Task 9: 更新 Skill 文档并做验收验证

**Files:**
- Modify: `.claude/skills/desktop/SKILL.md`
- Modify: `.claude/skills/desktop/REFERENCE.md`
- Test: `.claude/skills/desktop/tests/test_models.py`
- Test: `.claude/skills/desktop/tests/test_region.py`
- Test: `.claude/skills/desktop/tests/test_safety.py`
- Test: `.claude/skills/desktop/tests/test_ocr_backend.py`
- Test: `.claude/skills/desktop/tests/test_uia_backend.py`
- Test: `.claude/skills/desktop/tests/test_router_find.py`
- Test: `.claude/skills/desktop/tests/test_router_read.py`
- Test: `.claude/skills/desktop/tests/test_executor_primitives.py`
- Test: `.claude/skills/desktop/tests/test_cli_compat.py`
- Test: `.claude/skills/desktop/tests/test_wechat_scripts.py`

- [ ] **Step 1: 先补文档测试/检查清单**

准备一个人工核对清单，确保文档包含：
- 11 个 primitive
- 旧 CLI 兼容说明
- yellow / red safety 说明
- debug 返回字段
- 微信脚本迁移后的调用方式

- [ ] **Step 2: 更新 `SKILL.md` 与 `REFERENCE.md`**

至少补这些内容：
- primitive runtime 的定位
- 推荐流程从“截图→找→点→验”升级为“primitive 组合”
- 哪些命令是兼容入口，哪些是新底座能力
- 风险操作需要确认

- [ ] **Step 3: 运行完整测试集**

Run:
`python -m pytest .claude/skills/desktop/tests -v`

Expected: PASS。

- [ ] **Step 4: 做 1 轮 mock 半集成验证**

Run:
`python -m pytest .claude/skills/desktop/tests/test_router_find.py .claude/skills/desktop/tests/test_executor_primitives.py -v`

Expected: PASS，重点确认 fallback / wait / schema。

- [ ] **Step 5: 做真人桌面 smoke checklist（手工）**

验证清单：
- `activate_window`
- `find`
- `click`
- `type`
- `read_region`
- `wait_target`
- `wait_disappear`

记录机器配置、分辨率、缩放比、目标应用版本。

- [ ] **Step 6: Commit**

```bash
git add .claude/skills/desktop/SKILL.md .claude/skills/desktop/REFERENCE.md .claude/skills/desktop/tests
git commit -m "docs: update desktop skill for primitive runtime"
```

---

## Notes for Execution

- 第一阶段不要做的事：
  - 不做自学习 selector
  - 不做历史 UI 记忆
  - 不做模板匹配实装
  - 不做 watcher/event 订阅
  - 不做跨 backend score 混算
  - 不增加新的高层应用专用 primitive

- 实施顺序必须保持：
  1. 先测试骨架与 schema
  2. 再 adapters
  3. 再 backends
  4. 再 router
  5. 再 executor
  6. 最后 CLI 与应用迁移

- 如果 UIA 依赖在目标机器不可用：
  - 允许 UIA backend 先以 mockable MVP 落地
  - 但公共契约、fallback 行为、`backend_unavailable` 语义必须先稳定

- `desktop.py` 过渡期允许“双入口、同底层”，但新增能力只能进 runtime，不再继续往旧直调逻辑里堆实现。

Plan complete and saved to `docs/superpowers/plans/2026-03-13-desktop-runtime-implementation.md`. Ready to execute?
