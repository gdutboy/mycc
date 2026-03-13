# 1052-agent 多通道接入记录

> 创建时间：2026-03-09
> 更新：2026-03-09

---

## 飞书通道 ✅ 已完成

### 最终方案：子进程网关

核心问题：lark SDK 的 `ws.Client.start()` 内部调用 `asyncio.get_event_loop()`，在 uvicorn 环境下会冲突（`This event loop is already running`）。`nest_asyncio` 和 `asyncio.new_event_loop()` 都无法解决。

**解决方案**：用 `subprocess.Popen` 启动独立的 `feishu_gateway.py` 子进程，完全隔离事件循环。

### 架构

```
uvicorn (主进程, 端口 10053)
├── FastAPI 后端 (API + AI 聊天)
│   └── /api/feishu/internal  ← 飞书专用接口，带内容过滤
└── feishu_gateway.py (子进程)
    ├── 飞书 WebSocket 长连接
    ├── 收到消息 → POST /api/feishu/internal
    └── 拿到 AI 回复 → reply 回飞书
```

### 改动的文件

| 文件 | 改动 |
|------|------|
| `backend/feishu_gateway.py` | **新增**，独立子进程，飞书长连接 + HTTP 回调 |
| `backend/app/feishu_bot.py` | 改为子进程方式启动网关 |
| `backend/app/main.py` | 新增 `/api/feishu/internal` 接口，飞书专用 conversation，回复内容过滤 |
| `data/config.json` | 更新飞书凭证 |

### 飞书配置

```json
{
  "feishu_app_id": "cli_a92476ecd3b81bb4",
  "feishu_app_secret": "seGyX3uCtDTcdvLHruDZPcK1YBGfHxe1"
}
```

### 踩过的坑

1. **应用未发布** → 飞书后台保存长连接配置时提示"未检测到应用连接信息"，需要先发布应用
2. **事件循环冲突** → daemon 线程里 `run_until_complete` 和 uvicorn 冲突，子进程彻底解决
3. **subprocess.PIPE 卡死** → 子进程 stdout 被 pipe 缓冲满后阻塞，去掉 pipe 解决
4. **回复内容过滤** → AI 回复包含 `[调用 xxx]` `已成功...` 等工具描述，用正则过滤；注意 `clean_reply or full_reply` 在 clean 为空时会回退到未过滤内容，改为 `if clean_reply else "好的，已处理。"`

### 启动命令

```bash
cd C:/Users/gdutb/Desktop/1052-agent/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 10053
# 飞书网关子进程会自动启动
```

---

## 微信通道 🔲 待开发

### 现有方案

| 方案 | 状态 | 说明 |
|------|------|------|
| Run.exe (WeChatBot) | ❌ 未测试成功 | 基于扫码登录，config.py 配置 API，但还没跑通 |
| wechatbot.py (OCR) | ⚠️ 可用但粗糙 | 截屏 OCR + 模拟键盘，依赖微信窗口在前台 |

### Run.exe 方案问题

- 位置：`C:\Users\gdutb\Desktop\mycc\wechat-ai-assistant\Run.exe`
- config.py 用的 DeepSeek API 格式，需要适配
- **未测试成功，原因待排查**

### 下一步计划

1. 先排查 Run.exe 为什么跑不通
2. 如果 Run.exe 能跑，改 config.py 指向 1052 后端（需要后端兼容 OpenAI 格式，或加一层代理）
3. 如果 Run.exe 不行，考虑用 wechatbot.py 方案改造，调用 `/api/feishu/internal`（改名为 `/api/chat/internal`）

### 参考

- WeChatBot: https://github.com/1052666/WeChatBot
- WeChat-MCP-Server: https://github.com/1052666/WeChat-MCP-Server
- wechatbot.py: `.claude/skills/wechatbot/wechatbot.py`
