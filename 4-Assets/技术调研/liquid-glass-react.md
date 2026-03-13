# liquid-glass-react

> 记录时间：2026-03-09

## 项目信息

| 项目 | 信息 |
|------|------|
| 仓库 | https://github.com/rdev/liquid-glass-react |
| Stars | 4.6k |
| 技术栈 | TypeScript + React |
| 许可证 | MIT |

## 功能特性

- 边缘弯曲与折射效果
- 多种折射模式：standard、polar、prominent、shader
- 可配置模糊/霜冻程度
- 色差效果（chromatic aberration）
- 弹性液态触感（鼠标移动时）
- 正确的悬停和点击效果
- 光影高光效果

## 安装

```bash
npm install liquid-glass-react
```

## 基础用法

```tsx
import LiquidGlass from 'liquid-glass-react'

<LiquidGlass>
  <div>你的内容</div>
</LiquidGlass>
```

## 常用 Props

| Prop | 默认值 | 描述 |
|------|--------|------|
| `displacementScale` | 70 | 位移效果强度 |
| `blurAmount` | 0.0625 | 模糊/霜冻程度 |
| `saturation` | 140 | 颜色饱和度 |
| `aberrationIntensity` | 2 | 色差强度 |
| `elasticity` | 0.15 | 液态弹性 |
| `cornerRadius` | 999 | 边框圆角 |
| `mode` | "standard" | 折射模式 |

## 使用场景

- 玻璃卡片组件
- 玻璃按钮
- 背景装饰层
- 现代 UI 美化
- Apple 风格界面

## 在线演示

https://liquid-glass.maxrovensky.com

## 浏览器支持

- Chrome/Edge：完整支持
- Safari/Firefox：部分支持（位移效果不可见）

## 与现有项目关联

- 可用于 Next.js 项目装饰
- 公众号配图/演示页面美化
