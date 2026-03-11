# nextjs REFERENCE

> SKILL.md 的详细参考资料，包含代码示例、配置说明、排查指引。

来源: [wsimmonds/claude-nextjs-skills](https://github.com/wsimmonds/claude-nextjs-skills) — 通过了 Next.js 官方 evals 测试，将成功率从 32% 提升到 78%。

---

## 代码示例

### TypeScript 类型

```typescript
// ✅ 正确
function handleSubmit(e: React.FormEvent<HTMLFormElement>) { ... }

// ❌ 错误
function handleSubmit(e: any) { ... }
```

### useSearchParams + Suspense

```typescript
// 父组件
import { Suspense } from 'react';
import SearchComponent from './SearchComponent';

export default function Page() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <SearchComponent />
    </Suspense>
  );
}

// SearchComponent.tsx
'use client';
import { useSearchParams } from 'next/navigation';
```

### Cookies（Server Component）

```typescript
import { cookies } from 'next/headers';

export default async function Dashboard() {
  const cookieStore = await cookies();
  const token = cookieStore.get('session-token');
}
```

### searchParams（Next.js 15+）

```typescript
export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const q = (await searchParams).q || '';
}
```

### params（Next.js 15+）

```typescript
export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
}
```

### 并行数据获取

```typescript
// ❌ 串行（慢）
const user = await getUser();
const posts = await getPosts();

// ✅ 并行（快）
const [user, posts] = await Promise.all([getUser(), getPosts()]);
```

### Server Component 作为 children 传入 Client Component

```typescript
// ❌ 错误
'use client';
import ServerComponent from './ServerComponent';

// ✅ 正确
'use client';
export function ClientWrapper({ children }) {
  return <div onClick={...}>{children}</div>;
}
```

### 数据获取用 Server Component，不用 useEffect

```typescript
// ❌ 错误
'use client';
export function UserProfile() {
  const [user, setUser] = useState(null);
  useEffect(() => {
    fetch('/api/user').then(r => r.json()).then(setUser);
  }, []);
}

// ✅ 正确
export async function UserProfile() {
  const user = await getUser();
  return <div>{user.name}</div>;
}
```

---

## 路由结构

```
app/
├── page.tsx              # / 路由
├── layout.tsx            # 根布局
├── about/
│   └── page.tsx          # /about
├── blog/
│   ├── page.tsx          # /blog
│   └── [slug]/
│       └── page.tsx      # /blog/:slug
├── (auth)/               # 路由组（不影响 URL）
│   ├── login/
│   └── register/
└── api/
    └── route.ts          # API 路由
```

---

## Vercel AI SDK v5

```typescript
import { tool } from 'ai';
import { z } from 'zod';

// 必须使用 tool() helper，inputSchema 而非 parameters
const myTool = tool({
  description: '...',
  inputSchema: z.object({
    query: z.string(),
  }),
  execute: async ({ query }) => {
    // ...
  },
});

// Chat: 使用 sendMessage 而非 append
const { sendMessage } = useChat();
sendMessage({ text: 'Hello' });

// 消息内容: 使用 message.parts 而非 message.content
```

---

## Cloudflare 部署注意事项

1. 使用 `@cloudflare/next-on-pages` 或 `next-on-pages`
2. 避免使用 Node.js 特有 API，使用 Web 标准 API
3. 边缘运行时兼容：
   ```typescript
   export const runtime = 'edge';
   ```
4. 数据库使用 Cloudflare D1 或兼容边缘的数据库
