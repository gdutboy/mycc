#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Node.js 开发最佳实践查询脚本

提供 Node.js 后端开发的目录结构、API 设计、数据库操作、部署等最佳实践。

使用方法：
    python nodejs.py                           # 查看全部
    python nodejs.py --section 目录结构         # 查看指定章节
    python nodejs.py --search 路由              # 搜索关键词
"""
import os
import sys
import argparse

# 颜色
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RED = '\033[91m'
RESET = '\033[0m'


def banner():
    print(f"""
{BLUE}╔═══════════════════════════════════════════════════╗
║        🟢 Node.js 开发最佳实践                   ║
║           目录结构、API 设计、数据库、部署         ║
╚═══════════════════════════════════════════════════╝{RESET}
    """)


# Node.js 最佳实践内容
CONTENT = {
    '目录结构': """
src/
├── controllers/      # 控制器（处理请求）
├── services/        # 业务逻辑
├── models/          # 数据模型
├── routes/         # 路由定义
├── middleware/     # 中间件
├── utils/          # 工具函数
├── config/        # 配置
├── types/         # 类型定义
└── index.ts       # 入口文件

# 可选：分层结构
src/
├── modules/        # 按业务模块划分
│   ├── user/
│   │   ├── user.controller.ts
│   │   ├── user.service.ts
│   │   └── user.routes.ts
│   └── order/
└── shared/        # 共享代码
    ├── utils/
    └── constants/
""",

    '分层架构': """
## 架构分层

```
Controller → Service → Model
   ↓          ↓         ↑
   └──── Middleware ──┘
```

## 各层职责

| 层级 | 职责 |
|------|------|
| Controller | 接收请求、参数校验、返回响应 |
| Service | 业务逻辑处理 |
| Model | 数据模型定义、数据库操作 |
| Middleware | 鉴权、日志、错误处理 |
""",

    '错误处理': """
## 自定义错误类

```typescript
class AppError extends Error {{
  constructor(
    public message: string,
    public statusCode: number = 500,
    public isOperational: boolean = true
  ) {{
    super(message)
    Object.setPrototypeOf(this, AppError.prototype)
  }}
}}

class NotFoundError extends AppError {{
  constructor(message = '资源不存在') {{
    super(message, 404)
  }}
}}

class UnauthorizedError extends AppError {{
  constructor(message = '未授权') {{
    super(message, 401)
  }}
}}
```

## 统一错误处理

```typescript
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {{
  if (err instanceof AppError) {{
    return res.status(err.statusCode).json({{
      error: err.message
    }})
  }}

  // 未知错误
  console.error(err)
  res.status(500).json({{
    error: '服务器内部错误'
  }})
}})
```
""",

    'API 设计': """
## RESTful 路由规范

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /users | 获取用户列表 |
| GET | /users/:id | 获取单个用户 |
| POST | /users | 创建用户 |
| PUT | /users/:id | 更新用户 |
| DELETE | /users/:id | 删除用户 |

## 响应格式

```typescript
// 成功
res.status(200).json({{
  data: {{ users: [] }},
  message: 'success'
}})

// 201 创建
res.status(201).json({{
  data: newUser,
  message: '创建成功'
}})

// 分页
res.json({{
  data: users,
  pagination: {{
    page: 1,
    limit: 10,
    total: 100
  }}
}})
```

## 状态码

| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |
""",

    '数据库操作': """
## Prisma 使用

```typescript
// 查询用户
const user = await prisma.user.findUnique({{
  where: {{ id: userId }},
  include: {{ posts: true }}
}})

// 创建
const newUser = await prisma.user.create({{
  data: {{ name, email }}
}})

// 批量更新
await prisma.user.updateMany({{
  where: {{ role: 'guest' }},
  data: {{ role: 'user' }}
}})
```

## Drizzle ORM

```typescript
const users = await db
  .select()
  .from(usersTable)
  .where(eq(usersTable.active, true))
  .limit(10)
```

## 事务

```typescript
await prisma.$transaction(async (tx) => {{
  await tx.order.create({{...}})
  await tx.user.update({{...}})
}})
```
""",

    '环境配置': """
## .env 文件

```bash
NODE_ENV=development
PORT=3000

# 数据库
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb

# JWT
JWT_SECRET=your-secret-key
JWT_EXPIRES_IN=7d

# 第三方
SMTP_HOST=smtp.example.com
SMTP_USER=user@example.com
```

## 配置管理

```typescript
// config/index.ts
export const config = {{
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '3000', 10),

  jwt: {{
    secret: process.env.JWT_SECRET!,
    expiresIn: process.env.JWT_EXPIRES_IN || '7d'
  }},

  database: {{
    url: process.env.DATABASE_URL!
  }}
}}
```
""",

    '中间件': """
## 常用中间件

| 中间件 | 作用 |
|--------|------|
| cors | 跨域资源共享 |
| helmet | 安全头部 |
| morgan | HTTP 日志 |
| rate-limit | 请求限流 |
| express-validator | 参数校验 |
| jsonwebtoken | JWT 认证 |

## 自定义中间件

