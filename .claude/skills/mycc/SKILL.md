---
name: mycc
description: 启动 mycc 小程序后端服务（后台运行）
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
