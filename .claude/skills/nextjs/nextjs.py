#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Next.js 开发最佳实践查询脚本

提供 Next.js 开发的目录结构、路由、数据获取、状态管理等最佳实践。

使用方法：
    python nextjs.py                           # 查看全部
    python nextjs.py --section 目录结构         # 查看指定章节
    python nextjs.py --search 路由              # 搜索关键词
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
║        ⚛️ Next.js 开发最佳实践                   ║
║           目录结构、路由、数据获取、状态管理        ║
╚═══════════════════════════════════════════════════╝{RESET}
    """)


# Next.js 最佳实践内容
CONTENT = {
    '目录结构': """
src/
├── app/                    # App Router
│   ├── page.tsx           # 页面
│   ├── layout.tsx         # 布局
│   ├── loading.tsx        # 加载态
│   ├── error.tsx         # 错误处理
│   └── [id]/             # 动态路由
│       └── page.tsx
├── components/            # 组件
│   ├── ui/               # 基础 UI
│   └── features/         # 业务组件
├── lib/                   # 工具函数
│   ├── api.ts            # API 调用
│   ├── utils.ts          # 通用工具
│   └── constants.ts      # 常量
├── hooks/                 # 自定义 Hooks
├── stores/               # 状态管理
├── types/                # 类型定义
└── styles/               # 样式
""",

    '路由规范': """
## 路由规则

| 路径 | 说明 |
|------|------|
| `/` | 首页 |
| `/about` | 静态页面 |
| `/posts/[id]` | 动态路由 |
| `/posts/[id]/edit` | 嵌套路由 |
| `/posts/[id]/[comment]` | 多级动态 |

## 文件约定

- `page.tsx` - 页面组件（必需）
- `layout.tsx` - 布局组件
- `loading.tsx` - 加载态
- `error.tsx` - 错误处理
- `not-found.tsx` - 404 页面
- `route.ts` - API 路由
""",

    'Server Components': """
## Server Components 默认

- 优先使用 Server Components
- 只在需要交互时用 Client Components

```tsx
// Server Component（默认）
export default async function Page() {{
  const data = await fetchData()
  return <div>{{data.title}}</div>
}}

// 需要交互时加 'use client'
'use client'
export function Counter() {{
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(c => c + 1)}>{{count}}</button>
}}
```

## 使用场景

| Server Components | Client Components |
|-------------------|-------------------|
| 数据获取 | 交互（onClick, onChange）|
| 访问后端资源 | useState, useEffect |
| 敏感信息 | 浏览器 API |
| 大组件（减少 JS）| 自定义 Hooks |
""",

    '数据获取': """
## Server Components 数据获取

```tsx
// 直接 await
const data = await fetch('https://api.com/data', {
  next: { revalidate: 3600 } // ISR，1小时重新验证
})

// 缓存策略
fetch(url, { cache: 'no-store' })     // 每次请求
fetch(url, { cache: 'force-cache' })  // 强缓存
fetch(url, { next: { revalidate: 60 }}) // 60秒后失效
```

## 客户端数据获取

推荐使用 React Query / SWR：

```tsx
'use client'
const { data } = useQuery({
  queryKey: ['key'],
  queryFn: fetchFn
})
```
""",

    'API 路由': """
## 创建 API

```tsx
// app/api/posts/route.ts

// GET
export async function GET() {
  const posts = await db.post.findMany()
  return NextResponse.json(posts)
}

// POST
export async function POST(request: Request) {
  const body = await request.json()
  const post = await db.post.create({ data: body })
  return NextResponse.json(post)
}

// 动态路由：app/api/posts/[id]/route.ts
export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  const post = await db.post.findUnique({
    where: { id: params.id }
  })
  return NextResponse.json(post)
}
```
""",

    '样式方案': """
## 推荐：Tailwind CSS

```tsx
// 安装
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

// 配置 tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: { extend: {} },
  plugins: [],
}

// 使用
<div className="p-4 bg-white rounded-lg shadow">
  Hello Next.js
</div>
```

## CSS Modules（备选）

```tsx
// Button.module.css
.button { background: blue; }

// Button.tsx
import styles from './Button.module.css'
<button className={styles.button}>Click</button>
```
""",

    '表单提交': """
## Server Actions（推荐）

```tsx
// app/actions.ts
'use server'

export async function submitForm(formData: FormData) {
  const name = formData.get('name')
  await db.user.create({ data: { name: name as string } })
  revalidatePath('/')
}

// 客户端调用
<form action={submitForm}>
  <input name="name" />
  <button type="submit">提交</button>
</form>
```

## 传统方式

```tsx
'use client'
export function Form() {
  const router = useRouter()

  async function onSubmit(formData: FormData) {
    await fetch('/api/submit', {
      method: 'POST',
      body: formData
    })
    router.refresh()
  }

  return <form action={{onSubmit}}>...</form>
}}
```
""",

    '错误处理': """
## error.tsx

```tsx
// app/error.tsx
'use client'
export default function Error({ error, reset }) {
  return (
    <div>
      <p>发生错误: {error.message}</p>
      <button onClick={() => reset()}>重试</button>
    </div>
  )
}
```

## not-found.tsx

```tsx
// app/not-found.tsx
import Link from 'next/link'

export default function NotFound() {
  return (
    <div>
      <h2>Not Found</h2>
      <p>无法找到该页面</p>
      <Link href="/">返回首页</Link>
    </div>
  )
}
```

## 全局错误处理

```tsx
// app/global-error.tsx
'use client'
export default function GlobalError({ error, reset }) {
  return (
    <html>
      <body>
        <h2>出现问题了!</h2>
        <button onClick={() => reset()}>重试</button>
      </body>
    </html>
  )
}
```
""",

    '部署': """
## Vercel（推荐）

```bash
# 推送代码到 GitHub
# 访问 vercel.com 导入项目
# 自动部署，无需配置
```

## Docker 部署

```dockerfile
# Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
```

## PM2 部署

```bash
npm run build
pm2 start npm --name "nextjs" -- start
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
{GREEN}=== Next.js 快速开始 ==={RESET}

{BLUE}1. 创建项目{RESET}
npx create-next-app@latest my-app --typescript --tailwind --eslint

{BLUE}2. 目录结构{RESET}
src/app/page.tsx      # 首页
src/app/layout.tsx    # 根布局
src/app/globals.css   # 全局样式

{BLUE}3. 创建页面{RESET}
# src/app/about/page.tsx
export default function About() {{
  return <h1>About</h1>
}}

{BLUE}4. 创建 API{RESET}
# src/app/api/hello/route.ts
export function GET() {{
  return Response.json({{{{ message: 'Hello' }}}})
}}

{BLUE}5. 运行{RESET}
npm run dev
""")

    print(f"""
{GREEN}=== 核心原则 ==={RESET}

1. {YELLOW}Server Components 优先{RESET}
   - 默认使用服务端组件
   - 需要交互才用 'use client'

2. {YELLOW}数据获取{RESET}
   - 服务端直接 await
   - 客户端用 React Query

3. {YELLOW}路由{RESET}
   - 文件系统即路由
   - page.tsx = 页面

4. {YELLOW}样式{RESET}
   - 推荐 Tailwind CSS
""")


def main():
    parser = argparse.ArgumentParser(description='Next.js 开发最佳实践')
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
