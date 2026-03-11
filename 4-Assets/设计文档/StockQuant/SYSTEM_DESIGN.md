# 🏗️ StockQuant System Design & Analysis

This document consolidates the system design, architectural analysis, strategy evaluations, and risk management frameworks for the StockQuant application.

---

## 目录 / Table of Contents

1.  [架构分析 (Architecture Analysis)](#架构分析-architecture-analysis)
    *   [顶级量化公司视角评估](#顶级量化公司视角评估)
    *   [StockQuant 架构分析报告](#stockquant-架构分析报告)
2.  [选股系统分析 (Scanner Analysis)](#选股系统分析-scanner-analysis)
    *   ["一键选股"功能深度分析](#一键选股功能深度分析)
3.  [策略系统评估 (Strategy System Evaluation)](#策略系统评估-strategy-system-evaluation)
    *   [策略系统完整性评估](#策略系统完整性评估)
    *   [HA (Heiken Ashi) 策略优化方案](#ha-heiken-ashi-策略优化方案)
    *   [策略退出机制分析](#策略退出机制分析)
    *   [策略评分体系统一方案](#策略评分体系统一方案)
4.  [回测功能分析 (Backtest Analysis)](#回测功能分析-backtest-analysis)

---

# 架构分析 (Architecture Analysis)

## 顶级量化公司视角评估
*(Original File: QUANT_FIRM_ANALYSIS.md)*

**评估方**: Two Sigma / Renaissance Technologies 风控团队视角
**系统版本**: v1.0.28

### 核心流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    模拟交易完整流程                           │
└─────────────────────────────────────────────────────────────┘

【入场阶段】Entry Phase
    ↓
1️⃣ 股票池筛选 (Scanner)
   ├─ 板块轮动 (28个申万行业)
   ├─ 混合策略 (HA+MA双重确认)
   ├─ 复合评分 (0-100分，动态权重)
   └─ 风险过滤 (ST股/黑名单/VIX控制)
    ↓
2️⃣ 信号生成 (Signal Generation)
   ├─ 突破信号 Breakout: SuperTrend翻转 或 MA金叉
   ├─ 回调信号 Pullback: 价格回踩MA20 (0-5%区间)
   └─ AI门槛 (可选): 新闻面+基本面评分
    ↓
3️⃣ 仓位管理 (Position Sizing)
   ├─ Kelly公式 (基于历史胜率+盈亏比)
   ├─ 固定金额模式 (2万/5万/10万/20万)
   ├─ 单股上限 (15% / Kelly自动调整)
   └─ 板块集中度 (≤30%)
    ↓
4️⃣ 执行买入 (Execution)
   ├─ 滑点模拟 (买入+0.2%)
   ├─ 交易成本 (0.2%)
   ├─ 成交价格 (实时行情 fetchQuotes)
   └─ 分批建仓 (可选: 观察3天后加仓)
    ↓
【持仓阶段】Holding Phase
    ↓
5️⃣ 实时监控 (Real-Time Monitoring)
   ├─ 定时扫描 (每5分钟，交易时段)
   ├─ 页面触发 (onShow自动检查)
   └─ 实时行情 (fetchQuotes强制使用)
    ↓
6️⃣ 动态止损 (Dynamic Stop Loss)
   ├─ 渐进止损 Progressive
   │  ├─ 盈利≥20% → 止损线上移至+10%
   │  ├─ 盈利≥10% → 止损线上移至+5%
   │  └─ 盈利≥5% → 止损线上移至0% (保本)
   ├─ 固定止损 Fixed: ATR-2倍
   └─ 无止损 None: 仅依赖策略信号
    ↓
7️⃣ 分批止盈 (Tiered Exit)
   ├─ 第一批 (50%): 盈利15% + 技术共振卖出信号
   ├─ 第二批 (50%): 技术信号再次确认
   └─ 移动止盈 Trailing: 盈利10%后回撤5%离场
    ↓
【离场阶段】Exit Phase
    ↓
8️⃣ 卖出执行 (Exit Execution)
   ├─ 实时价格 (fetchQuotes)
   ├─ 滑点模拟 (卖出-0.2%)
   ├─ 交易成本 (0.2%)
   └─ 原因记录 (止损/止盈/技术共振/超期清理)
```

### 机构级亮点

1.  **实时数据完整性**: 盈亏计算强制使用实时行情 `fetchQuotes`。
2.  **交易成本建模**: 滑点 (+0.2%) + 佣金 (0.2% 双边)。
3.  **Kelly公式仓位管理**: Half-Kelly 策略，仓位上限控制 (2%-15%)。
4.  **分批离场策略**: 盈利区间 + 技术强度双重确认，分批锁定利润。
5.  **动态止损系统**: 渐进式止损，随盈利上移保护利润。

### 改进建议

1.  **最大回撤止损**: 盈利后回撤超过 15% 强制离场。
2.  **ATR动态仓位调整**: 高波动股票应降低仓位。
3.  **夏普比率优化**: 引入 Sharpe Ratio 计算。
4.  **因子相关性分析**: 避免多重共线性。

---

## StockQuant 架构分析报告
*(Original File: ARCHITECTURE_ANALYSIS_TOP_QUANT.md)*

### 当前架构概览

StockQuant 采用 **三层架构设计**：

1.  **Tier 1: Stock Selection (Scanner)**
    *   10+ 技术指标: RSI, KDJ, ATR, ADX, BIAS, VolRatio, etc.
    *   多因子评分 & ML权重优化
    *   混合策略筛选

2.  **Tier 2: Signal Generation (Trend Page)**
    *   4个交易策略: MA, MACD, BOLL, HA_TREND
    *   策略对比与回测
    *   评分系统

3.  **Tier 3: Execution (Paper Trading)**
    *   策略一致性 (买卖同策略)
    *   实时行情执行
    *   风险控制

### 核心发现

*   ✅ **架构设计正确**: 三层分离符合顶级量化公司标准。
*   ⚠️ **策略数量不足**: Trend Page 仅 4 个策略，建议扩展。
*   ⚠️ **指标使用不一致**: Scanner 用 10+ 指标，Trend Page 仅用 4 个，数据未打通。

### 架构优化方案

**方案 A: 打通数据流 (推荐)**
*   Scanner 生成策略推荐标签 (如 "RSI超卖", "ATR突破")。
*   Trend Page 接收推荐并显示，打通数据孤岛。

**方案 B: 扩展策略库**
*   将 Scanner 的核心指标 (RSI, ATR, KDJ) 提升为独立交易策略。
*   新增: RSI Mean Reversion, ATR Breakout, KDJ Momentum 等。

---

# 选股系统分析 (Scanner Analysis)

## "一键选股"功能深度分析
*(Original File: SCANNER_ANALYSIS.md)*

### 核心模块划分

*   **数据层**: 多源股票池 (在线API > 热门排行 > 本地池)，实时市场状态监控。
*   **扫描层**: 批处理 (20只/批) + 并行分析 + UI节流，非阻塞扫描。
*   **策略层**:
    *   混合策略 (HA_TREND + MA): 趋势 + 时机双轨验证。
    *   经典策略: MA/MACD/BOLL + 信号新鲜度检查 (≤2天)。
    *   回调低吸: 强趋势 + 价格回踩 MA20。
*   **风控层**: 合规检查, 黑名单冷却 (7天), 市场弱势暂停, VIX高波动防护。
*   **交互层**: 批量跟踪, 自动建仓.

### 核心策略特点

1.  **混合策略 (Hybrid Strategy)**: HA趋势确定方向 (Compass)，MA均线确定时机 (Map)。避免追高 (≤12%偏离)，确认动能。
2.  **风险优先排序**: 风险等级 > 星级评分 > 综合得分。
3.  **多层风控**: 四层防护体系 (合规 -> 黑名单 -> 市场环境 -> VIX)。
4.  **多因子评分**: 动态权重，遗传算法优化。

### 改进建议

1.  **增量扫描机制**: 仅扫描 24 小时内未更新的股票，提升速度。
2.  **信号强度分级**: 细化 1-3 星标准。
3.  **流动性硬性过滤**: 强制过滤成交额 < 5000万的标的。

---

# 策略系统评估 (Strategy System Evaluation)

## 策略系统完整性评估
*(Original File: STRATEGY_SYSTEM_EVALUATION.md)*

### 现状分析

当前系统包含 4 个策略：MA, MACD, BOLL, HA_TREND。
*   **覆盖率**: 约 30% (仅覆盖趋势和均值回归)。
*   **缺失**: 波动率策略, 均值多因子, 机器学习, 市场微观结构。
*   **相关性**: 策略间相关性较高 (MA 和 HA 高度相关)。

### 缺少的策略类型 (P0)

1.  **波动率策略 (Volatility)**: ATR突破，与趋势策略负相关，适合震荡市。
2.  **RSI相对强弱 (Relative Strength)**: 识别超买超卖，适合震荡市。
3.  **市场环境识别 (Market Regime)**: ADX 判断趋势强度，自动切换趋势/震荡策略。

### 实施路线图

1.  **基础完善**: 增加 RSI, ATR 策略，实现市场环境识别。
2.  **多因子增强**: 引入价值、质量、动量因子。
3.  **高级策略**: 引入机器学习 (XGBoost/LSTM) 和另类数据。

---

## HA (Heiken Ashi) 策略优化方案
*(Original File: HA_STRATEGY_EXPLANATION.md)*

### 核心理念：分组比较 + 风险调整

不再强制统一所有策略使用普通K线，而是采用分组比较：
*   **标准策略组** (普通K线): MA, MACD, BOLL
*   **HA优化组** (HA K线): HA_TREND, HA_ROC

### 关键改进

1.  **保持HA策略使用HA K线**: 保留平滑特性，减少假信号。
2.  **分组比较**: 同组内使用相同数据源比较，最终选择整体最优 (夏普比率)。
3.  **新增 HA_ROC 策略**: 结合 ROC, VWAP, WMA, HMA，目标胜率 70%+。

---

## 策略退出机制分析
*(Original File: STRATEGY_EXIT_ANALYSIS.md)*

### 关键缺陷诊断

**问题**: 买入和卖出逻辑脱节。
*   买入: 用户选择 BOLL 策略。
*   卖出: 使用多策略共振 (MA+MACD+BOLL) 投票卖出。

**后果**: 回测无效 (回测只用BOLL)，无法归因，策略不一致。

### 解决方案：策略一致性 (Strategy Integrity)

**推荐模式**: **策略一致模式**
*   如果使用 BOLL 买入，必须严格使用 BOLL 信号卖出。
*   确保实盘逻辑与回测逻辑完全一致。
*   保留 "多策略共振" 作为可选项，但默认推荐一致性模式。

---

## 策略评分体系统一方案
*(Original File: STRATEGY_SCORING_FINAL_UNIFICATION.md & STRATEGY_SCORING_UNIFICATION.md)*

### 问题分析

趋势页 (Trend Page) 和 实验页 (Experiment Page) 推荐结果不一致。
*   趋势页: 综合评分 (收益+胜率+回撤+夏普)，使用全部数据。
*   实验页: 纯夏普比率，使用 Train-Test Split (前70%数据)。

### 统一方案 (方案A)

1.  **统一数据范围**: 两个页面均使用 **全部历史数据** (去掉 Train-Test Split)。
    *   理由: 普通用户更关注当前最优，无需机构级的样本外验证；数据量越大评估越准。
2.  **统一评分算法**: 实验页复用趋势页的综合评分函数。
3.  **支持 Alpha 加分**: 策略收益 > 买入持有收益时，额外加分 (Alpha Bonus)。
4.  **UI 统一**: 同时显示综合评分和夏普比率。

---

# 回测功能分析 (Backtest Analysis)
*(Original File: BACKTEST_ANALYSIS.md)*

### 当前问题

*   指标抽象 (新手看不懂夏普比率)。
*   缺少对比 (不知道比买入持有好多少)。
*   无可视化 (缺少收益曲线)。

### 改进方案

1.  **指标解读卡片**: 通俗解释累计收益、赚钱概率、最大回撤。
2.  **策略对比卡片**: 直观对比 "本策略" vs "买入持有"，高亮超额收益 (Alpha)。
3.  **可视化**: 添加收益曲线图。
4.  **回测说明**: 添加 Tooltip 解释回测局限性。
