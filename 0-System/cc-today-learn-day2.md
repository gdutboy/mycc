# CC学习今日内容

> 每天深度更新 | 2026-03-12

---

# Day 2 - 文件操作：Read/Edit/Write 三大金刚

> 目标：熟练掌握文件交互的三个基础工具

---

## 三个工具的分工

| 工具 | 功能 | 何时使用 |
|------|------|---------|
| **Read** | 读取文件内容 | 看代码、看配置 |
| **Edit** | 修改文件内容 | 改 bug、调参数 |
| **Write** | 创建新文件/完全覆盖 | 新增功能、写文档 |

---

## Read 深度技巧

### 1. 大文件读取

当文件超过 2000 行时，需要指定范围：

```bash
# 只读前 100 行（适合快速了解结构）
Read file_path: src/app.ts limit: 100

# 从第 500 行开始读（跳到关键部分）
Read file_path: src/app.ts offset: 500

# 读第 500-600 行（精准定位）
Read file_path: src/app.ts limit: 100 offset: 500
```

**案例**：一个 3000 行的路由配置文件，我想看中间某个路由定义：
```
Read 这个文件 offset: 1500 limit: 50
```

### 2. 读多个文件

```bash
# 同时读配置和入口文件
Read file_path: [config.json, package.json, src/index.ts]
```

**案例**：我想同时了解项目配置和入口文件：
```
Read [package.json, src/index.ts]
```

### 3. 带指令的读

```bash
# 让 CC 读完后总结
Read 这个 React 组件，重点关注：
1. 状态管理方式
2. 副作用处理
3. 性能优化点
```

---

## Edit 深度技巧

### 1. 精确替换（核心技能）

Edit 工具的本质是**字符串替换**，所以必须找到**唯一匹配**的内容。

**❌ 错误案例**：
```bash
# 假设文件中有多个 console.log
Edit 替换 console.log 为 logger
# CC.info 会报错：匹配到多个位置，无法确定是哪一个
```

**✅ 正确案例**：
```bash
# 包含更多上下文，让匹配唯一
old_string: export function handleClick() {
  console.log('button clicked');
  setCount(count + 1);
}

new_string: export function handleClick() {
  logger.info('button clicked');
  setCount(count + 1);
}
```

### 2. replace_all 批量替换

当确定要修改**所有**匹配项时：

```bash
# 替换文件中所有 TODO 为 FIXME
Edit 替换文件中所有 TODO 为 FIXME
replace_all: true
```

**案例**：统一团队的代码规范，把所有 `var` 改成 `const`：
```
Edit 把文件中所有 var 替换为 const
replace_all: true
```

### 3. Edit 最佳实践流程

```
1. Read 先读取文件，了解结构
2. 分析 确认要改哪部分
3. Edit 进行精确替换
4. Read 验证修改结果
```

---

## Write 深度技巧

### 1. 自动创建目录

```bash
# Write 会自动创建父目录
Write file_path: src/utils/helpers/format.ts 内容是...
```

### 2. 模板生成

```bash
Write 生成一个 React 函数组件模板，包含：
- 使用 TypeScript
- 定义 Props 接口
- useState 示例
- useEffect 副作用示例
- 返回 JSX
- 导出组件
```

### 3. 覆盖 vs 追加

| 操作 | 行为 | 使用场景 |
|------|------|---------|
| Write | 完全覆盖 | 新建文件、从头重写 |
| Edit | 修改部分 | 改现有文件的一小部分 |

**⚠️ 注意**：Write 现有文件会**完全覆盖**，不是追加。

---

## 今日练习（必做！）

### 练习 1：Read 精准定位
你项目里有一个大文件（500+ 行），用 offset 和 limit 读取特定段落。

### 练习 2：Edit 精确替换
修改一个函数，给它增加更多上下文，确保 Edit 能找到唯一位置。

### 练习 3：Write 模板生成
让 CC 用 Write 生成一个完整的工具函数模板，包含完整的类型定义和导出。

---

## 今日思考

> Edit 的精髓是"精确"——给足够的上下文，让 CC 找到唯一的那段代码。上下文不够是 Edit 失败的最多原因。

**本阶段验收标准**：能够精准读取文件的任意部分，精确修改目标位置，不再需要反复试错。

---

*明日预告：Day 3 - 代码审查，把 CC 变成你的专属审查员*
