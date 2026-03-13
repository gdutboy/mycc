# 微信 AI 聊天机器人 - 快速设置指南

## ✅ 已完成

1. ✅ 项目已克隆：`C:\Users\gdutb\Desktop\WeChat-AI-Bot`
2. ✅ AI 引擎已配置：智谱 GLM-4-Flash
3. ✅ 微信控制器已就绪：支持 NT 框架
4. ✅ 测试成功：AI 可以生成回复

## 🎯 AI 测试结果

**输入**：你好，这是一条测试消息

**AI 回复**：嗨，这是我的测试回复！看起来你的消息测试很成功哦~ 🎉

## ⚠️ 当前问题

**发送失败**：无法将微信窗口置于前台

**解决方法**：
1. 确保微信已打开
2. **确保微信窗口在前台**（不要最小化，不要被其他窗口遮挡）
3. 再次运行测试

## 🚀 使用方法

### 快速测试

```bash
cd C:\Users\gdutb\Desktop\WeChat-AI-Bot
python wechat_ai_bot.py -m "你好"
```

### 交互模式

```bash
python wechat_ai_bot.py
```

然后输入消息：
```
> 你好                  # 发送给默认联系人（魔童）
> 张三 你好              # 发送给指定联系人
> quit                  # 退出
```

### 测试模式

```bash
python wechat_ai_bot.py --test
```

## 📁 项目文件

| 文件 | 说明 |
|------|------|
| `wechat_ai_bot.py` | 主程序 |
| `ai_engine.py` | AI 引擎 |
| `src/wechat_controller.py` | 微信控制器 |
| `.env` | 配置文件 |
| `start.bat` | 启动脚本 |
| `快速测试.bat` | 测试脚本 |

## 🔧 配置

编辑 `.env` 文件：

```env
# 默认联系人
DEFAULT_CONTACT=魔童

# AI 配置
ZHIPUAI_API_KEY=06a208b9b6be4bb6bc42b097dc00f6b5.IOzAf6mEqeSWMa1o
ZHIPUAI_MODEL=glm-4-flash

# 对话记忆
MEMORY_SIZE=10
```

## ⚠️ 重要提示

1. **微信窗口必须在前台**（不能最小化）
2. 仅支持 Windows 系统
3. 仅支持微信 4.0+ NT 框架版本
4. 不要在运行时操作微信

---

**状态**：✅ AI 工作正常 | ⚠️ 需要微信窗口在前台

**创建时间**：2026-03-05
**基于项目**：gdutboy/WeChat-MCP-Server
