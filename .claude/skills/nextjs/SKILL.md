---
name: nextjs
description: Next.js App Router 开发最佳实践指南
layer: 执行层
authorization: A区（自动执行，无需人类介入）
output_levels: L1（结论）
status: active
created: 2026-02-01
origin: wsimmonds/claude-nextjs-skills 社区 skill 引入
---

# nextjs（参考规范）

> Next.js App Router 开发指南。cc 开发 Next.js 项目时自动遵循，不是独立触发的 skill。

## 触发词

- "/nextjs"
- 开发 Next.js 项目时自动加载

---

## 核心决策

**Server Component（默认）**：数据获取、环境变量、敏感信息
**Client Component（加 `'use client'`）**：交互事件、React hooks、浏览器 API

---

## 关键规则（必须遵守）

1. **TypeScript**：永远不用 `any`，明确标注类型
2. **useSearchParams**：必须同时加 `'use client'` + Suspense 包裹
3. **Cookies**：Server Component 中用 `await cookies()` 获取
4. **searchParams / params（Next.js 15+）**：都是 Promise，必须 `await`
5. **数据获取**：多个并行请求用 `Promise.all`，不串行

## 必须避免

- 过度使用 `'use client'`（只在需要交互时加）
- Client Component 内直接 fetch 数据（应在 Server Component 获取后传 props）
- 将 Server Component 直接 import 进 Client Component（用 children 传递）
- `useEffect + useState` 获取数据（改用 Server Component async/await）

---

## 边界

- 定位：参考规范，不独立产出文档或报告
- 不覆盖项目已有的自定义约定
- 不在非 Next.js 项目中强行套用

---

详细参考：同目录下 REFERENCE.md
