# 1052ADB - Android 自动化模块

> 记录时间：2026-03-09

## 项目信息

| 项目 | 信息 |
|------|------|
| 仓库 | https://github.com/1052666/1052ADB |
| 语言 | Python 100% |
| 许可证 | MIT |
| Stars | 6 |

## 功能特性

- ADB 连接管理（USB、WiFi、远程调试）
- 设备控制：点击、滑动、长按、导航键、启动应用
- 文本输入（支持中文）
- 屏幕截图获取与 Base64 转换

## 目录结构

```
1052ADB/
├── __init__.py
├── apps.py        # 应用映射
├── connection.py  # 连接管理
├── device.py      # 设备操作
├── input.py       # 文本输入
├── screenshot.py  # 截图
└── timing.py      # 延迟配置
```

## 前置要求

- 安装 ADB 工具
- 安装 Pillow 库
- 手机开启开发者选项和 USB 调试

## 与现有 skill 对比

| Skill | 目标设备 |
|-------|----------|
| desktop | Windows 电脑 |
| 1052ADB | Android 手机/模拟器 |

## 使用场景

- Android App 自动化测试
- 远程操作 Android 手机
- 手机游戏挂机脚本
- 移动端 OCR + 自动化流程

## 待探索

- [ ] 集成到 CC skill 体系
- [ ] 配合 desktop skill 实现跨设备联动
