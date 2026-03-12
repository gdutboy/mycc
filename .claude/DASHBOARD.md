# cc 能力看板

> 共 **39** 个技能，按功能分 8 类。

---

## 平台基础（5）

| 技能 | 功能 | 状态 |
|------|------|------|
| `/setup` | 首次使用引导，交互式完成配置 | 稳定 |
| `/dashboard` | 可视化查看能力看板 | 稳定 |
| `/mycc` | 启动移动端后端，手机/网页远程访问 CC | 稳定 |
| `/scheduler` | 定时任务系统（cron），内置在 mycc 后端 | 稳定 |
| `/tell-me` | 飞书通知，发送消息/结果到飞书群 | 稳定 |

## 开发工程（6）

| 技能 | 功能 | 状态 |
|------|------|------|
| `/dev` | TDD 开发流程：测试先行，人工卡点审核 | 稳定 |
| `/dev-team` | 多 Agent 团队协作开发（30min+ 大任务） | 稳定 |
| `/test-review` | 审核测试用例覆盖率和质量 | 稳定 |
| `/nextjs` | Next.js App Router 开发最佳实践 | 稳定 |
| `/nodejs` | Node.js 开发最佳实践 | 稳定 |
| `/skill-creator` | 创建、测试和优化 Claude Code Skill | 稳定 |

## PACE 工作流（6）

| 技能 | 功能 | 状态 |
|------|------|------|
| `/pace-workflow` | PACE 协议核心工作流（Plan-Artifact-Check-Execute） | 稳定 |
| `/artifact-management` | Artifact 文件管理规则（spec/task/impl/walk/findings） | 稳定 |
| `/change-management` | 变更 ID 管理模块，跨 Artifact 联动 | 稳定 |
| `/pace-bridge` | Superpowers 计划文件桥接到 PACEflow artifacts | 稳定 |
| `/pace-knowledge` | PACEflow 知识库笔记管理（thoughts/knowledge） | 稳定 |
| `/paceflow-audit` | 5-agent 并行团队全面审查 | 稳定 |

## 信息采集（4）

| 技能 | 功能 | 状态 |
|------|------|------|
| `/collect` | 多源并行采集（时政/AI/GitHub/股票），推送飞书简报 | 稳定 |
| `/read-gzh` | 读取微信公众号文章，生成结构化总结 | 稳定 |
| `/gh-trending` | 采集 GitHub Trending AI 项目并推飞书 | 稳定 |
| `/evolve` | 对比 Trending 与 mycc skill 体系，生成升级建议 | 稳定 |

## 内容创作（6）

| 技能 | 功能 | 状态 |
|------|------|------|
| `/create-system` | 创作任务路由（自动分发到子技能） | 稳定 |
| `/outline` | 根据主题生成文章大纲 | 稳定 |
| `/draft` | 根据大纲生成文章初稿 | 稳定 |
| `/polish` | 打磨文章语言质量 | 稳定 |
| `/title` | 生成公众号标题 | 稳定 |
| `/gzh` | Markdown 转微信公众号可发布格式 | 稳定 |

## 自动化 & Agent（4）

| 技能 | 功能 | 状态 |
|------|------|------|
| `/1052agent` | 动态双主多智能体协同架构 | 稳定 |
| `/heartbeat` | 定时唤醒，从焦点池挑任务后台思考 | 稳定 |
| `/reflect` | 记录故障异常，定期反思提炼经验 | 稳定 |
| `/decision` | 从对话上下文自动提取决策记录 | 稳定 |

## 桌面 & 通讯（3）

| 技能 | 功能 | 状态 |
|------|------|------|
| `/desktop` | Windows 桌面操控（截图/点击/键盘） | 稳定 |
| `/wechatbot` | 微信机器人桌面控制 | 稳定 |
| `/brush` | AI 图片生成（文字描述生成配图） | 稳定 |

## 方法论 & 框架（5）

| 技能 | 功能 | 状态 |
|------|------|------|
| `/cc-usage` | 查看本月 Claude Code token 用量统计 | 稳定 |
| `/sop4ai` | 编写 AI 可执行的标准化 SOP | 稳定 |
| `/sales` | DCFCS 销售框架 | 稳定 |
| `/startup-259` | 2-5-9 创业假设验证 | 稳定 |
| `/fun-design` | 极简设计法审视产品需求 | 稳定 |

---

## 规划中

| 想法 | 描述 | 优先级 |
|------|------|--------|
| Seed 2.0 引擎 | team-mode 接入火山引擎 Seed 2.0 低成本选项 | 中 |
| check-deps | mycc 依赖检查脚本 | 低 |
| `.claude-plugin/` 打包 | 插件化分发方案 | 低 |

---

*最后更新：2026-03-12*
