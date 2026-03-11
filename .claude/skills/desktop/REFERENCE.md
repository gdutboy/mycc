# Desktop Skill — 详细参考文档

## 完整命令速查

| 功能 | 命令 |
|------|------|
| 鼠标位置 | `--cursor-pos` |
| 截图 | `--screenshot file.png` |
| OCR 文字 | `--screenshot --ocr` |
| 鼠标附近 OCR | `--cursor` |
| 移动鼠标 | `--move X Y` |
| 点击 | `--click X Y` |
| 双击 | `--double-click X Y` |
| 右键点击 | `--right-click X Y` |
| 输入文字 | `--type TEXT` |
| 按键 | `--press enter` |
| 组合键 | `--hotkey ctrl c` |
| 列出窗口 | `--windows` |
| 激活窗口 | `--activate 窗口名` |
| 查找文字 | `--find TEXT` |
| 活动窗口 | `--active-window` |

## 典型操作示例

### 点击按钮

```bash
python $DESKTOP --screenshot screen.png --ocr
# → 找到 "保存按钮" @ (550, 300)
python $DESKTOP --click 550 300
python $DESKTOP --cursor   # 验证
```

### 文字输入

```bash
python $DESKTOP --click 400 200       # 点击输入框
python $DESKTOP --type "要输入的内容"
python $DESKTOP --press enter
```

### 查找并点击

```bash
python $DESKTOP --find "提交"
# → {"found": true, "center": [550, 300]}
python $DESKTOP --click 550 300
```

### 常用组合键

```bash
python $DESKTOP --hotkey ctrl c   # 复制
python $DESKTOP --hotkey ctrl v   # 粘贴
python $DESKTOP --hotkey alt f4   # 关闭窗口
python $DESKTOP --hotkey ctrl a   # 全选
```

## 微信操控详细说明

### 脚本列表

| 脚本 | 功能 |
|------|------|
| `wechat-read.py` | 读取当前聊天窗口文字 |
| `wechat-read.py --bbox` | 读取文字 + JSON 包围盒坐标 |
| `wechat-send.py "消息"` | 发送消息，自动 OCR 验证 |
| `wechat-send-file.py /path` | 发送文件或图片 |
| `wechat-monitor.py` | 后台监控 @MYCC 触发词 |
| `wechat-monitor.py "关键词"` | 自定义监控关键词 |

### 使用前提

- 微信已打开并停留在目标聊天窗口
- 已安装 Python 依赖

### 关键参数（环境变量覆盖）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `WECHAT_SIDEBAR` | `320` | 侧边栏宽度（图标+联系人列表） |
| `WECHAT_TITLE_H` | `60` | 顶部标题栏高度 |
| `WECHAT_INPUT_H` | `160` | 底部输入框+工具栏高度 |

### 实现细节

- **中文输入**：通过剪贴板粘贴，`--type` 也已改用剪贴板方式
- **坐标动态获取**：每次操作前自动获取窗口位置，不硬编码
- **OCR 验证**：发送后 OCR 输入框，count==0 表示发送成功

## OCR 说明

使用 Windows 10+ 内置 OCR 引擎（通过 `winocr` 调用）：
- 支持中英文识别
- 无需安装额外 OCR 软件
- 全屏识别耗时 0.5–1.5s，局部识别 0.2–0.5s

## 性能参考

| 操作 | 耗时 |
|------|------|
| 鼠标移动/点击 | < 10ms |
| 截图 | ~100ms |
| 全屏 OCR | 0.5–1.5s |
| 局部 OCR | 0.2–0.5s |
| 窗口列表 | < 100ms |

## 安全禁区

- 不操控系统关键窗口（任务管理器、注册表等）
- 不输入密码或敏感凭证
- 不操作支付页面
- 不修改系统设置
- 涉及发消息、删除操作前必须确认

---

*Windows 版 Desktop Skill - 2026-03-09*
