---
name: dashboard
description: Use when 用户要打开或查看 cc 能力看板、skill 列表汇总或平台状态总览时触发；不用于解释某个 skill 的规则、触发词或流程
---

# cc 能力看板可视化

生成好看的 HTML 页面展示 cc 的技能、开发中能力、规划想法。

## 触发词

- `/dashboard`
- "看看能力看板"
- "cc 能力"
- "技能看板"

## 执行

```bash
python3 .claude/skills/dashboard/scripts/visualize.py
```

脚本会：
1. 读取 `.claude/DASHBOARD.md`
2. 解析内容生成 HTML
3. 自动在浏览器打开

## 完成后

告知用户：看板已在浏览器打开。
