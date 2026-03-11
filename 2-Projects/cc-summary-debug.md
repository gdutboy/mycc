# CC 汇总信息截断问题故障报告

## 故障概述

团队模式三引擎并行处理中，"CC 汇总"环节失败，无法将多行 prompt 正确传递给子进程 `claude -p`。

## 环境信息

- **平台**：Windows 11 Pro
- **CC 版本**：Claude Code (最新)
- **调用方式**：Node.js `spawn` + PowerShell 管道

## 故障现象

执行 CC 汇总时，子进程 `claude -p` 收到的是被截断的、空的或格式错误的消息，导致：
1. CC 汇总失败，返回错误信息
2. 三引擎并行变成"双引擎"（CC + Codex，Gemini 超时）

## 根因分析

### 问题链路

```
team-engine.ts
  → execWithTimeout('powershell', ['-Command', 'Get-Content file | claude -p'])
    → PowerShell 管道将文件内容传给 claude -p
      → claude -p 无法正确接收管道输入
        → 返回空响应或报错
```

### 已尝试的方案

| 方案 | 实现方式 | 结果 |
|------|----------|------|
| 1. `-p` 直接传多行 | `claude -p "prompt1\nprompt2"` | ❌ 截断 |
| 2. `-f` 文件方式 | `claude -f prompt.txt` | ❌ 用户 CLI 不支持 |
| 3. 单行 `|` 分隔 | `echo "prompt" \| claude -p` | ❌ 超时/无输出 |
| 4. 多行 prompt 参数 | `claude -p "line1\nline2"` | ❌ 截断 |
| 5. PowerShell Get-Content 管道 | `powershell -Command "Get-Content file \| claude -p"` | ❌ 无输出 |

### 验证测试

```bash
# 测试1：直接运行 claude -p（正常）
env -u CLAUDECODE claude -p "Say hello"
# ✅ 返回正常

# 测试2：管道方式（失败）
echo "Hello test" | claude -p
# ❌ 无输出

# 测试3：PowerShell 管道（失败）
powershell -Command "echo 'Hello test' | claude -p"
# ❌ 无输出
```

**结论**：在 Windows 环境下，`claude -p` 无法通过管道接收输入。

## 影响范围

- `/team` 命令的 CC 汇总环节
- 三引擎并行结果的综合分析

## 当前状态

- **三引擎并行**：CC ✅ / Codex ✅ / Gemini ❌ (超时)
- **CC 汇总**：❌ 失败

## 可能的修复方向

1. **用 Codex 代替 CC 做汇总**：Codex 已验证可用
2. **用文件 + 启动脚本**：写 wrapper 脚本用 `--arg` 传 prompt
3. **用 node-pty 代替 spawn**：类似 Gemini 的实现方式，提供真实 TTY

## 相关文件

- `.claude/skills/mycc/scripts/src/engines/team-engine.ts` - 引擎管理器
- `.claude/skills/mycc/scripts/src/channels/feishu-commands.ts` - 飞书集成

---

*记录于 2026-03-11*
