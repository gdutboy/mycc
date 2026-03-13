---
name: mycc
description: Use when 用户要启动、重启或排查 mycc 手机端远程访问服务时触发，如启动远程访问、查看连接信息、处理连不上问题；不用于首次初始化配置、普通代码开发或只解释 mycc 是什么的场景
---

# mycc

## 执行步骤

### 1. 检查是否已在运行

```bash
netstat -ano | findstr :18080
```

如果端口已占用 → 直接跳到**第 4 步**读取连接信息。

### 2. 启动后端（后台运行）

```bash
npx tsx .claude/skills/mycc/scripts/src/index.ts start
```

使用 `run_in_background: true`。

### 3. 等待启动

```bash
sleep 5
```

### 4. 读取连接信息并告知用户

```bash
cat .claude/skills/mycc/current.json
```

告知用户：配对码（pairCode）、访问 https://mycc.dev 输入配对。

## 启动失败？

读取详细文档排查：`.claude/skills/mycc/TROUBLESHOOT.md`
