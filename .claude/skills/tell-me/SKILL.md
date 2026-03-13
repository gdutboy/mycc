---
name: tell-me
description: Use when 用户明确要把结果、结论、错误、进展或提醒推送到飞书时触发；不用于普通对话回复、仅在终端展示结果或尚未决定发送通知的场景
---

# Tell Me - 飞书通知（全平台版）

将当前对话的关键信息发送到飞书群。支持 macOS / Linux / Windows。

## 触发词

- "/tell-me"
- "通知我"
- "飞书通知"
- "告诉我"

## 执行步骤

1. **总结对话**（3-5 句话）
   - 做了什么
   - 结论/结果
   - 下一步（如有）

2. **发送飞书**

## 发送命令

```bash
node /Users/aster/AIproject/mylife/.claude/skills/tell-me/send.js "标题" "内容" [颜色]
```

**参数说明**：
- 标题：卡片标题
- 内容：支持 lark_md 格式，用 `\n` 换行，`**粗体**`、`*斜体*`
- 颜色（可选）：blue（默认）、green、orange、red

**示例**：
```bash
node /Users/aster/AIproject/mylife/.claude/skills/tell-me/send.js "任务完成" "• 完成了 xxx\n• 下一步 yyy" green
```

## 卡片颜色

根据内容性质选择：
- **green**：完成/成功
- **blue**：普通信息
- **orange**：提醒/警告
- **red**：紧急/错误

## 跨平台说明

使用 Node.js 原生 `fetch`（Node 18+），无需额外依赖，三平台通用。
