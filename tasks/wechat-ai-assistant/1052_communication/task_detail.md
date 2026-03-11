# 任务详情

## 项目名称
WeChat AI Assistant - 微信智能助手

## 用户需求
整合两个开源项目，开发微信 AI 助手：
1. WeChatBot (https://github.com/1052666/WeChatBot) - 智能回复、图片识别、情绪回复
2. WeChat-MCP-Server (https://github.com/1052666/WeChat-MCP-Server) - MCP 协议、定时发送

## 技术方案
- **核心技术**：wxautox_wechatbot 库直接收发微信消息（不是 OCR）
- **备选方案**：pyautogui + win32gui
- **输入方式**：剪贴板（避免输入法干扰）

## 项目规划
详见：`2-Projects/wechat-ai-assistant.md`

### Phase 1: MVP
- 消息监听
- AI 回复
- 触发词识别
- 冷却机制

### Phase 2: 增强感知
- 图片识别
- 情绪回复

### Phase 3: 记忆系统
- 对话历史
- AI 总结

### Phase 4: 扩展能力
- MCP 协议
- 定时任务

## 当前阶段
确认项目规划，准备开始 Phase 1 开发

## 约束
- 仅支持 Windows
- 需要微信保持运行
- 需要配置 API Key
