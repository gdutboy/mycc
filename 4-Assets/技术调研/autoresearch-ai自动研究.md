# autoresearch - AI 自动研究项目

> 记录时间：2026-03-09

## 项目信息

| 项目 | 信息 |
|------|------|
| 仓库 | https://github.com/karpathy/autoresearch |
| Stars | 11.3k |
| 作者 | Andrej Karpathy |
| 许可证 | MIT |

## 核心功能

让 AI Agent 在一个小型 LLM 训练环境中**自主做实验**：

1. 修改 `train.py` 代码
2. 训练 5 分钟
3. 检查 val_bpb 指标是否改进
4. 保留或丢弃，然后重复

## 设计亮点

- **固定时间**：每次实验 5 分钟，公平比较
- **单一文件**：只改 `train.py`，可控
- **单 GPU**：不需要分布式

## 本地硬件

| 设备 | 规格 |
|------|------|
| 本机 | RX Vega M GH (4GB) - 不够 |
| 7900XTX 主机 | 24GB 显存 - 够用 |

## Windows 可用方案

| 方案 | 说明 |
|------|------|
| Ollama | 本地跑 LLM |
| LM Studio | 图形界面，更易用 |
| llama.cpp | 跑量化模型 |

## 未来可能方向

- [ ] 在 7900XTX 上跑 autoresearch（需 WSL2）
- [ ] 微调小模型
- [ ] 跑 13B 本地模型

## 相关资料

- 原始项目：https://github.com/karpathy/autoresearch
- fork 版本：https://github.com/gdutboy/autoresearch
