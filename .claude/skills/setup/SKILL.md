---
name: setup
description: 交互式引导完成 MyCC 初始化配置
---

# MyCC 初始化引导

## 触发条件

- 用户输入 `/setup` 或说"帮我配置"、"初始化"
- 检测到 `CLAUDE.md` 中仍含 `{{YOUR_NAME}}` 时，主动询问是否引导

## 配置进度清单

> 每完成一步打勾，支持中断后继续。

- [ ] 1. 检查前置条件
- [ ] 2. 复制配置文件
- [ ] 3. 收集用户信息
- [ ] 4. 替换模板变量
- [ ] 5. 验证配置生效
- [ ] 6. 完成初始化

## 执行步骤

**步骤 1：检查前置条件**
- 确认 `claude --version` 可执行
- 确认当前目录存在 `CLAUDE.md`
- 失败处理：见 REFERENCE.md

**步骤 2：复制配置文件**
```bash
cp .claude/settings.local.json.example .claude/settings.local.json
cp 0-System/status.md.example 0-System/status.md
cp 0-System/context.md.example 0-System/context.md
```

**步骤 3：收集用户信息**
- 问用户："你希望我怎么称呼你？"
- 记住答案用于下一步

**步骤 4：替换模板变量**
```bash
sed -i '' 's/{{YOUR_NAME}}/用户名字/g' CLAUDE.md
```
- Windows 下去掉 `''`：`sed -i 's/{{YOUR_NAME}}/用户名字/g' CLAUDE.md`

**步骤 5：验证配置**
- 确认三个配置文件存在
- 确认 `CLAUDE.md` 中不再含 `{{YOUR_NAME}}`

**步骤 6：完成初始化**
- 告知用户重启 Claude Code 让 Hooks 生效
- 提示可编辑 `0-System/status.md` 和 `0-System/about-me/`

## 中断与继续

下次触发 `/setup` 时检查清单，从未完成的步骤继续，告知用户："上次配置到步骤 X，要继续吗？"

详细参考：同目录下 REFERENCE.md
