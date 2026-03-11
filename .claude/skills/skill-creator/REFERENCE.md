# Skill Creator — 参考文档

## Skill 核心概念

Skill 是模块化的能力包，用于扩展 Claude 的能力：
- **专业工作流**：多步骤的领域流程
- **工具集成**：特定文件格式或 API 的使用方法
- **领域知识**：公司特定知识、schema、业务逻辑
- **打包资源**：脚本、参考文档、资产文件

Skill 遵循 Agent Skills 开放标准，同一份 SKILL.md 可跨 Claude Code、Cursor、Gemini CLI、Codex CLI 使用。

---

## SKILL.md 完整格式示例

```yaml
---
name: skill-name
description: 做什么 + 什么时候触发（这是最重要的字段，决定 AI 是否使用此 skill）
---

# Skill 标题

## 触发词
- "关键词1"
- "关键词2"

## 执行步骤
1. xxx
2. xxx

## 示例
[示例用法]
```

---

## Description 写法详解

description 是 skill 触发的唯一机制。AI 看到用户消息后，根据 description 决定是否调用 skill。

### 常见问题：under-trigger

AI 倾向于不触发 skill（觉得自己能直接处理）。对策：

1. **写明触发场景**，不只写功能描述
2. **覆盖多种说法**，包括用户不会直接提到 skill 名的情况
3. **适度"主动"**，让 AI 在模糊场景也倾向于触发

### 示例

弱 description：
> 生成公众号文章格式

强 description：
> 将 Markdown 文章渲染成微信公众号可用格式。当用户提到公众号、微信排版、文章发布、渲染文章、gzh、推文时都应触发，即使只说"帮我排一下版"也要使用此 skill。

### 触发机制原理

AI 只有在觉得任务"需要帮助"时才会查阅 skill。简单的一步操作（如"读一下这个文件"）即使 description 完美匹配也不一定触发。复杂的、多步骤的、专业的任务更容易触发。设计 eval 测试集时要注意这一点。

---

## 设计原则

### 1. 解释 why，不堆 MUST

AI 有理解力。与其写"MUST always use TypeScript"，不如写"用 TypeScript 因为项目需要类型安全，而且现有代码全是 TS"。

如果发现自己在写 ALWAYS/NEVER 大写字母，停下来想想能不能换成解释原因。

### 2. 简洁为王

上下文窗口是共享的。假设 AI 已经很聪明，只添加它不知道的信息。一个好示例胜过三段描述。

### 3. 设置合适的自由度

| 自由度 | 何时使用 | 形式 |
|--------|---------|------|
| **高** | 多种有效方法，依赖上下文判断 | 文字说明 |
| **中** | 有推荐模式，允许一些变化 | 伪代码/脚本 |
| **低** | 操作脆弱，一致性关键 | 精确脚本 |

### 4. 渐进加载

SKILL.md 控制在 500 行以内。超过时拆到 references/，在 SKILL.md 中写清"什么时候去读哪个文件"。

大型参考文件（>300 行）加目录索引。

### 5. 按领域组织

当 skill 支持多个框架/领域时：

```
cloud-deploy/
├── SKILL.md (流程 + 选择逻辑)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

AI 只读取相关的 reference。

---

## Eval 测试集格式

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "用户的任务描述",
      "expected_output": "期望结果描述",
      "assertions": [
        {
          "text": "输出文件包含标题",
          "type": "contains"
        }
      ],
      "files": []
    }
  ]
}
```

assertions 的 type 可以是：contains（包含）、format（格式）、exists（文件存在）、custom（自定义脚本验证）。

---

## 评分结果格式

```json
{
  "eval_id": 1,
  "expectations": [
    {
      "text": "输出文件包含标题",
      "passed": true,
      "evidence": "在第 3 行找到 '# 标题内容'"
    }
  ]
}
```

字段名必须是 `text`、`passed`、`evidence`（不是 name/met/details）。

---

## 触发测试集格式

```json
[
  {"query": "具体的用户 prompt", "should_trigger": true},
  {"query": "另一个 prompt", "should_trigger": false}
]
```

好的测试查询特征：
- 具体（有文件名、路径、个人背景、数据细节）
- 真实（用户真的会这么说）
- 有挑战性（负面用例是"差点该触发"的近似场景）

---

## 不要包含的文件

- README.md / INSTALLATION_GUIDE.md / CHANGELOG.md
- 其他与 skill 功能无关的文件

---

*参考：[官方 Skill 仓库](https://github.com/anthropics/skills)*
