# 微信 AI 聊天机器人

基于 **gdutboy/WeChat-MCP-Server** + **智谱 GLM-4-Flash** 的微信 AI 聊天机器人。

## ✨ 功能特点

- ✅ **智能对话** - 调用智谱 GLM-4-Flash 模型
- ✅ **对话记忆** - 支持多轮对话上下文
- ✅ **中文支持** - 完美支持中文输入输出
- ✅ **NT 框架** - 支持微信 4.0+ NT 框架
- ✅ **剪贴板输入** - 避免输入法干扰
- ✅ **交互模式** - 命令行交互式聊天

## 🚀 快速开始

### 1. 安装依赖

```bash
cd C:\Users\gdutb\Desktop\WeChat-AI-Bot
pip install -r requirements.txt
```

### 2. 配置

编辑 `.env` 文件：

```env
ZHIPUAI_API_KEY=你的API密钥
DEFAULT_CONTACT=魔童
MEMORY_SIZE=10
```

### 3. 启动

**方式 1：快捷启动**
```
双击：start.bat
```

**方式 2：测试模式**
```
双击：快速测试.bat
```

**方式 3：命令行**
```bash
# 交互模式
python wechat_ai_bot.py

# 测试模式
python wechat_ai_bot.py --test

# 单次发送
python wechat_ai_bot.py -m "你好"
python wechat_ai_bot.py -c "张三" -m "你好"
```

## 📖 使用方法

### 交互模式

启动后输入消息：

```
> 你好                  # 发送给默认联系人
> 张三 你好              # 发送给指定联系人
> quit                  # 退出
```

### Python 调用

```python
from wechat_ai_bot import WeChatAIBot

bot = WeChatAIBot()

# 发送并获取回复
bot.send_and_reply("魔童", "你好")

# 直接发送
bot.send_message("魔童", "测试消息")
```

## 🔧 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `ZHIPUAI_API_KEY` | 智谱 API 密钥 | - |
| `ZHIPUAI_MODEL` | 模型名称 | glm-4-flash |
| `DEFAULT_CONTACT` | 默认联系人 | 魔童 |
| `MEMORY_SIZE` | 对话记忆轮数 | 10 |

## ⚠️ 注意事项

1. **微信要求**
   - 微信已登录
   - 微信窗口可见（不要最小化）
   - 仅支持 Windows 系统

2. **使用限制**
   - 不要频繁发送消息
   - 不要用于群发广告
   - 遵守微信使用条款

## 🐛 故障排除

### 找不到微信窗口
- 确保微信已启动
- 检查微信窗口是否可见

### 消息发送失败
- 检查联系人名称是否正确
- 确保联系人在最近聊天列表

### AI 调用失败
- 检查 API KEY 是否正确
- 检查网络连接

---

**基于项目**：[gdutboy/WeChat-MCP-Server](https://github.com/gdutboy/WeChat-MCP-Server)

**AI 模型**：[智谱 GLM-4-Flash](https://open.bigmodel.cn/)
