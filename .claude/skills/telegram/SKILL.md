---
name: telegram
description: Telegram Bot 接入 Claude Code，实现 Telegram ↔ CC 双向通信
---

# Telegram Bot 接入 Claude Code

使用 [RichardAtCT/claude-code-telegram](https://github.com/RichardAtCT/claude-code-telegram) 项目（2.1k ⭐）

## 前置准备

1. **安装 Python 3.11+**
2. **安装 Claude Code CLI**
3. **创建 Telegram Bot**：
   - 打开 Telegram，搜索 @BotFather
   - 发送 `/newbot` 创建机器人
   - 获取 Bot Token
4. **获取你的 Telegram 用户 ID**：搜索 @userinfobot

## 安装

```bash
# 使用 uv 安装（推荐）
uv tool install git+https://github.com/RichardAtCT/claude-code-telegram@v1.3.0

# 或使用 pip
pip install git+https://github.com/RichardAtCT/claude-code-telegram@v1.3.0
```

## 配置

```bash
# 创建配置目录
mkdir -p ~/.claude-telegram
cd ~/.claude-telegram

# 复制配置模板
curl -L -o .env.example https://raw.githubusercontent.com/RichardAtCT/claude-code-telegram/main/.env.example
cp .env.example .env

# 编辑配置
nano .env
```

**必填配置：**
```env
TELEGRAM_BOT_TOKEN=你的BotToken
TELEGRAM_BOT_USERNAME=你的机器人用户名
APPROVED_DIRECTORY=C:/Users/gdutb/Desktop/mycc
ALLOWED_USERS=你的Telegram用户ID
```

## 运行

```bash
make run
```

或直接运行：
```bash
python -m claude_telegram
```

## 功能

| 功能 | 描述 |
|------|------|
| AI 对话 | Claude Code SDK/CLI 双支持 |
| 文件处理 | 文件上传、图片分析 |
| Git 集成 | 仓库克隆、分支操作 |
| 会话持久化 | 按用户保存上下文 |
| 安全控制 | 用户白名单、目录隔离 |

## 卸载

```bash
uv tool uninstall claude-telegram
# 或
pip uninstall claude-telegram
```
