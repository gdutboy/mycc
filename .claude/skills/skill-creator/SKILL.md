---
name: skill-creator
description: 创建新的 Claude Code Skill
---

# Skill Creator

## 触发词

- "帮我创建一个 skill"
- "把这个变成 skill"
- "新建技能"
- "/create-skill"

---

## 执行流程

### Step 1: 理解需求
- 这个 skill 要做什么？
- 用户会怎么触发它？
- 需要什么输入/输出？

### Step 2: 规划资源
- 需要脚本 → 放 `scripts/`
- 需要参考文档 → 放 `references/`
- 需要模板/资产 → 放 `assets/`

### Step 3: 创建目录
```bash
mkdir -p .claude/skills/你的skill名
```

### Step 4: 编写 SKILL.md

frontmatter 格式：
```yaml
---
name: skill-name
description: 做什么 + 什么时候触发
---
```

body 内容：触发词、执行步骤、必要示例。

### Step 5: 测试迭代
在真实任务中使用 → 发现问题 → 更新 SKILL.md → 重复。

---

## 存放位置

| 位置 | 作用域 |
|------|--------|
| `~/.claude/skills/` | 个人全局 |
| `项目/.claude/skills/` | 项目级，可 git 共享 |

---

详细参考：同目录下 REFERENCE.md
