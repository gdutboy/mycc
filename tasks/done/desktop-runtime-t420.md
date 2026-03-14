# [dev] desktop-runtime-t420

## 原始需求
- 执行 T-420：实现 desktop runtime 的 flow 最小骨架
- 先澄清边界，再写失败测试和最小实现
- 范围：`.claude/skills/desktop/core/flow.py`、`.claude/skills/desktop/flows/`、`.claude/skills/desktop/tests/`

## 进度
- [x] 创建任务文档
- [x] 澄清本轮边界
- [x] 写 flow 测试文件
- [x] 测试自检
- [x] 跑失败测试
- [x] 写最小实现
- [x] 跑通过测试

## 当前边界
- 本轮 flow 只做流程编排骨架，不做文件加载
- 先只支持内存中的 Python `steps` 定义
- 只支持四类 step：`click`、`type`、`press`、`wait`
- 失败策略为遇错即停，返回失败 step 索引、动作名和原始错误结果
- 本轮不做条件分支、重试、变量上下文、错误恢复

## 计划测试点
- 成功路径：按顺序执行 `click -> type -> press -> wait`
- 失败路径：某一步返回 `ok=False` 时立即停止，后续 step 不再执行
- 非法动作：`action` 不在白名单时返回 `unsupported_action`

## 当前进度备注
- flow 最小骨架已完成：`core/flow.py` 已支持 `click/type/press/wait` 四类动作、失败即停、非法动作保护
- `flows/__init__.py` 已导出 `run_flow`
- flow 单测已通过：`.claude/skills/desktop/tests/test_flow.py` 共 3 个 case 全绿
- `/test-review` 已完成自检，本轮 spec 范围内通过
- 下一步建议：先做 T-417，把 `desktop.py` 收口到 runtime 薄封装，再继续微信脚本迁移
