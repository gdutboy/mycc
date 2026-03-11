# Node.js 开发参考手册

## 目录结构

```
src/
├── controllers/      # 控制器
├── services/        # 业务逻辑
├── models/          # 数据模型
├── routes/         # 路由
├── middleware/     # 中间件
├── utils/          # 工具函数
├── config/        # 配置
└── index.ts       # 入口
```

## 分层架构

```
Controller → Service → Model
   ↓          ↓         ↑
   └──── Middleware ──┘
```

## 错误处理

```typescript
// 自定义错误类
class AppError extends Error {
  constructor(message: string, statusCode: number) {
    super(message)
    this.statusCode = statusCode
  }
}

// 统一错误处理中间件
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500
  res.status(statusCode).json({
    error: err.message
  })
})
```

## API 设计（RESTful）

```
GET    /users          # 获取列表
GET    /users/:id      # 获取单个
POST   /users          # 创建
PUT    /users/:id      # 更新
DELETE /users/:id      # 删除
```

## 数据库操作

```typescript
// 推荐使用 Prisma 或 Drizzle
const user = await prisma.user.findUnique({
  where: { id },
  include: { posts: true }
})
```

## 环境配置

```
# .env
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://...
```

```typescript
// config/index.ts
export const config = {
  env: process.env.NODE_ENV,
  port: parseInt(process.env.PORT || '3000'),
}
```

## 常用中间件

| 中间件 | 作用 |
|--------|------|
| cors | 跨域 |
| helmet | 安全头 |
| morgan | 日志 |
| rate-limit | 限流 |
| validate | 参数校验 |

## 部署

### PM2 进程管理

```bash
pm2 start dist/index.js -n myapp
pm2 logs
pm2 restart
```

### Docker

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["node", "dist/index.js"]
```
