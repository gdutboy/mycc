# evolve skill 开发

> 创建时间：2026-03-09 23:30
> 完成时间：2026-03-10
> 状态：✅ 已完成

## 功能说明

cc 自进化巡检 skill：
- 扫描来源：GitHub Trending + watchlist 固定关注列表
- 触发方式：每天凌晨 3 点定时 + 手动 `/evolve`
- 输出：值得引入 / 观望 / 已覆盖 三档分类，推送飞书卡片
- 用户回复"升级 xxx"拉起 /dev，"备用 xxx"记录观望

## 文件结构

```
.claude/skills/evolve/
├── SKILL.md              # skill 定义
└── scripts/
    ├── scan.mjs          # 核心扫描脚本
    ├── scan.test.mjs     # 测试（9/9 通过）
    └── watchlist.md      # 关注列表
```

## 验收记录

- 2026-03-10：试运行成功，飞书卡片推送正常
- 用户操作：收到通知，暂不升级，候选项标记"观望备用"存入 watchlist

## 观望备用清单（2026-03-10）

| 仓库 | 理由 |
|------|------|
| wshobson/agents | 专为 Claude Code 定制的 sub-agents 集合 |
| ruvnet/ruflo | agent-orchestration 框架 |
| microsoft/autogen | 多 Agent 框架，架构参考 |
