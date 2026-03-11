---
name: test-review
description: 审核测试用例质量，自动或手动触发
layer: 执行层
authorization: A区（自动执行，无需人类介入）
output_levels: L1（结论）, L4（深度分析）
status: active
created: 2026-01-28
origin: P08 开发流程沉淀
---

# 测试用例审核

## 执行流程

**Step 1：覆盖度检查**
- 正常路径（Happy Path）、异常路径（Error Path）、边界值（Boundary）、并发（如适用）

**Step 2：AAA 模式合规**
- 每个 case 有清晰 Arrange/Act/Assert 三段
- Assert 断言具体（非 toBeTruthy）
- 一个 case 只测一件事

**Step 3：质量检查**
- 命名清晰、测试独立、无冗余 case、Mock 合理、断言明确

**Step 4：端到端链路检查（必查，不得跳过）**
- 涉及"写入 → 读取"的功能，测试数据必须来自真实函数输出
- 检查 `as any` 类型断言，有则核查类型定义
- 禁止手动构造假数据后自证（反模式见 REFERENCE.md）

**Step 5：遗漏检查**
- 对照需求逐项检查：空字符串、null/undefined、空数组、0、负数、特殊字符、超时、权限不足

## 输出格式

```markdown
## 测试用例审核报告

### 覆盖度
- ✅/❌/⚠️/➖ [每项状态]

### AAA 合规
- [逐项 ✅/❌]

### 端到端链路
- [逐项 ✅/❌]

### 质量
- [逐项 ✅/❌]

### 遗漏
- [逐项 ✅/❌]

### 改进建议
1. [具体建议]

### 评级
⭐⭐⭐☆☆ (x/5) - [一句话说明]
```

## 约束

- 每项必须给出 ✅/❌，不得给模糊评价
- 发现问题要具体指出哪个 case、问题是什么、怎么改
- 不修改被审核的测试代码，只出报告
- 产出前缀：`[test-review]`
- 单次审核不超过 10 分钟

## 与 /dev 集成

写测试完成后 → cc 自动执行 /test-review 自检 → 修复问题 → 输出「测试代码 + 审核报告」给人审核

详细参考：同目录下 REFERENCE.md
