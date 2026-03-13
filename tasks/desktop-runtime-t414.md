# [dev] desktop-runtime-t414

## 原始需求
- 执行 T-414：落地 OCR / UIA / template backend 最小实现
- 先写失败测试，再补最小实现
- 范围：`.claude/skills/desktop/backends/`、`.claude/skills/desktop/tests/`

## 进度
- [x] 创建任务文档
- [x] 澄清本轮边界
- [x] 写 backend 测试文件
- [x] 测试自检
- [x] 跑失败测试
- [x] 写最小实现
- [x] 跑通过测试

## 当前边界
- 本轮先落地 `OCRBackend`、`UIABackend`、`TemplateBackend` 三个最小 backend
- `OCRBackend` 先提供 `find()` / `read()`，输出标准化 matches，不做跨 backend 打分
- `UIABackend` 先支持可见节点读取、按 `hints.role` 过滤、bounds 转 `bbox` / `center`
- `TemplateBackend` 先做占位实现，返回 `backend_unavailable`
- 本轮不做 router / executor / watcher / 缓存 / 事件订阅

## 计划测试点
- OCR：命中目标时返回标准化 match；read 聚合文本；空结果时返回空列表
- UIA：read 优先可见文本节点；find 可按 role hint 过滤并返回标准化坐标
- Template：find/read 明确返回 `backend_unavailable`

## 本轮结果
- 新增 `backends/__init__.py`、`ocr_backend.py`、`template_backend.py`、`uia_backend.py`
- 新增 backend 测试：`test_ocr_backend.py`、`test_uia_backend.py`
- 已执行 RED：pytest 收集阶段失败，原因为 `backends` 模块不存在
- 已执行 GREEN：`python -m pytest .claude/skills/desktop/tests/test_ocr_backend.py .claude/skills/desktop/tests/test_uia_backend.py -v`，结果 `10 passed`
- 用户已手动验收通过，本轮 T-414 backend 最小实现收口完成
