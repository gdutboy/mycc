# WeChat AI Assistant - 微信智能助手项目

> **版本**: v1.0 规划
> **日期**: 2026-03-09
> **目标**: 整合 WeChatBot + WeChat-MCP-Server，打造功能完备的微信 AI 助手
> **核心原则**: 可用性优先、渐进式迭代

---

## 📌 项目概述

### 背景

| 来源项目 | 核心能力 | Star |
|---------|---------|------|
| [WeChatBot](https://github.com/1052666/WeChatBot) | 智能回复、图片识别、情绪回复、记忆功能 | 2 |
| [WeChat-MCP-Server](https://github.com/1052666/WeChat-MCP-Server) | MCP 协议封装、定时发送、多快捷键 | 21 |

### 目标

1. **基础能力**：保留现有 wechatbot skill 的 OCR + AI 回复功能
2. **增强能力**：整合图片/表情识别、情绪回复
3. **扩展能力**：MCP 协议支持、定时任务
4. **记忆能力**：对话历史记忆与总结

---

## 🏗️ 系统架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                   WeChat AI Assistant                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 2: 应用层                                            │
│  ├─ Run.exe (WeChatBot 核心)                               │
│  ├─ MCP Server (符合 Model Context Protocol)                │
│  └─ 配置管理                                                │
│                                                              │
│  Layer 1: 核心层 (Run.exe)                                  │
│  ├─ 消息监听/收发                                           │
│  ├─ AI 对话 (DeepSeek/GPT/MiniMax)                         │
│  ├─ 图片/表情识别                                           │
│  ├─ 情绪回复                                                │
│  ├─ 记忆系统                                                │
│  └─ 定时任务                                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 功能规划

> Run.exe 已内置 Phase 1-3 的核心功能，只需下载配置即可使用

### Phase 1: 下载 Run.exe

| 任务 | 描述 | 优先级 |
|-----|------|--------|
| 下载 Run.exe | 从 WeChatBot 项目下载 Run.exe | P0 |
| 配置 API Key | 配置大模型 API | P0 |
| 运行测试 | 启动测试是否能正常收发消息 | P0 |

### Phase 2: MCP 封装（可选）

| 功能 | 描述 | 优先级 |
|-----|------|--------|
| MCP Server | 将 Run.exe 封装为 MCP 服务 | P1 |
| 定时任务 | 支持定时发送消息 | P1 |

### Phase 3: 定制开发（如需要）

| 功能 | 描述 | 优先级 |
|-----|------|--------|
| 自定义 Prompt | 修改 AI 回复风格 | P2 |
| 特殊功能 | 按需开发 | P2 |

---

## 📁 项目结构

```
wechat-ai-assistant/
├── Run.exe                 # 核心程序（来自 WeChatBot 项目）
├── config.json             # 配置文件
├── prompts/                # AI 提示词
├── logs/                   # 日志目录
├── memory/                 # 记忆存储
├── README.md
└── requirements.txt        # Python 依赖（如需 MCP）
```

---

## 🔧 技术栈

| 层级 | 技术 |
|-----|------|
| 核心程序 | Run.exe（WeChatBot 项目） |
| AI | OpenAI API / DeepSeek API / MiniMax API |
| 协议 | MCP (Model Context Protocol) - 可选封装 |
| 开发语言 | Python（用于 MCP 封装） |

---

## ⚠️ 技术方案说明

**核心技术方案**：直接使用 **Run.exe**（来自 WeChatBot 项目）

| 方案 | 说明 |
|-----|------|
| Run.exe | WeChatBot 项目提供的可执行文件，直接运行即可收发微信消息 |
| 备选：pyautogui + win32gui | 自己实现（如果 Run.exe 不满足需求） |

### 为什么用 Run.exe？

- WeChatBot 项目已实现完整的微信 AI 机器人功能
- 直接下载 Run.exe 即可使用，无需自己开发底层功能
- 项目只需做配置或包装工作

---

## 🚀 下一步

- [ ] 下载 Run.exe
- [ ] 配置 API Key
- [ ] 运行测试
- [ ] 如需要 MCP 封装再开发
