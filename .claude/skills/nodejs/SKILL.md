---
name: nodejs
description: Node.js 开发最佳实践指南
layer: 领域层
authorization: A区（自动执行）
output_levels: L1（指引）
---

# Node.js 开发最佳实践

## 执行流程

收到 Node.js 开发任务时，按以下步骤处理：

1. **确认项目结构**：按分层架构组织代码 `Controller → Service → Model`
   - `src/controllers/` 处理请求，`src/services/` 放业务逻辑，`src/models/` 定义数据模型
   - `src/routes/`、`src/middleware/`、`src/utils/`、`src/config/`、`src/index.ts`

2. **错误处理**：统一使用自定义 `AppError` 类 + 全局错误中间件兜底

3. **API 设计**：遵循 RESTful 规范，路由命名清晰

4. **数据库**：优先使用 Prisma 或 Drizzle ORM

5. **环境配置**：`.env` 管理敏感配置，`config/index.ts` 统一导出

6. **中间件**：按需引入 cors / helmet / morgan / rate-limit / validate

7. **部署**：
   - 开发/生产：PM2 进程管理
   - 容器化：Docker，基础镜像 `node:20-alpine`

详细参考：同目录下 REFERENCE.md
