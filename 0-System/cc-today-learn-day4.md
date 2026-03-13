# CC学习今日内容

> 每天深度更新 | 2026-03-12

---

# Day 4 - 项目探索：Glob + Grep 搜遍全代码

> 目标：像搜索引擎一样快速定位代码

---

## Glob vs Grep 的分工

| 工具 | 功能 | 类比 |
|------|------|------|
| **Glob** | 按文件名/路径模式匹配 | 搜"文件名" |
| **Grep** | 按文件内容匹配 | 搜"文件内容" |

**口诀**：Glob 告诉你"在哪"，Grep 告诉你"是什么"。

---

## Glob 模式详解

### 基础模式

```
*.js           # 当前目录的 js 文件
**/*.js       # 所有目录的 js 文件（递归）
src/**/*.ts   # src 下所有子目录的 ts 文件
!node_modules # 排除 node_modules
```

### 实用场景

```bash
# 找所有 React 组件
**/*.{tsx,jsx}

# 找所有测试文件
**/*.test.ts
**/*.spec.ts

# 找配置文件
*.config.js
*.config.ts
```

### 排除模式

```bash
# 找源码，排除 node_modules 和 dist
src/**/*.{ts,tsx}
```

---

## Grep 技巧详解

### 1. 基础搜索

```bash
# 搜索函数名
Grep 搜索: "functionName"

# 搜索字符串
Grep 搜索: "TODO"
```

### 2. 显示上下文

```bash
# -C 显示前后 3 行
Grep 搜索: "TODO" -C: 3

# -A 显示后 5 行
Grep 搜索: "function handleClick" -A: 5

# -B 显示前 3 行
Grep 搜索: "return result" -B: 3
```

### 3. 正则搜索

```bash
# 搜索多个关键词（任一匹配）
Grep 搜索: "useState|useEffect"

# 搜索以某开头的内容
Grep 搜索: "^import"

# 搜索特定格式
Grep 搜索: "console\\.log"
```

### 4. 限制文件类型

```bash
# 只在 TypeScript 文件中搜索
Grep 搜索: "API_URL" glob: "*.ts"

# 只在组件中搜索
Grep 搜索: "useState" glob: "*.{ts,tsx}"
```

---

## 组合技（核心技能）

### 组合技 1：先找文件再搜内容

```
# 第一步：找到所有组件
Glob **/*.tsx

# 第二步：在组件中搜某个函数
Grep 搜索: "handleSubmit" glob: "*.tsx"
```

### 组合技 2：搜问题

```bash
# 找所有 any 类型
Grep 搜索: ": any" glob: "*.ts"

# 找所有 console.log
Grep 搜索: "console\\.log" glob: "src/**/*.{ts,tsx}"

# 找所有 TODO
Grep 搜索: "TODO" glob: "src/**/*.{ts,tsx}"
```

### 组合技 3：生成报告

```
搜项目里所有的 TODO，生成一个报告，包含：
- 文件位置
- TODO 内容
- 建议优先级
```

---

## 今日练习（必做！）

### 练习 1：Glob 找文件
用 Glob 找出你项目中：
- 所有组件文件
- 所有测试文件
- 所有配置文件

### 练习 2：Grep 搜内容
用 Grep 搜索：
- 某个函数的所有定义位置
- 某个变量的所有使用位置
- 所有包含 "TODO" 的位置

### 练习 3：组合技
用组合技：先 Glob 找到组件目录，再 Grep 搜索某个方法的调用。

---

## 今日思考

> Glob 告诉你"在哪"，Grep 告诉你"是什么"。两者配合，天下无难搜的代码。

**本阶段验收标准**：能够快速定位任意代码位置，理解 Glob 和 Grep 的适用场景。

---

*明日预告：Day 5 - 任务执行，用 Bash 让 CC 帮你跑命令*