```typescript
// 鉴权中间件
export const authMiddleware = (req: Request, res: Response, next: NextFunction) => {{
  const token = req.headers.authorization?.split(' ')[1]

  if (!token) {{
    return res.status(401).json({{ error: '未提供 token' }})
  }}

  try {{
    const decoded = jwt.verify(token, config.jwt.secret)
    req.user = decoded
    next()
  }} catch {{
    res.status(401).json({{ error: '无效的 token' }})
  }}
}}
```
""",

    'PM2 部署': """
## 安装 PM2

```bash
npm install -g pm2
```

## 启动应用

```bash
# 启动
pm2 start dist/index.js --name myapp

# 查看状态
pm2 status

# 查看日志
pm2 logs myapp

# 重启
pm2 restart myapp

# 停止
pm2 stop myapp
```

## 常用命令

| 命令 | 说明 |
|------|------|
| pm2 start | 启动 |
| pm2 stop | 停止 |
| pm2 restart | 重启 |
| pm2 logs | 查看日志 |
| pm2 monit | 监控面板 |
| pm2 delete | 删除 |
""",

    'Docker 部署': """
## Dockerfile

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# 生产镜像
FROM node:20-alpine
WORKDIR /app

COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./

EXPOSE 3000
CMD ["node", "dist/index.js"]
```

## docker-compose.yml

```yaml
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://db:5432/app
    depends_on:
      - db

  db:
    image: postgres:15
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=app
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass

volumes:
  pgdata:
```
""",

    '日志与监控': """
## 日志方案

```typescript
// 使用 pino（推荐）
import pino from 'pino'

const logger = pino({{
  level: process.env.LOG_LEVEL || 'info',
  transport: process.env.NODE_ENV === 'development' {{
    target: 'pino-pretty'
  }}
}})

logger.info('服务启动')
logger.error({{ err }}, '错误')
```

## 监控

```bash
# PM2 Plus 监控
pm2 link <secret> <public>

# 使用 PM2 的监控面板
pm2 monit
```
"""
}


def show_all():
    """显示全部内容"""
    print(f"""
{GREEN}=== 全部内容 ==={RESET}

使用 --section 参数查看具体章节：
""")
    for i, key in enumerate(CONTENT.keys(), 1):
        print(f"  {i}. {key}")

    print("\n使用 --search 搜索关键词")


def show_section(section_name):
    """显示指定章节"""
    section_name = section_name.strip()

    # 模糊匹配
    matched = None
    for key in CONTENT:
        if section_name.lower() in key.lower():
            matched = key
            break

    if matched:
        print(f"\n{GREEN}=== {matched} ==={RESET}")
        print(CONTENT[matched])
    else:
        print(f"{RED}未找到章节: {section_name}{RESET}")
        print("\n可用章节：")
        for key in CONTENT:
            print(f"  - {key}")


def search(keyword):
    """搜索关键词"""
    keyword = keyword.lower()
    found = []

    for key, content in CONTENT.items():
        if keyword in key.lower() or keyword in content.lower():
            found.append((key, content))

    if found:
        print(f"\n{GREEN}=== 搜索结果: {keyword} ==={RESET}")
        for title, content in found:
            print(f"\n--- {title} ---")
            print(content[:500] + "..." if len(content) > 500 else content)
    else:
        print(f"{RED}未找到相关内容{RESET}")


def quickstart():
    """快速开始"""
    print(f"""
{GREEN}=== Node.js 快速开始 ==={RESET}

{BLUE}1. 初始化项目{RESET}
npm init -y
npm install express typescript ts-node
npm install -D @types/node @types/express typescript

{BLUE}2. 目录结构{RESET}
src/
├── index.ts       # 入口
├── controllers/  # 控制器
├── services/     # 业务逻辑
└── routes/       # 路由

{BLUE}3. 简单示例{RESET}
```typescript
import express from 'express'
const app = express()

app.get('/api/health', (req, res) => {{
  res.json({{ status: 'ok' }})
}})

app.listen(3000, () => {{
  console.log('Server running on port 3000')
}})
```

{BLUE}4. 运行{RESET}
npx ts-node src/index.ts
""")

    print(f"""
{GREEN}=== 核心原则 ==={RESET}

1. {YELLOW}分层架构{RESET}
   - Controller → Service → Model
   - 职责清晰，便于测试

2. {YELLOW}错误处理{RESET}
   - 自定义错误类
   - 统一错误中间件

3. {YELLOW}配置管理{RESET}
   - 环境变量优先
   - 不提交 .env 到 Git

4. {YELLOW}数据库{RESET}
   - 推荐 Prisma 或 Drizzle
   - 使用事务保证一致性
""")


def main():
    parser = argparse.ArgumentParser(description='Node.js 开发最佳实践')
    parser.add_argument('--section', '-s', metavar='SECTION', help='查看指定章节')
    parser.add_argument('--search', metavar='KEYWORD', help='搜索关键词')
    parser.add_argument('--all', '-a', action='store_true', help='显示全部章节')
    parser.add_argument('--quick', '-q', action='store_true', help='快速开始')

    args = parser.parse_args()

    if args.quick:
        quickstart()
    elif args.all:
        show_all()
    elif args.section:
        show_section(args.section)
    elif args.search:
        search(args.search)
    else:
        banner()
        quickstart()


if __name__ == '__main__':
    main()
