# [dev] desktop-runtime-t419

## 原始需求
- 执行 T-419：补齐 desktop runtime 的 scroll 动作
- 先澄清边界，再写失败测试和最小实现
- 范围：`.claude/skills/desktop/core/executor.py`、`.claude/skills/desktop/core/runtime.py`、`.claude/skills/desktop/adapters/input.py`、`.claude/skills/desktop/tests/`

## 进度
- [x] 创建任务文档
- [x] 澄清本轮边界
- [x] 写 scroll 测试文件
- [x] 测试自检
- [x] 跑失败测试
- [x] 写最小实现
- [x] 跑通过测试

## 当前边界
- 本轮 scroll 只做原始输入滚动，不做“滚到目标出现”为止的智能滚动
- 对外接口定为 `scroll(clicks)`，只支持纵向滚动
- 本轮只补 runtime 输入链路：`adapters/input.py` → `core/runtime.py` → `core/executor.py`
- 不扩展到 `desktop.py` CLI，不改微信脚本
- 保持现有 safety 模式，与 click/type/press 一样走 `ensure_action_allowed()`

## 计划测试点
- `Executor.scroll(clicks)` 会先走 safety 校验，再调用 `input_adapter.scroll(clicks)`
- 未注入 `input_adapter` 时返回 `dependency_unavailable`
- `_InputAdapterWrapper.scroll(clicks)` 会把调用转发到 `adapters/input.py`
- `build_executor()` 组装后的 executor 具备可用的 `scroll()` 输入能力
