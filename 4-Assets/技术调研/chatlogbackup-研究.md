# chatlogbackup 研究

> 来源：https://github.com/playmobil/chatlogbackup
> 日期：2026-03-10
> 状态：待评估

## 项目简介

微信聊天记录导出工具，支持：
- 多平台：Windows + macOS
- 微信版本：3.x/4.x
- 数据解密：自动解密本地数据库
- MCP 集成：支持 Model Context Protocol
- HTTP API：RESTful 接口

## 核心功能

| 功能 | 说明 |
|------|------|
| 数据解密 | 获取 Data Key 和 Image Key 解密数据库 |
| HTTP API | 查询聊天记录、联系人、群聊等 |
| MCP 集成 | 对接 AI 助手（ChatWise、Cherry Studio） |
| 多媒体 | 图片、视频、语音解密，语音转文字 |
| Webhook | 新消息 HTTP POST 推送 |

## HTTP API 端点

```
GET /api/v1/chatlog      # 聊天记录查询
GET /api/v1/contact      # 联系人列表
GET /api/v1/chatroom     # 群聊列表
GET /api/v1/session      # 最近会话
GET /api/v1/search       # 搜索
GET /api/v1/dashboard    # 汇总统计
GET /image/<id>          # 图片
GET /avatar/<wxid>      # 头像
GET /video/<id>         # 视频
GET /voice/<id>         # 语音（可转文字）
```

## 对现有微信机器人项目的借鉴

### 现状分析

当前 wechatbot skill 使用 **Desktop 方案**：
- OCR 识别屏幕内容
- 鼠标键盘控制微信窗口
- 优点：无需逆向微信
- 缺点：不稳定、速度慢、功能有限

### 可借鉴的设计

| 借鉴点 | 价值 | 复杂度 |
|--------|------|--------|
| **数据库直接访问** | 比 OCR 可靠 100 倍 | 高（需逆向微信） |
| **MCP 协议** | CC 可直接查询微信数据 | 中 |
| **结构化 API** | 更容易做智能分析 | 低 |
| **语音转文字** | 语音消息可解析 | 中 |
| **Webhook** | 实时消息推送 | 低 |

### 短期可参考

1. **API 设计** - 聊天记录查询接口设计
2. **Webhook** - 新消息推送机制
3. **多媒体处理** - 语音转文字流程

### 长期方向

如果能实现数据库直接访问（类似 chatlogbackup），可以：
- 完全脱离 Desktop 方案
- 实现真正的 AI 微信助手
- 支持聊天记录智能分析

## 与现有项目的对比

| 维度 | wechatbot (Desktop) | chatlogbackup |
|------|-------------------|---------------|
| 实现方式 | OCR + 鼠标键盘 | 数据库解密 |
| 稳定性 | 较差 | 较好 |
| 速度 | 慢 | 快 |
| 功能 | 发送/读取消息 | 全文搜索 + AI |
| 依赖 | 微信窗口打开 | 微信运行中 |

## 结论

chatlogbackup 的架构更先进，但需要深入逆向微信数据库。

**可行动项：**
- [ ] 短期：参考 API 设计优化现有 wechatbot
- [ ] 长期：研究数据库直接访问的可能性
