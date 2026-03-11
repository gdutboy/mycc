# Setup Skill 参考文档

## 文件说明

| 源文件 | 目标文件 | 说明 |
|--------|----------|------|
| `.claude/settings.local.json.example` | `.claude/settings.local.json` | Hooks 配置 |
| `0-System/status.md.example` | `0-System/status.md` | 短期记忆模板 |
| `0-System/context.md.example` | `0-System/context.md` | 中期记忆模板 |

## 步骤 1 失败处理

- Claude Code 未安装 → 引导用户访问 https://docs.anthropic.com/en/docs/claude-code 安装
- 不在项目目录 → 提示用户 `cd` 到 mycc 目录

## 步骤 5 验证命令

```bash
ls -la .claude/settings.local.json
ls -la 0-System/status.md
ls -la 0-System/context.md
grep "{{YOUR_NAME}}" CLAUDE.md || echo "变量已全部替换"
```

## 完成消息模板

```
MyCC 初始化完成！

已完成：
✅ 配置文件已复制
✅ 名字已设置为「{用户名字}」
✅ Hooks 已配置

接下来你可以：
1. 重启 Claude Code（让 Hooks 生效）
2. 开始使用！试试说"今天有什么安排"

提示：
- 编辑 `0-System/status.md` 记录你的每日状态
- 编辑 `0-System/about-me/` 让我更了解你
- 输入 `/dashboard` 查看所有可用能力
```

## 常见问题

**Q: Hooks 没生效**
1. 确认 `.claude/settings.local.json` 存在
2. 重启 Claude Code
3. 检查文件路径是否正确

**Q: 想重新配置**
1. 删除 `.claude/settings.local.json`
2. 重新运行 `/setup`

**Q: 想改名字**
直接编辑 `CLAUDE.md`，把名字改成想要的
