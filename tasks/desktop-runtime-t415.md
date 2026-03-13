# [dev] desktop-runtime-t415

## 原始需求
- 执行 T-415：实现 router 的 find/read/wait 动作分流
- 先写失败测试，再补最小实现
- 范围：`.claude/skills/desktop/core/router.py`、`.claude/skills/desktop/tests/test_router_find.py`、`.claude/skills/desktop/tests/test_router_read.py`

## 进度
- [x] 创建任务文档
- [x] 澄清本轮边界
- [x] 写 router 测试文件
- [x] 测试自检
- [x] 跑失败测试
- [x] 写最小实现
- [x] 跑通过测试

## 当前边界
- 本轮先落地 `Router` 最小版本，覆盖 `find()`、`read()`、`wait()` 三类动作分流
- `find()` 先实现：裸文本默认 OCR 优先；`hints.role` 存在时 UIA 优先；显式 `hints.backend` 时仅走指定 backend
- `read()` 先实现：无显式 backend 时 UIA 优先、再 fallback OCR；显式 backend 时禁止自动 fallback
- `wait()` 本轮先做轮询分流壳：按 `mode` 选择 `find` 或 `read` 路径，超时返回统一失败结果
- 本轮不做真实时间统计、复杂 score 排名、watcher、事件订阅、缓存

## 计划测试点
- find：裸文本命中时优先选 OCR；role hint 命中时优先选 UIA；显式 backend 缺失时返回 `backend_unavailable`
- read：默认优先 UIA 文本；显式 backend 缺失时返回 `backend_unavailable`；默认 fallback 到 OCR
- wait：`mode=find` 时轮询 find；`mode=read` 时轮询 read；超时时返回 `timeout`
