# [dev] desktop-runtime-t416

## 原始需求
- 执行 T-416：实现 executor 的 11 个 primitive 与 safety 校验
- 继续沿用 desktop runtime implementation plan
- 严格按 dev + TDD 流程：先任务文档，再边界确认，再写失败测试，再 test-review，再最小实现
- 范围核心：`.claude/skills/desktop/core/executor.py`、`.claude/skills/desktop/tests/test_executor_primitives.py`

## 进度
- [x] 创建任务文档
- [ ] 澄清本轮边界
- [ ] 写 executor 测试文件
- [ ] 测试自检
- [ ] 跑失败测试
- [ ] 写最小实现
- [ ] 跑通过测试

## 当前边界
- 本轮只做 `Executor` 的最小可用版本，不碰 CLI 和微信脚本。
- 先在 `core/executor.py` 暴露统一 primitive API，作为 runtime 的执行入口。
- 本轮按 implementation plan 先锁定 11 个 primitive：`find`、`read`、`click`、`double_click`、`right_click`、`move`、`type`、`press`、`hotkey`、`assert`、`wait`。
- `find` / `read` / `assert` / `wait` 复用 `Router`；输入类 primitive 通过注入的 input adapter 执行。
- 所有会触发真实动作的 primitive 都先接入 `ensure_action_allowed()`；未确认的红级动作返回 `unsafe_action`，不执行底层 adapter。
- `region` 相关动作先支持透传和标准化入口，不在本轮扩展复杂窗口区域推导。
- `assert` 本轮先实现一次性观测语义：按 mode 走 `find` 或 `read`，失败返回 assertion 失败结果，不做额外轮询。
- `wait` 本轮先作为 `Router.wait()` 的薄封装，负责参数转发与统一动作名，不重复实现轮询。
- 本轮不做复杂 debug 聚合、不做 template backend 专属逻辑、不做批量动作编排。

## 计划测试点
- `find` / `read`：Executor 调用 Router，并把 target / region / hints 原样传递。
- `click` / `type` 等动作：安全校验通过时才调用 input adapter；未确认时返回 `unsafe_action` 且 adapter 零调用。
- `assert`：`mode=find` 成功返回 ok；失败返回统一 assertion 失败结果；`mode=read` 同理。
- `wait`：参数透传到 `Router.wait()`；非法 mode 由 Router 兜底。
- 边界：缺失必须依赖（如无 input adapter 执行 click）时返回统一失败结果而不是抛异常。
