# 机构级量化监控系统设计方案

**版本**: v1.0
**日期**: 2026-01-30
**设计理念**: 不盯盘，只监控异常

---

## 📋 目录

- [核心理念](#核心理念-散户式盯盘-vs-机构式监控)
- [四大监控维度](#四大监控维度)
- [系统架构](#系统架构)
- [核心代码实现](#核心代码实现)
- [实现路线图](#实现路线图)
- [与现有系统集成](#与现有系统集成)

---

## 🎯 核心理念：散户式盯盘 vs 机构式监控

| 维度 | 散户式盯盘 | 量化机构监控 |
|------|-----------|-------------|
| **目标** | 看价格涨跌，找买卖点 | 监控风险暴露，自动触发 |
| **频率** | 高频（秒级刷新） | 事件驱动（有变化才触发） |
| **内容** | 价格、成交量 | 仓位、止损、波动率、流动性 |
| **方式** | 人工盯着 | 系统自动巡检 |
| **决策** | 情绪化 | 规则化、算法化 |

### 设计原则

> **"好的量化系统应该像自动雷达，不需要人盯着屏幕。只有异常事件发生时才需要人工介入。"**

1. **事件驱动，非定时轮询**
   - 不是每3秒刷新，而是"有变化才触发"
   - 节省电量、API请求

2. **分层监控**
   - L1: 每分钟巡检（止损、流动性）
   - L2: 每5分钟巡检（偏离度、市场状态）
   - L3: 每小时巡检（全局风控、大级别分析）

3. **智能抑制噪音**
   - 同类警告10分钟内只发一次
   - 低优先级警告只在"汇总报告"中显示

---

## 📊 四大监控维度

### 1️⃣ 风险暴露监控（最重要）

**目标**: 防止单只股票亏损失控和账户回撤超限

**监控指标**:
```javascript
const RISK_THRESHOLDS = {
    // 单只股票亏损阈值
    MAX_SINGLE_LOSS_PCT: -8,

    // 总账户回撤阈值
    MAX_MAX_DRAWDOWN_PCT: -15,

    // 单只股票仓位上限
    MAX_SINGLE_POSITION_PCT: 12,

    // 行业集中度上限
    MAX_INDUSTRY_CONCENTRATION: 40
};
```

**触发条件**:
- 🚨 单只股票亏损超过 -8% → 自动止损卖出
- 🚨 总账户回撤超过 -15% → 触发全局风控，停止所有开仓
- ⚠️ 单只股票仓位超过 12% → 提醒分散风险
- ⚠️ 单一行业集中度超过 40% → 提醒行业风险

---

### 2️⃣ 市场状态监控

**目标**: 及时发现市场状态切换，动态调整仓位策略

**监控内容**:
- 牛市 → 震荡市 → 熊市的状态切换
- VIX指数（波动率）异常
- 市场成交量变化

**触发条件**:
```javascript
const MARKET_TRANSITION_STRATEGIES = {
    'BULL->RANGING': {
        action: 'REDUCE_POSITION',
        targetPosition: 50,
        reason: '牛市转震荡，降低风险暴露'
    },
    'RANGING->BEAR': {
        action: 'STOP_NEW_BUYS',
        targetPosition: 30,
        reason: '震荡转熊市，暂停开仓'
    },
    'BEAR->BULL': {
        action: 'AGGRESSIVE_BUILD',
        targetPosition: 60,
        reason: '熊市转牛市，积极建仓'
    }
};
```

**输出**:
- 📊 市场状态切换通知
- 🎯 仓位调整建议
- 📈 策略切换提示（如：从激进策略转为防御策略）

---

### 3️⃣ 流动性监控

**目标**: 防止买入流动性枯竭的股票，导致无法及时卖出

**监控指标**:
- 换手率（Turnover Rate）
- 成交量（Volume）
- 买卖价差（Bid-Ask Spread）

**触发条件**:
- 🔴 **流动性枯竭**: 换手率 < 0.5%
  - 风险：可能无法及时卖出
  - 行动：考虑提前卖出或避免加仓

- 🟡 **异常放量**: 换手率 > 15%
  - 风险：可能是主力出货信号
  - 行动：关注价格走势，准备止损

**机构经验**:
> "流动性风险是量化基金的最大杀手之一。
> 2008年金融危机中，许多策略失败不是因为方向错了，而是因为流动性枯竭无法平仓。"

---

### 4️⃣ 组合偏离度监控

**目标**: 确保ETF配置符合目标配置，自动触发再平衡

**监控内容**:
- 当前ETF配置 vs 目标配置
- 各类ETF的偏离度百分比
- 最大偏离度

**计算示例**:
```javascript
// 市场状态：牛市
// 目标配置：宽基18% + 行业10% + 策略3% = 31%

const currentAllocation = {
    broad: 15,      // 当前：15%
    industry: 12,   // 当前：12%
    strategy: 4     // 当前：4%
};

const targetAllocation = {
    broad: 18,
    industry: 10,
    strategy: 3
};

// 偏离度计算
const drift = {
    broad: (15 - 18) / 18 * 100 = -16.7%,    // ✅ 可接受
    industry: (12 - 10) / 10 * 100 = +20%,   // ⚠️ 接近阈值
    strategy: (4 - 3) / 3 * 100 = +33.3%     // 🚨 超过阈值，触发再平衡
};

// 最大偏离度：33.3% > 25% → 触发再平衡提醒
```

**触发条件**:
- 最大偏离度 > 25% → 触发再平衡提醒
- 提供一键再平衡功能
- 显示调仓建议（卖出哪些、买入哪些）

---

## 🏗️ 系统架构

### 监控中心页面设计

```
┌─────────────────────────────────────────┐
│          量化机构监控中心                │
│  (Quantitative Monitoring Dashboard)    │
├─────────────────────────────────────────┤
│                                         │
│  🔴 实时风险面板                        │
│  ┌─────────────────────────────┐       │
│  │ 总资产: 105,200  总盈亏: +5.2%│       │
│  │ 仓位: 52/100  风控状态: 🟢正常 │       │
│  │ 回撤: -2.3%  最大回撤: -8.5% │       │
│  └─────────────────────────────┘       │
│                                         │
│  🚨 异常事件列表                        │
│  ┌─────────────────────────────┐       │
│  │ [15:32] 🚨 止损触发          │       │
│  │  平安银行 亏损超-8%，已卖出  │       │
│  ├─────────────────────────────┤       │
│  │ [15:30] ⚠️ 流动性警告        │       │
│  │  科创50ETF 换手率0.3%       │       │
│  ├─────────────────────────────┤       │
│  │ [15:25] 📊 市场切换          │       │
│  │  震荡市→熊市，建议降仓      │       │
│  ├─────────────────────────────┤       │
│  │ [15:15] 🔄 再平衡提醒        │       │
│  │  ETF偏离度28%，建议调仓     │       │
│  └─────────────────────────────┘       │
│                                         │
│  📈 组合分析                            │
│  ┌─────────────────────────────┐       │
│  │ ETF偏离度: 18% ✅           │       │
│  │ 行业分布: 科技40% 金融30%   │       │
│  │ 风险暴露: VaR -1,234        │       │
│  │ 流动性评分: 85/100          │       │
│  └─────────────────────────────┘       │
│                                         │
│  📊 监控状态                            │
│  ┌─────────────────────────────┐       │
│  │ ✅ 止损监控 (1分钟)          │       │
│  │ ✅ 流动性监控 (2分钟)        │       │
│  │ ✅ 市场状态 (5分钟)          │       │
│  │ ✅ ETF偏离度 (10分钟)        │       │
│  └─────────────────────────────┘       │
│                                         │
│  [🔄 开始监控]  [⏸ 暂停]  [📋 查看日志]│
└─────────────────────────────────────────┘
```

### 技术架构图

```
┌─────────────────────────────────────────────┐
│           监控引擎 (Monitoring Engine)        │
│   - 任务调度器                               │
│   - 优先级队列                               │
│   - 噪音抑制器                               │
└────────────┬────────────────────────────────┘
             │
    ┌────────┼────────┬────────┬────────┐
    │        │         │        │        │
┌───▼──┐ ┌──▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼────┐
│止损监│ │流动 │ │市场  │ │ETF偏 │ │全局  │
│控任务│ │性监控│ │状态  │ │离度  │ │风控  │
│(1min)│ │(2min)│ │(5min)│ │(10min)│ │(1hour)│
└───┬──┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬────┘
    │       │       │       │       │
    └───────┴───────┴───────┴───────┘
            │
    ┌───────▼────────┐
    │  警告路由器    │
    │  - 去重        │
    │  - 分级        │
    │  - 推送        │
    └───────┬────────┘
            │
      ┌─────┴────────┐
      │              │
  ┌───▼───┐      ┌──▼────┐
  │小程序内│      │订阅消息│
  │通知栏  │      │推送    │
  └───────┘      └───────┘
```

---

## 💻 核心代码实现

### 监控引擎（utils/monitoring_engine.js）

```javascript
/**
 * 量化监控系统引擎
 * 设计原则：
 * 1. 事件驱动，非定时轮询
 * 2. 分层监控（不同任务不同频率）
 * 3. 智能抑制噪音
 */

class QuantMonitoringEngine {
    constructor() {
        this.monitors = [];
        this.isRunning = false;
        this.timers = {};
        this.alertHistory = [];  // 警告历史
        this.alertSuppress = {}; // 噪音抑制
    }

    /**
     * 注册监控任务
     * @param {Object} config - 监控配置
     * @param {String} config.name - 监控名称
     * @param {Number} config.interval - 执行间隔（毫秒）
     * @param {Number} config.priority - 优先级（1=高, 2=中, 3=低）
     * @param {Function} config.checkFn - 检查函数，返回 { shouldAlert: boolean, data: any }
     * @param {Function} config.alertFn - 告警函数
     */
    registerMonitor(config) {
        const { name, interval, priority, checkFn, alertFn } = config;

        this.monitors.push({
            name,
            interval,
            priority,
            checkFn,
            alertFn,
            lastRun: 0,
            runCount: 0
        });

        // 按优先级排序
        this.monitors.sort((a, b) => a.priority - b.priority);

        console.log(`[监控引擎] ✅ 注册监控任务: ${name} (${interval/1000}秒, 优先级${priority})`);
    }

    /**
     * 启动监控
     */
    start() {
        if (this.isRunning) {
            console.warn('[监控引擎] ⚠️ 监控已在运行中');
            return;
        }

        console.log('[监控引擎] 🚀 启动量化监控系统');
        this.isRunning = true;

        this.monitors.forEach(monitor => {
            this.timers[monitor.name] = setInterval(() => {
                if (!this.isRunning) return;

                this.runMonitor(monitor);
            }, monitor.interval);

            console.log(`[监控引擎] ✅ ${monitor.name} - ${monitor.interval/1000}秒/次`);
        });

        // 立即执行一次所有任务
        this.monitors.forEach(monitor => this.runMonitor(monitor));
    }

    /**
     * 执行单个监控任务
     */
    async runMonitor(monitor) {
        const startTime = Date.now();

        try {
            monitor.lastRun = startTime;
            monitor.runCount++;

            const result = await monitor.checkFn();

            if (result && result.shouldAlert) {
                // 检查是否需要抑制（避免重复报警）
                if (this.shouldSuppressAlert(monitor.name, result)) {
                    console.log(`[监控引擎] 🤫 警告已抑制: ${monitor.name}`);
                    return;
                }

                // 记录并触发告警
                this.recordAlert(monitor.name, result);
                monitor.alertFn(result);
            }

            const elapsed = Date.now() - startTime;
            if (elapsed > 1000) {
                console.warn(`[监控引擎] ⚠️ ${monitor.name} 执行耗时: ${elapsed}ms`);
            }
        } catch (e) {
            console.error(`[监控引擎] ❌ ${monitor.name} 执行失败:`, e);
            monitor.errorCount = (monitor.errorCount || 0) + 1;

            // 连续失败3次，停止该任务
            if (monitor.errorCount >= 3) {
                console.error(`[监控引擎] 🚨 ${monitor.name} 连续失败3次，停止运行`);
                clearInterval(this.timers[monitor.name]);
            }
        }
    }

    /**
     * 噪音抑制：同类警告10分钟内只发一次
     */
    shouldSuppressAlert(monitorName, alertData) {
        const key = `${monitorName}_${JSON.stringify(alertData)}`;
        const lastTime = this.alertSuppress[key];

        if (lastTime && Date.now() - lastTime < 10 * 60 * 1000) {
            return true;  // 抑制
        }

        this.alertSuppress[key] = Date.now();
        return false;
    }

    /**
     * 记录警告历史
     */
    recordAlert(monitorName, alertData) {
        const alert = {
            id: Date.now(),
            monitor: monitorName,
            data: alertData,
            timestamp: new Date().toLocaleString()
        };

        this.alertHistory.unshift(alert);

        // 只保留最近100条
        if (this.alertHistory.length > 100) {
            this.alertHistory = this.alertHistory.slice(0, 100);
        }

        // 持久化
        wx.setStorageSync('MONITOR_ALERT_HISTORY', this.alertHistory);
    }

    /**
     * 暂停监控
     */
    stop() {
        console.log('[监控引擎] ⏸ 暂停监控');
        this.isRunning = false;

        Object.values(this.timers).forEach(timer => clearInterval(timer));
        this.timers = {};
    }

    /**
     * 紧急停止（触发全局风控）
     */
    emergencyStop(reason) {
        console.error(`[监控引擎] 🚨 紧急停止: ${reason}`);
        this.stop();

        // 触发全局风控
        wx.setStorageSync('GLOBAL_RISK_CONTROL', {
            status: 'EMERGENCY_STOP',
            reason,
            timestamp: Date.now()
        });

        // 发送紧急通知
        sendUrgentAlert({
            type: 'EMERGENCY_STOP',
            reason,
            message: '系统已触发紧急风控，所有开仓操作已暂停'
        });
    }

    /**
     * 获取监控状态
     */
    getStatus() {
        return {
            isRunning: this.isRunning,
            monitors: this.monitors.map(m => ({
                name: m.name,
                interval: m.interval,
                lastRun: m.lastRun,
                runCount: m.runCount,
                errorCount: m.errorCount || 0
            })),
            alertCount: this.alertHistory.length
        };
    }
}

// 创建全局实例
const monitoringEngine = new QuantMonitoringEngine();

// 注册默认监控任务
monitoringEngine.registerMonitor({
    name: '止损监控',
    interval: 60000,           // 1分钟
    priority: 1,               // 最高优先级
    checkFn: checkStopLoss,
    alertFn: sendStopLossAlert
});

monitoringEngine.registerMonitor({
    name: '流动性监控',
    interval: 120000,          // 2分钟
    priority: 1,
    checkFn: checkLiquidity,
    alertFn: sendLiquidityAlert
});

monitoringEngine.registerMonitor({
    name: '市场状态监控',
    interval: 300000,          // 5分钟
    priority: 2,
    checkFn: monitorMarketRegimeChange,
    alertFn: sendRegimeChangeAlert
});

monitoringEngine.registerMonitor({
    name: 'ETF偏离度监控',
    interval: 600000,          // 10分钟
    priority: 2,
    checkFn: monitorPortfolioDrift,
    alertFn: sendRebalanceAlert
});

module.exports = monitoringEngine;
```

### 风险暴露监控（utils/risk_monitor.js）

```javascript
/**
 * 风险暴露监控
 * 防止单只股票亏损失控和账户回撤超限
 */

const RISK_THRESHOLDS = {
    MAX_SINGLE_LOSS_PCT: -8,        // 单只股票亏损阈值
    MAX_MAX_DRAWDOWN_PCT: -15,      // 总账户回撤阈值
    MAX_SINGLE_POSITION_PCT: 12,    // 单只股票仓位上限
    MAX_INDUSTRY_CONCENTRATION: 40  // 行业集中度上限
};

/**
 * 检查止损
 */
async function checkStopLoss() {
    const trades = wx.getStorageSync('PAPER_TRADES') || [];
    const account = wx.getStorageSync('PAPER_ACCOUNT') || {};

    const alerts = [];

    for (const trade of trades) {
        const { symbol, cost, quantity } = trade;

        try {
            const quote = await fetchStockDetail(symbol);
            const currentPnL = ((quote.price - cost) / cost * 100);

            // 🔴 CRITICAL: 触发止损
            if (currentPnL <= RISK_THRESHOLDS.MAX_SINGLE_LOSS_PCT) {
                // 执行止损
                await executeStopLoss(symbol, quantity, quote.price);

                alerts.push({
                    type: 'STOP_LOSS_TRIGGERED',
                    severity: 'CRITICAL',
                    symbol,
                    loss: currentPnL.toFixed(2),
                    action: '已自动卖出',
                    price: quote.price
                });
            }

            // ⚠️ 接近止损线
            if (currentPnL <= RISK_THRESHOLDS.MAX_SINGLE_LOSS_PCT + 2) {
                alerts.push({
                    type: 'STOP_LOSS_WARNING',
                    severity: 'WARNING',
                    symbol,
                    loss: currentPnL.toFixed(2),
                    message: `亏损${currentPnL.toFixed(2)}%，接近止损线`
                });
            }
        } catch (e) {
            console.error(`[风险监控] 获取${symbol}行情失败:`, e);
        }
    }

    // 检查总账户回撤
    const currentDrawdown = calculateMaxDrawdown(account);
    if (currentDrawdown <= RISK_THRESHOLDS.MAX_MAX_DRAWDOWN_PCT) {
        alerts.push({
            type: 'MAX_DRAWDOWN_TRIGGERED',
            severity: 'CRITICAL',
            drawdown: currentDrawdown.toFixed(2),
            action: '触发全局风控，停止所有开仓'
        });

        // 触发全局风控
        setGlobalRiskControl('EMERGENCY_STOP');
    }

    return {
        shouldAlert: alerts.length > 0,
        data: alerts
    };
}

/**
 * 检查仓位集中度
 */
async function checkPositionConcentration() {
    const trades = wx.getStorageSync('PAPER_TRADES') || [];
    const account = wx.getStorageSync('PAPER_ACCOUNT') || {};

    const alerts = [];

    // 计算单只股票仓位
    const totalAsset = account.totalAsset || 0;
    for (const trade of trades) {
        const positionValue = trade.quantity * trade.currentPrice;
        const positionPct = (positionValue / totalAsset * 100);

        if (positionPct > RISK_THRESHOLDS.MAX_SINGLE_POSITION_PCT) {
            alerts.push({
                type: 'POSITION_CONCENTRATION',
                severity: 'WARNING',
                symbol: trade.symbol,
                positionPct: positionPct.toFixed(2),
                message: `${trade.symbol}仓位${positionPct.toFixed(2)}%，超过${RISK_THRESHOLDS.MAX_SINGLE_POSITION_PCT}%`
            });
        }
    }

    // 计算行业集中度
    const industryDistribution = calculateIndustryDistribution(trades);
    for (const [industry, pct] of Object.entries(industryDistribution)) {
        if (pct > RISK_THRESHOLDS.MAX_INDUSTRY_CONCENTRATION) {
            alerts.push({
                type: 'INDUSTRY_CONCENTRATION',
                severity: 'WARNING',
                industry,
                concentration: pct.toFixed(2),
                message: `${industry}集中度${pct.toFixed(2)}%，超过${RISK_THRESHOLDS.MAX_INDUSTRY_CONCENTRATION}%`
            });
        }
    }

    return {
        shouldAlert: alerts.length > 0,
        data: alerts
    };
}

/**
 * 执行止损
 */
async function executeStopLoss(symbol, quantity, price) {
    console.log(`[风险监控] 🚨 执行止损: ${symbol}, 数量:${quantity}, 价格:${price}`);

    // TODO: 调用卖出逻辑
    // await executeSell(symbol, quantity, price);

    // 记录止损历史
    const history = wx.getStorageSync('STOP_LOSS_HISTORY') || [];
    history.push({
        symbol,
        quantity,
        price,
        timestamp: Date.now()
    });
    wx.setStorageSync('STOP_LOSS_HISTORY', history);
}

/**
 * 设置全局风控
 */
function setGlobalRiskControl(status) {
    wx.setStorageSync('GLOBAL_RISK_CONTROL', {
        status,
        timestamp: Date.now()
    });

    // 发送紧急通知
    sendUrgentAlert({
        type: 'GLOBAL_RISK_CONTROL',
        status,
        message: `系统已触发全局风控：${status}`
    });
}

module.exports = {
    checkStopLoss,
    checkPositionConcentration,
    RISK_THRESHOLDS
};
```

### 流动性监控（utils/liquidity_monitor.js）

```javascript
/**
 * 流动性监控
 * 防止买入流动性枯竭的股票
 */

/**
 * 检查流动性风险
 */
async function checkLiquidity() {
    const trades = wx.getStorageSync('PAPER_TRADES') || [];
    const alerts = [];

    for (const trade of trades) {
        try {
            const quote = await fetchStockDetail(trade.symbol);
            const turnoverRate = quote.turnover;  // 换手率
            const volume = quote.volume;          // 成交量

            // 🔴 CRITICAL: 流动性枯竭
            if (turnoverRate < 0.5) {
                alerts.push({
                    type: 'LIQUIDITY_DRY',
                    severity: 'WARNING',
                    symbol: trade.symbol,
                    turnoverRate: turnoverRate.toFixed(2),
                    message: `换手率仅${turnoverRate.toFixed(2)}%，流动性枯竭`,
                    advice: '可能无法及时卖出，建议提前清仓'
                });
            }

            // 🟡 WARNING: 异常放量（可能是出货信号）
            if (turnoverRate > 15) {
                alerts.push({
                    type: 'ABNORMAL_VOLUME',
                    severity: 'WARNING',
                    symbol: trade.symbol,
                    turnoverRate: turnoverRate.toFixed(2),
                    message: `换手率${turnoverRate.toFixed(2)}%，异常放量`,
                    advice: '可能是主力出货，建议密切关注'
                });
            }

            // 成交量过低
            if (volume < 1000) {  // 低于1000手
                alerts.push({
                    type: 'LOW_VOLUME',
                    severity: 'INFO',
                    symbol: trade.symbol,
                    volume: volume.toFixed(0),
                    message: `成交量仅${volume.toFixed(0)}手`,
                    advice: '成交清淡，注意流动性风险'
                });
            }
        } catch (e) {
            console.error(`[流动性监控] 获取${trade.symbol}行情失败:`, e);
        }
    }

    return {
        shouldAlert: alerts.length > 0,
        data: alerts
    };
}

/**
 * 计算流动性评分
 * @returns {Number} 0-100分，100分流动性最好
 */
function calculateLiquidityScore(trades) {
    let totalScore = 0;
    let count = 0;

    for (const trade of trades) {
        // TODO: 获取实时换手率
        // const turnoverRate = getTurnoverRate(trade.symbol);

        // 简化评分逻辑
        // if (turnoverRate > 5) totalScore += 100;
        // else if (turnoverRate > 2) totalScore += 80;
        // else if (turnoverRate > 1) totalScore += 60;
        // else totalScore += 40;

        count++;
    }

    return count > 0 ? Math.round(totalScore / count) : 0;
}

module.exports = {
    checkLiquidity,
    calculateLiquidityScore
};
```

### 市场状态监控（utils/market_state_monitor.js）

```javascript
/**
 * 市场状态监控
 * 及时发现市场状态切换
 */

const MARKET_TRANSITION_STRATEGIES = {
    'BULL->RANGING': {
        action: 'REDUCE_POSITION',
        targetPosition: 50,
        reason: '牛市转震荡，降低风险暴露',
        strategySwitch: '从激进策略转为平衡策略'
    },
    'RANGING->BEAR': {
        action: 'STOP_NEW_BUYS',
        targetPosition: 30,
        reason: '震荡转熊市，暂停开仓',
        strategySwitch: '从平衡策略转为防御策略'
    },
    'BEAR->BULL': {
        action: 'AGGRESSIVE_BUILD',
        targetPosition: 60,
        reason: '熊市转牛市，积极建仓',
        strategySwitch: '从防御策略转为激进策略'
    },
    'RANGING->BULL': {
        action: 'INCREASE_POSITION',
        targetPosition: 60,
        reason: '震荡转牛市，提高仓位',
        strategySwitch: '从平衡策略转为激进策略'
    },
    'BULL->BEAR': {
        action: 'EMERGENCY_EXIT',
        targetPosition: 30,
        reason: '牛市直接转熊，紧急退出',
        strategySwitch: '从激进策略转为防御策略'
    }
};

/**
 * 监控市场状态变化
 */
async function monitorMarketRegimeChange() {
    const previousRegime = wx.getStorageSync('LAST_MARKET_REGIME');
    const currentRegime = detectMarketRegime();  // 使用现有的市场状态判断函数

    if (!previousRegime) {
        // 首次运行，保存当前状态
        wx.setStorageSync('LAST_MARKET_REGIME', currentRegime);
        return { shouldAlert: false };
    }

    if (previousRegime !== currentRegime) {
        // 🚨 市场状态切换！
        const transition = `${previousRegime}->${currentRegime}`;
        const strategy = MARKET_TRANSITION_STRATEGIES[transition];

        const alert = {
            type: 'MARKET_REGIME_CHANGE',
            severity: 'IMPORTANT',
            from: previousRegime,
            to: currentRegime,
            transition,
            strategy: strategy || {},
            message: `市场状态切换：${previousRegime} → ${currentRegime}`,
            advice: strategy ? strategy.reason : '建议重新评估投资策略'
        };

        // 保存新状态
        wx.setStorageSync('LAST_MARKET_REGIME', currentRegime);

        // 记录历史
        const history = wx.getStorageSync('MARKET_REGIME_HISTORY') || [];
        history.push({
            from: previousRegime,
            to: currentRegime,
            timestamp: Date.now()
        });
        wx.setStorageSync('MARKET_REGIME_HISTORY', history);

        return {
            shouldAlert: true,
            data: [alert]
        };
    }

    return { shouldAlert: false };
}

module.exports = {
    monitorMarketRegimeChange
};
```

### 组合偏离度监控（utils/portfolio_monitor.js）

```javascript
/**
 * 组合偏离度监控
 * 确保ETF配置符合目标配置
 */

/**
 * 监控ETF配置偏离度
 */
async function monitorPortfolioDrift() {
    const trades = wx.getStorageSync('PAPER_TRADES') || [];
    const account = wx.getStorageSync('PAPER_ACCOUNT') || {};
    const marketState = detectMarketRegime();

    // 计算当前ETF配置
    const currentAllocation = calculateETFAllocation(trades);

    // 获取目标配置
    const targetAllocation = getTargetETFAllocation(marketState);

    // 计算偏离度
    const drift = calculateAllocationDrift(currentAllocation, targetAllocation);

    // 找出最大偏离度
    const maxDrift = Math.max(...Object.values(drift));

    if (maxDrift > 25) {
        // 🚨 偏离度过大，触发再平衡提醒
        const alert = {
            type: 'REBALANCE_NEEDED',
            severity: 'MEDIUM',
            maxDrift: maxDrift.toFixed(2),
            currentAllocation,
            targetAllocation,
            drift,
            message: `ETF配置偏离度${maxDrift.toFixed(1)}%，建议再平衡`,
            advice: generateRebalanceAdvice(currentAllocation, targetAllocation)
        };

        return {
            shouldAlert: true,
            data: [alert]
        };
    }

    return { shouldAlert: false };
}

/**
 * 计算当前ETF配置
 */
function calculateETFAllocation(trades) {
    let totalAsset = 0;
    const etfValue = {
        broad: 0,
        industry: 0,
        strategy: 0
    };

    trades.forEach(trade => {
        const value = trade.quantity * trade.currentPrice;
        totalAsset += value;

        // 判断ETF类型
        const etfInfo = getETFInfo(trade.symbol);
        if (etfInfo) {
            etfValue[etfInfo.type] += value;
        }
    });

    return {
        broad: totalAsset > 0 ? (etfValue.broad / totalAsset * 100) : 0,
        industry: totalAsset > 0 ? (etfValue.industry / totalAsset * 100) : 0,
        strategy: totalAsset > 0 ? (etfValue.strategy / totalAsset * 100) : 0
    };
}

/**
 * 计算偏离度
 */
function calculateAllocationDrift(current, target) {
    const drift = {};

    for (const key in current) {
        const currentVal = current[key];
        const targetVal = target[key];

        if (targetVal > 0) {
            drift[key] = Math.abs((currentVal - targetVal) / targetVal * 100);
        } else {
            drift[key] = 0;
        }
    }

    return drift;
}

/**
 * 生成再平衡建议
 */
function generateRebalanceAdvice(current, target) {
    const advice = {
        sell: [],   // 需要卖出的ETF
        buy: []     // 需要买入的ETF
    };

    for (const key in current) {
        const currentVal = current[key];
        const targetVal = target[key];
        const diff = currentVal - targetVal;

        if (diff > 2) {
            // 当前配置过高，需要卖出
            advice.sell.push({
                type: key,
                amount: diff.toFixed(2),
                action: `卖出${getTypeName(key)}ETF ${diff.toFixed(2)}%`
            });
        } else if (diff < -2) {
            // 当前配置过低，需要买入
            advice.buy.push({
                type: key,
                amount: Math.abs(diff).toFixed(2),
                action: `买入${getTypeName(key)}ETF ${Math.abs(diff).toFixed(2)}%`
            });
        }
    }

    return advice;
}

function getTypeName(type) {
    const names = {
        broad: '宽基',
        industry: '行业',
        strategy: '策略'
    };
    return names[type] || type;
}

module.exports = {
    monitorPortfolioDrift
};
```

### 页面集成（pages/monitor/monitor.js）

```javascript
// pages/monitor/monitor.js
const monitoringEngine = require('../../utils/monitoring_engine');

Page({
    data: {
        isRunning: false,
        alerts: [],
        accountSummary: null,
        riskStatus: 'NORMAL',
        monitorStatus: []
    },

    onLoad() {
        this.loadAccountSummary();
        this.loadAlertHistory();

        // 检查是否已有监控在运行
        const wasRunning = wx.getStorageSync('MONITORING_RUNNING');
        if (wasRunning) {
            this.startMonitoring();
        }
    },

    onShow() {
        // 页面显示时刷新数据
        this.loadAccountSummary();
        this.updateMonitorStatus();
    },

    /**
     * 开始监控
     */
    startMonitoring() {
        wx.showToast({ title: '启动监控...', icon: 'loading' });

        monitoringEngine.start();

        this.setData({ isRunning: true });

        // 保存监控状态
        wx.setStorageSync('MONITORING_RUNNING', true);

        // 定期刷新监控状态
        this.statusTimer = setInterval(() => {
            this.updateMonitorStatus();
        }, 5000);

        wx.showToast({ title: '监控已启动', icon: 'success' });
    },

    /**
     * 暂停监控
     */
    stopMonitoring() {
        monitoringEngine.stop();

        if (this.statusTimer) {
            clearInterval(this.statusTimer);
        }

        this.setData({ isRunning: false });
        wx.setStorageSync('MONITORING_RUNNING', false);

        wx.showToast({ title: '监控已暂停' });
    },

    /**
     * 加载账户摘要
     */
    async loadAccountSummary() {
        const trades = wx.getStorageSync('PAPER_TRADES') || [];
        const account = wx.getStorageSync('PAPER_ACCOUNT') || {};

        // 计算总盈亏、仓位等
        const summary = await calculateAccountSummary(trades, account);

        this.setData({ accountSummary: summary });
    },

    /**
     * 加载警告历史
     */
    loadAlertHistory() {
        const history = wx.getStorageSync('MONITOR_ALERT_HISTORY') || [];
        this.setData({ alerts: history.slice(0, 10) });  // 只显示最近10条
    },

    /**
     * 更新监控状态
     */
    updateMonitorStatus() {
        const status = monitoringEngine.getStatus();
        this.setData({ monitorStatus: status.monitors });
    },

    /**
     * 查看警告详情
     */
    viewAlertDetail(e) {
        const alert = e.currentTarget.dataset.alert;
        wx.showModal({
            title: '警告详情',
            content: JSON.stringify(alert, null, 2),
            showCancel: false
        });
    },

    /**
     * 查看完整历史
     */
    viewAlertHistory() {
        wx.navigateTo({ url: '/pages/alert-history/alert-history' });
    },

    /**
     * 查看账户详情
     */
    viewAccountDetail() {
        wx.navigateTo({ url: '/pages/paper/paper' });
    },

    onUnload() {
        // 页面卸载时暂停监控
        if (this.data.isRunning) {
            this.stopMonitoring();
        }

        if (this.statusTimer) {
            clearInterval(this.statusTimer);
        }
    }
});
```

---

## 📋 实现路线图

### P0: 核心风控（必须实现）⏱ 2-3天

**目标**: 防止 catastrophic loss

- [x] 监控引擎框架（`utils/monitoring_engine.js`）
- [ ] 止损监控
  - [ ] 单只股票亏损监控
  - [ ] 自动止损执行
  - [ ] 止损历史记录
- [ ] 流动性监控
  - [ ] 换手率监控
  - [ ] 异常放量检测
  - [ ] 流动性评分
- [ ] 全局风控
  - [ ] 账户回撤监控
  - [ ] 紧急停止机制
  - [ ] 风控状态持久化

**验收标准**:
- 亏损超-8%自动止损
- 回撤超-15%自动停止开仓
- 流动性枯竭及时警告

---

### P1: 组合管理（重要功能）⏱ 2-3天

**目标**: 优化ETF配置，跟随市场状态

- [ ] 市场状态监控
  - [ ] 牛熊震荡状态切换检测
  - [ ] 状态变化提醒
  - [ ] 仓位调整建议
- [ ] ETF偏离度监控
  - [ ] 当前配置计算
  - [ ] 偏离度计算
  - [ ] 再平衡提醒
  - [ ] 调仓建议生成

**验收标准**:
- 市场切换时及时提醒
- 偏离度>25%触发再平衡
- 提供具体调仓建议

---

### P2: 体验优化（提升用户体验）⏱ 2-3天

**目标**: 提供直观的监控界面

- [ ] 监控中心页面
  - [ ] 实时风险面板
  - [ ] 异常事件列表
  - [ ] 组合分析展示
  - [ ] 监控状态展示
- [ ] 警告管理
  - [ ] 警告历史页面
  - [ ] 警告详情查看
  - [ ] 警告筛选和搜索
- [ ] 风险仪表盘
  - [ ] 可视化图表
  - [ ] 关键指标卡片
  - [ ] 趋势分析

**验收标准**:
- 界面直观易懂
- 警告信息清晰
- 操作流畅无卡顿

---

### P3: 高级功能（锦上添花）⏱ 3-5天

**目标**: 增强系统能力

- [ ] 订阅消息推送
  - [ ] 离开小程序也能收到警告
  - [ ] 紧急警告实时推送
  - [ ] 每日监控报告
- [ ] VaR（风险价值）计算
  - [ ] 历史波动率计算
  - [ ] VaR模型（参数法/历史法）
  - [ ] 风险归因分析
- [ ] 压力测试
  - [ ] 市场暴跌情景模拟
  - [ ] 极端情况测试
  - [ ] 抗风险能力评估

**验收标准**:
- 订阅消息送达率>90%
- VaR计算误差<10%
- 压力测试结果可信

---

## 🔗 与现有系统集成

### 利用已有功能

1. **自动建仓系统**
   - 监控AI审核完成事件
   - 建仓前检查流动性
   - 建仓后更新监控列表

2. **智能轮换**
   - 监控卖出事件
   - 轮换时检查候选股票流动性
   - 自动补充观察池

3. **市场状态适配**
   - 监控市场状态变化
   - 自动调整目标仓位
   - 提示策略切换

4. **自动止损止盈**
   - 增强 `runAutoSignalCheck` 为监控任务
   - 添加止损执行逻辑
   - 记录止损历史

### 新增功能

1. **流动性监控**（机构非常重视）
2. **组合偏离度监控**（已有再平衡，改为自动触发）
3. **全局风控**（回撤超限自动停止所有开仓）

### 数据流图

```
现有系统
    │
    ├─> AI审核 ──┐
    ├─> 自动建仓 ─┼─> 持仓数据 ──> 监控引擎 ──> 警告/执行
    ├─> 智能轮换 ──┘
    │
    └─> 市场状态 ──> 监控引擎 ──> 仓位调整建议
```

---

## 🤔 需要讨论的问题

### 1. 监控频率

**止损监控**:
- 选项A: 30秒（最快，但API压力大）
- 选项B: 1分钟（推荐，平衡速度和压力）
- 选项C: 2分钟（保守，适合低频交易）

**建议**: 1分钟，平衡实时性和API压力

---

### 2. 监控范围

**选项A**: 只监控持仓（实现简单）
**选项B**: 监控持仓 + 自选池（全面，但复杂）

**建议**: 先实现选项A，P2阶段扩展到选项B

---

### 3. 自动执行 vs 提醒确认

**止损执行**:
- 选项A: 完全自动（符合量化理念）
- 选项B: 提醒后手动确认（更保守）

**建议**: 选项A（自动执行），但提供"模拟模式"开关

---

### 4. 全局风控阈值

**账户回撤阈值**:
- 选项A: -10%（严格）
- 选项B: -15%（中等，推荐）
- 选项C: -20%（宽松）

**建议**: -15%，并在设置中可调

---

## 📚 参考资料

### 机构风控系统
- Renaissance Technologies（文艺复兴科技）
- Two Sigma（二西格玛）
- Citadel（城堡投资）

### 量化风控指标
- VaR（Value at Risk）
- Maximum Drawdown（最大回撤）
- Sharpe Ratio（夏普比率）
- Liquidity Risk（流动性风险）

### 相关论文
- "Risk Management for Quantitative Trading"
- "Portfolio Rebalancing: Theory and Practice"

---

## 📝 附录

### 术语表

| 术语 | 解释 |
|------|------|
| VaR | Value at Risk，风险价值，在一定置信水平下，投资组合在给定时间内的最大可能损失 |
| Drawdown | 回撤，从峰值到谷底的下跌幅度 |
| Liquidity | 流动性，资产转换为现金而不影响价格的能力 |
| Turnover Rate | 换手率，成交量/流通股本，反映交易活跃度 |
| Market Regime | 市场状态，如牛市/熊市/震荡市 |

### 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-01-30 | 初始版本 |

---

**文档结束**

> 本设计方案参考了顶级量化投资机构的最佳实践，结合StockQuant现有系统的特点，提供了一套完整的监控解决方案。

---

## 🔍 方案分析与改进建议

> **分析者**: Antigravity AI
> **分析时间**: 2026-01-30

---

### ✅ 方案优点

1.  **设计理念正确**
    -   "事件驱动，非定时轮询" 符合现代量化系统的最佳实践。
    -   "分层监控"（L1/L2/L3）合理分配资源，避免不必要的API请求。
    -   "噪音抑制"（Suppression）机制防止警报疲劳。

2.  **四大监控维度覆盖全面**
    -   **风险暴露**：单票止损 + 账户回撤双保险。
    -   **市场状态**：主动适应牛熊转换，比被动止损更进一步。
    -   **流动性**：这是许多个人量化系统忽略的维度，非常专业。
    -   **组合偏离**：与已有的再平衡功能无缝衔接。

3.  **代码实现可行**
    -   `QuantMonitoringEngine` 类设计清晰，易于扩展。
    -   与现有 `paper.js`、`market_regime.js` 等模块集成点明确。
    -   路线图优先级合理（P0风控 > P1组合 > P2体验 > P3高级）。

---

### ⚠️ 潜在问题与风险

#### 1. 微信小程序后台限制

> [!CAUTION]
> **核心技术风险**：微信小程序的 `setInterval` 在页面切换或手机锁屏后会被系统暂停或销毁。

**问题描述**：
-   用户离开监控页面后，`setInterval` 定时器可能不再执行。
-   小程序进入后台 5 分钟后通常会被系统挂起。
-   这意味着"1分钟止损监控"在用户不打开小程序时**完全失效**。

**建议方案**：
```javascript
// 方案A：利用 onShow 生命周期触发巡检
onShow() {
    // 每次页面显示时，立即执行一次所有高优先级监控
    this.runMonitor(this.monitors.find(m => m.name === '止损监控'));
}

// 方案B：云函数定时任务（需要后端支持）
// 在云函数中运行监控，通过订阅消息推送告警

// 方案C：明确告知用户限制
// 在UI中显示："监控仅在小程序打开时有效"
```

**最终建议**：采用 **方案A + 方案C** 组合。在 `paper.js` 的 `onShow` 中调用 `runAutoSignalCheck`（本质上就是止损巡检），并在监控页面明确告知用户"后台监控存在限制"。

---

#### 2. API 请求压力

**问题描述**：
-   止损监控每 1 分钟检查所有持仓，假设持仓 10 只股票 = 每分钟 10 次 API 请求。
-   加上流动性监控（2分钟/10次），每小时约 **600+ 次请求**。
-   可能触发新浪/腾讯的反爬虫机制。

**建议方案**：
```javascript
// 方案：批量请求代替逐只查询
// 使用 fetchQuotes 一次获取多只股票数据
async function checkStopLossBatch() {
    const trades = wx.getStorageSync('PAPER_TRADES') || [];
    const symbols = trades.map(t => t.symbol);
    
    // 🔴 关键：一次请求获取所有股票实时价格
    const quotes = await fetchQuotes(symbols);
    
    // 然后在内存中计算止损
    for (const trade of trades) {
        const quote = quotes[trade.symbol];
        // ... 止损逻辑
    }
}
```

---

#### 3. 自动止损的执行风险

**问题描述**：
-   代码中 `executeStopLoss` 函数标记为 `// TODO`，尚未实现。
-   自动卖出逻辑如果与手动操作并发，可能导致数据竞争（与之前修复的 Race Condition 类似）。

**建议方案**：
-   复用 `paper.js` 中已有的 `closeTrade` 函数。
-   在执行前设置 `_isAutoClosing` 锁，防止并发。
-   执行后调用 `_saveTradesSafely` 保证数据一致性。

```javascript
async function executeStopLoss(symbol, quantity, price) {
    // 复用现有平仓逻辑
    const paperPage = getCurrentPages().find(p => p.route === 'pages/paper/paper');
    if (paperPage && !paperPage.data._isAutoClosing) {
        await paperPage.closeTrade({
            currentTarget: { dataset: { trade: { symbol } } }
        });
    }
}
```

---

#### 4. 全局风控的解除机制

**问题描述**：
-   设计文档中只提到"触发全局风控，停止所有开仓"。
-   但没有说明如何**解除**风控状态（用户需要手动确认？还是第二天自动解除？）。

**建议方案**：
-   添加"解除风控"按钮，需要用户**双重确认**。
-   可选：提供"观望期"选项（如：停止开仓 24 小时后自动解除）。

---

### 💡 改进建议

#### 建议 1：简化 P0 范围

当前 P0 包含"止损 + 流动性 + 全局风控"，工作量偏大（预估 2-3 天可能不够）。

**建议**：
-   **P0（1-2天）**：只实现止损监控 + 警告展示，不含自动执行。
-   **P0.5（1天）**：添加自动执行 + 全局风控。
-   **P1**：流动性监控（可降级为"仅警告，不阻止交易"）。

---

#### 建议 2：复用现有代码

以下现有代码可以直接复用，减少开发量：

| 监控任务 | 可复用代码 | 复用程度 |
|----------|-----------|---------|
| 止损监控 | `paper.js > runAutoSignalCheck` | 高（改造即可） |
| 市场状态 | `market_regime.js > detectMarketRegime` | 直接使用 |
| ETF偏离度 | `paper.js > calculateRebalanceNeeds` | 直接使用 |
| 流动性 | `liquidity_checker.js` | 部分复用 |

---

#### 建议 3：监控页面可选

考虑到微信小程序的限制，建议将"监控中心"作为**可选功能**，而非核心功能。

**替代方案**：
-   在 `paper.js` 的 `onShow` 中自动执行所有巡检。
-   将警告显示在现有的"模拟交易"页面顶部（类似现有的 Banner 设计）。
-   这样用户无需单独打开监控页面，每次进入实验页都会自动巡检。

---

#### 建议 4：渐进式实现

| 阶段 | 功能 | 预计时间 | 依赖 |
|------|------|----------|------|
| **阶段 0** | 在 `paper.js` onShow 中添加止损巡检 | 0.5 天 | 无 |
| **阶段 1** | 添加警告 Banner UI | 0.5 天 | 阶段 0 |
| **阶段 2** | 自动止损执行 | 1 天 | 阶段 1 |
| **阶段 3** | 流动性警告 | 1 天 | 阶段 1 |
| **阶段 4** | 独立监控页面 | 2 天 | 阶段 2/3 |

---

### 📊 总结评分

| 维度 | 评分 | 说明 |
|------|------|------|
| **设计完整性** | ⭐⭐⭐⭐⭐ | 四大维度覆盖全面，参考了机构最佳实践 |
| **代码可行性** | ⭐⭐⭐⭐☆ | 代码清晰，但需注意微信小程序限制 |
| **实现优先级** | ⭐⭐⭐⭐⭐ | P0-P3 优先级合理 |
| **与现有系统集成** | ⭐⭐⭐⭐☆ | 集成点明确，但需复用更多现有代码 |
| **工期估算** | ⭐⭐⭐☆☆ | 预估偏乐观，建议按渐进式实现 |

**总体评价**：这是一份**高质量的设计文档**，体现了专业的量化投资理念。主要风险在于微信小程序的后台限制，建议采用渐进式实现策略，优先在现有页面中嵌入巡检逻辑，再逐步构建独立监控页面。

---

### 📱 推荐使用模式：「偶尔打开」触发式监控

#### 核心理念

> **用户不需要长期打开小程序。每次打开时，系统自动执行一次全面巡检，完成所有必要的监控和操作。**

#### 模式对比

| 维度 | 长期打开模式 ❌ | 偶尔打开模式 ✅ |
|------|---------------|----------------|
| **用户负担** | 需要保持小程序在前台 | 每天打开 1-2 次即可 |
| **耗电** | 高（后台定时器） | 低（按需执行） |
| **可靠性** | 依赖后台存活（不可靠） | 每次打开都执行（可靠） |
| **API压力** | 每分钟请求（高） | 每次打开请求（低） |

#### 实现方案

**利用 `onShow` 生命周期强化现有能力**：

```javascript
// pages/paper/paper.js
onShow() {
    // 🔴 每次打开模拟交易页面时，自动执行以下任务：
    
    // 1️⃣ 止损巡检：检查是否有持仓触及止损线
    this.runAutoSignalCheck();
    
    // 2️⃣ 流动性检查：检查持仓股票是否有流动性风险
    this.checkLiquidityRisk();  // 新增
    
    // 3️⃣ 市场状态检查：判断牛熊震荡，调整策略
    this.checkMarketRegimeChange();  // 新增
    
    // 4️⃣ ETF偏离度检查：是否需要再平衡
    this.checkRebalanceNeeds();  // 已有类似逻辑
    
    // 5️⃣ 显示警告摘要（如有）
    this.showRiskSummaryBanner();  // 新增
}
```

#### 推荐使用习惯

| 时间点 | 用户操作 | 系统行为 |
|--------|---------|---------|
| **早盘 9:30** | 打开小程序 | 自动巡检，显示隔夜风险 |
| **午盘 11:30** | 可选：打开小程序 | 自动巡检，显示上午异常 |
| **尾盘 14:50** | 打开小程序 | 自动巡检，显示全天总结 |
| **盘后** | 不需要打开 | 无操作（数据不变） |

**关键点**：
- 用户每天打开 **1-3 次** 即可覆盖所有风险监控
- 每次打开都会触发完整巡检，不会遗漏
- 巡检结果以 **Banner** 形式显示在页面顶部

#### 进一步自动化：订阅消息推送（P3 可选）

如果用户希望"完全不打开小程序也能收到通知"，可以利用微信的 **订阅消息** 功能：

```javascript
// 方案：云函数 + 订阅消息
// 1. 用户一次性订阅"风险提醒"模板
// 2. 后端云函数每天 9:30/15:00 执行巡检
// 3. 发现问题时推送订阅消息

// 注意：此方案需要云开发支持，复杂度较高，属于 P3 功能
```

#### 功能与打开频率对照表

| 优先级 | 功能 | 用户需要打开小程序？ |
|--------|------|---------------------|
| **P0** | 止损巡检（onShow 触发） | 是（每天 1-2 次） |
| **P1** | 流动性/市场状态/偏离度巡检 | 是 |
| **P2** | 警告 Banner UI | 是 |
| **P3** | 订阅消息推送 | 否（后台推送） |

**结论**：当前阶段（P0-P2），用户需要 **每天打开小程序 1-2 次**，每次打开时系统自动完成所有监控任务。这是最务实且可靠的设计。

---

### ☁️ 未来演进：云端 24 小时监控（P3+）

#### 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    微信云开发架构                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│   ⏰ 定时触发器 ─────────────────────────────────────┐   │
│   (每分钟/每5分钟)                                   │   │
│                                                      ▼   │
│   ┌─────────────────────────────────────────────────┐   │
│   │            云函数 (Node.js)                      │   │
│   │  1. 读取用户持仓数据（云数据库）                   │   │
│   │  2. 获取实时行情（第三方 API）                    │   │
│   │  3. 执行监控逻辑（止损/流动性/市场状态）           │   │
│   │  4. 发现问题 → 发送订阅消息                       │   │
│   └─────────────────────────────────────────────────┘   │
│                         │                               │
│                         ▼                               │
│   ┌─────────────────────────────────────────────────┐   │
│   │        微信订阅消息                              │   │
│   │  → 推送到用户手机通知栏                          │   │
│   │  → 用户点击可直接打开小程序                       │   │
│   └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### 需要解决的问题

| 问题 | 说明 | 解决方案 |
|------|------|----------|
| **数据同步** | 用户持仓数据目前存在本地 Storage | 需要同步到云数据库 |
| **行情数据** | 云函数需要能访问股票行情 | 使用第三方 API（如新浪/腾讯） |
| **订阅消息限制** | 用户需要主动订阅，且每次只能发一条 | 提示用户订阅"风险提醒" |
| **云函数调用量** | 每分钟执行 = 每天 1440 次调用 | 可能需要付费（超出免费额度） |
| **实时性** | 云函数最小触发间隔 1 分钟 | 对于止损可能略慢，但可接受 |

#### 成本估算

微信云开发免费额度（个人使用 1-10 用户基本在免费额度内）：

| 资源 | 免费额度/月 | 预估使用量 | 是否够用 |
|------|------------|-----------|---------|
| **云函数调用** | 50 万次 | ~4.3 万次（每分钟执行） | ✅ 够用 |
| **云函数资源** | 10 万 GBs | 取决于执行时间 | ⚠️ 需监控 |
| **云数据库读取** | 5 万次/天 | 取决于用户数 | ⚠️ 需监控 |
| **订阅消息** | 无限制 | - | ✅ 够用 |

#### 云端监控实现路线图

| 阶段 | 任务 | 预计时间 |
|------|------|----------|
| **阶段 1** | 开通微信云开发 + 创建云数据库 | 0.5 天 |
| **阶段 2** | 持仓数据同步（本地 → 云端） | 1 天 |
| **阶段 3** | 云函数：止损监控 | 1 天 |
| **阶段 4** | 定时触发器配置 | 0.5 天 |
| **阶段 5** | 订阅消息模板申请 + 推送 | 1 天 |
| **阶段 6** | 测试与调优 | 1 天 |

**总计**：约 **5 天** 开发时间

#### 适用场景判断

| 场景 | 建议 |
|------|------|
| **个人使用，每天能打开 1-2 次** | ❌ 不需要，onShow 巡检足够 |
| **个人使用，经常忘记打开** | ✅ 值得做，自动提醒 |
| **多用户使用，希望提供增值服务** | ✅ 值得做，是核心卖点 |
| **追求极致实时性（秒级）** | ❌ 云函数最小 1 分钟，不够快 |

#### 云函数示例代码

```javascript
// cloudfunctions/monitorStopLoss/index.js
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });

const db = cloud.database();

exports.main = async (event, context) => {
    // 1. 获取所有用户的持仓数据
    const usersResult = await db.collection('user_trades').get();
    const users = usersResult.data;

    const alerts = [];

    for (const user of users) {
        const { openid, trades } = user;

        // 2. 获取实时行情（批量）
        const symbols = trades.map(t => t.symbol);
        const quotes = await fetchQuotesBatch(symbols);  // 需实现

        // 3. 检查止损
        for (const trade of trades) {
            const quote = quotes[trade.symbol];
            const pnl = ((quote.price - trade.cost) / trade.cost * 100);

            if (pnl <= -8) {  // 止损线
                alerts.push({
                    openid,
                    symbol: trade.symbol,
                    pnl: pnl.toFixed(2),
                    action: 'STOP_LOSS'
                });
            }
        }
    }

    // 4. 发送订阅消息
    for (const alert of alerts) {
        await cloud.openapi.subscribeMessage.send({
            touser: alert.openid,
            templateId: 'YOUR_TEMPLATE_ID',
            data: {
                thing1: { value: `${alert.symbol} 触发止损` },
                number2: { value: `${alert.pnl}%` },
                time3: { value: new Date().toLocaleString() }
            }
        });
    }

    return { alertCount: alerts.length };
};
```

#### 定时触发器配置

```json
// cloudfunctions/monitorStopLoss/config.json
{
    "triggers": [
        {
            "name": "stopLossTimer",
            "type": "timer",
            "config": "0 */1 9-15 * * 1-5"  // 工作日 9:00-15:00 每分钟执行
        }
    ]
}
```

> [!NOTE]
> 云端监控属于 P3+ 高级功能，建议在 P0-P2 完成后再考虑实现。对于个人用户，「偶尔打开」触发式监控已经足够满足日常需求。

---

**建议结束**

