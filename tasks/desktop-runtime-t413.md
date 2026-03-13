# [dev] desktop-runtime-t413

## 原始需求
- 执行 T-413：固化 adapters 边界，抽离旧底层能力
- 先写失败测试，再补最小实现
- 范围：`.claude/skills/desktop/desktop.py`、`adapters/`、`tests/`

## 进度
- [x] 创建任务文档
- [x] 澄清抽离边界
- [x] 写 adapters 测试文件
- [x] 测试自检
- [x] 跑失败测试
- [x] 写最小实现
- [x] 跑通过测试

## 当前边界
- 先抽 `screenshot`、输入控制、窗口控制三类能力
- 本轮先固化 adapter API，不做 router/executor
- CLI 仍可先继续使用旧入口，后续任务再切换到 runtime 薄封装

## 本轮结果
- 新增 `adapters/input.py`、`adapters/screen.py`、`adapters/windows.py`
- `desktop.py` 旧入口已改为委托 adapters，形成可 monkeypatch 的兼容边界
- 修复 import `desktop.py` 时的 stdout 副作用，避免 pytest capture 异常
- 已验证：legacy wrapper 测试 `7 passed`，adapter 测试 `13 passed`
