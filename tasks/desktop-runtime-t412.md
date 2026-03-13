# [dev] desktop-runtime-t412

## 原始需求
- 执行 T-412：建立 desktop runtime 测试骨架
- 先写失败测试，再补最小实现
- 范围：`.claude/skills/desktop/requirements-dev.txt`、`core/`、`tests/`

## 进度
- [x] 创建任务文档
- [x] 写基础测试文件
- [x] 测试自检
- [x] 安装 pytest
- [x] 跑失败测试
- [x] 写最小实现
- [x] 跑通过测试

## 备注
- 已安装 `pytest 8.4.2`
- 红灯阶段确认失败原因为缺少 `core.models` / `core.region` / `core.safety`
- 当前通过测试：`8 passed`
- 按计划只先覆盖 models / region / safety 三个基础模块
