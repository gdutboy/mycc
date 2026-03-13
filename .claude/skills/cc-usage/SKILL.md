---
name: cc-usage
description: Use when 用户要查看 Claude Code 本月 token 用量、费用统计或消费趋势时触发，如看看用量、token 消耗、花了多少；不用于一般日志分析、项目成本核算或解释计费机制的场景
layer: 基础层
authorization: A区（自动执行，无需人类介入）
output_levels: L1（结论）
status: active
created: 2026-02-15
origin: 日常对话需求
---

# cc-usage — Token 用量统计

> 原子工具：扫描本地 Claude Code 日志，统计 token 消耗和费用。

## 触发词

- "/cc-usage"
- "看看用量"
- "token 消耗"
- "用量统计"

## 执行步骤

1. 根据用户需求确定参数（天数、项目、输出格式）
2. 运行分析脚本
3. 把结果整理成**易读的 Markdown 表格**返回给用户

## 脚本位置

```
.claude/skills/cc-usage/scripts/analyzer.py
```

## 用法

```bash
# 默认：全部历史，所有项目
python3 .claude/skills/cc-usage/scripts/analyzer.py

# 最近 N 天
python3 .claude/skills/cc-usage/scripts/analyzer.py --days 7

# 只看某项目（模糊匹配目录名）
python3 .claude/skills/cc-usage/scripts/analyzer.py --project mylife

# 输出 CSV（可导入 Excel）
python3 .claude/skills/cc-usage/scripts/analyzer.py --csv

# 只看模型汇总
python3 .claude/skills/cc-usage/scripts/analyzer.py --summary
```

## 默认行为

用户没指定天数时，默认跑 `--days 7`（最近 7 天）。

## 输出要求

脚本跑完后，整理成以下固定格式的 Markdown 表格：

```
| 日期 | Opus 4.6 | Sonnet 4.6 | 合计 | 合计 | 费用 |
|------|----------|------------|------|------|------|
| 03-04 | 28.7M | 56.6M | 85.3M | 0.85亿 | $65.26 |
| **总计** | **1,044M** | **218M** | **1,262M** | **12.62亿** | **$1,052** |
```

**格式规则**：
1. 模型列固定两列：Opus 4.6、Sonnet 4.6（如有新模型再加列）
2. 数值统一带单位：M（百万 token）或 亿
3. 合计列出两遍：一列 M 单位，一列 亿 单位（1亿 = 100M）
4. 无数据的模型列填 `—`
5. 如有异常（某天突然暴涨），在表格下方主动指出

## 跨平台说明

- 路径：使用 `os.path.expanduser('~')` 自动适配
- 时区：使用 `datetime.astimezone()` 自动检测系统本地时区
- 依赖：仅 Python 3 标准库，无需 pip install

## 产出格式

`[cc-usage] 最近 N 天用量统计`（后接 Markdown 表格）

## 边界

- **资源预算**：执行不超过 1 分钟
- **产出前缀**：`[cc-usage]`

## 不做的事

- 不修改日志文件（只读）
- 不对外发送用量数据
- 不在没有日志的情况下编造数据

## 维护提示

新模型上线时需更新脚本里的 `MODEL_SHORT` 和 `PRICING` 字典。
