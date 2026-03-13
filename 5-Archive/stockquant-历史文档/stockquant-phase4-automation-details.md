# Phase 4: 完全自动化执行引擎 - 详细实施指南

> **分级决策系统 + 5重熔断机制**
>
> **日期**: 2026-02-01
> **实施周期**: 1周
> **风险等级**: 中（需要严格的测试）

---

## 目录

1. [分级决策系统](#1-分级决策系统)
2. [风险评估算法](#2-风险评估算法)
3. [熔断机制实现](#3-熔断机制实现)
4. [微信通知交互](#4-微信通知交互)
5. [操作日志与审计](#5-操作日志与审计)

---

## 1. 分级决策系统

### 1.1 决策层级设计

**核心理念**: 根据风险等级，自动化程度递减

```
Level 1 (AUTO):     全自动执行 → 低风险操作
Level 2 (SEMI):     AI建议+审核 → 中风险操作
Level 3 (MANUAL):   仅通知 → 高风险操作
```

**风险评估矩阵**:

| 风险维度 | AUTO | SEMI | MANUAL |
|---------|------|------|--------|
| **单笔金额** | ≤3万 | 3-10万 | >10万 |
| **AI信心度** | ≥75% | 60-75% | <60% |
| **组合回撤** | ≤5% | 5-10% | >10% |
| **日交易次数** | ≤5次 | 5-10次 | >10次 |
| **市场状态** | 正常 | 警惕 | 极端 |

---

### 1.2 核心代码实现

```javascript
// cloudfunctions/autoTradingEngine/index.js

const cloud = require('wx-server-sdk');
cloud.init();
const db = cloud.database();

class AutoTradingEngine {
    constructor() {
        // 决策阈值配置
        this.thresholds = {
            AUTO: {
                maxPosition: 30000,
                maxDailyTrades: 5,
                minConfidence: 0.75,
                maxDrawdown: 0.05
            },
            SEMI: {
                maxPosition: 100000,
                maxDailyTrades: 10,
                minConfidence: 0.60,
                maxDrawdown: 0.10
            }
        };
    }

    /**
     * 智能决策路由
     * @param {Object} signal 交易信号
     * @param {Object} portfolio 组合状态
     * @param {Object} aiPrediction AI预测
     * @returns {Object} 决策结果
     */
    async makeDecision(signal, portfolio, aiPrediction) {
        console.log('开始决策评估...');

        // Step 1: 检查熔断状态
        const isCircuitBreaker = await this.checkCircuitBreaker(portfolio);
        if (isCircuitBreaker) {
            return {
                action: 'HOLD',
                reason: '熔断触发，暂停交易',
                level: 'CIRCUIT_BREAKER'
            };
        }

        // Step 2: 评估风险等级
        const riskLevel = await this.assessRiskLevel(signal, portfolio, aiPrediction);

        console.log(`风险等级: ${riskLevel}`);

        // Step 3: 根据等级执行
        switch (riskLevel) {
            case 'AUTO':
                return await this.executeAutoTrade(signal);

            case 'SEMI':
                return await this.executeSemiAuto(signal, portfolio);

            case 'MANUAL':
                return await this.sendManualNotification(signal);

            default:
                throw new Error('未知风险等级: ' + riskLevel);
        }
    }

    /**
     * 风险等级评估
     */
    async assessRiskLevel(signal, portfolio, aiPrediction) {
        const risks = {
            positionRisk: this.assessPositionRisk(signal),
            portfolioRisk: await this.assessPortfolioRisk(portfolio),
            aiRisk: this.assessAIRisk(aiPrediction),
            marketRisk: await this.assessMarketRisk(),
            frequencyRisk: await this.assessFrequencyRisk(portfolio)
        };

        console.log('风险评估:', risks);

        // 计算总分
        const riskScore = Object.values(risks).reduce((a, b) => a + b, 0);

        // 风险等级判定
        if (riskScore === 0) {
            return 'AUTO';  // 无风险
        } else if (riskScore <= 2) {
            return 'SEMI';  // 低风险
        } else {
            return 'MANUAL';  // 中高风险
        }
    }

    /**
     * 评估单笔金额风险
     * @returns {number} 0=AUTO, 1=SEMI, 2=MANUAL
     */
    assessPositionRisk(signal) {
        if (signal.position <= this.thresholds.AUTO.maxPosition) {
            return 0;
        } else if (signal.position <= this.thresholds.SEMI.maxPosition) {
            return 1;
        } else {
            return 2;
        }
    }

    /**
     * 评估组合风险
     */
    async assessPortfolioRisk(portfolio) {
        const drawdown = portfolio.drawdown || 0;

        if (drawdown <= this.thresholds.AUTO.maxDrawdown) {
            return 0;
        } else if (drawdown <= this.thresholds.SEMI.maxDrawdown) {
            return 1;
        } else {
            return 2;
        }
    }

    /**
     * 评估AI风险
     */
    assessAIRisk(aiPrediction) {
        if (!aiPrediction) {
            return 2;  // 无AI预测，高风险
        }

        if (aiPrediction.confidence >= this.thresholds.AUTO.minConfidence) {
            return 0;
        } else if (aiPrediction.confidence >= this.thresholds.SEMI.minConfidence) {
            return 1;
        } else {
            return 2;
        }
    }

    /**
     * 评估市场风险
     */
    async assessMarketRisk() {
        // 获取市场状态
        const marketRes = await db.collection('market_state')
            .orderBy('timestamp', 'desc')
            .limit(1)
            .get();

        if (marketRes.data.length === 0) {
            return 1;
        }

        const regime = marketRes.data[0].regime;

        // 熊市风险更高
        if (regime === 'BEAR') {
            return 2;
        } else if (regime === 'RANGING') {
            return 1;
        } else {
            return 0;  // BULL
        }
    }

    /**
     * 评估交易频率风险
     */
    async assessFrequencyRisk(portfolio) {
        // 获取今日交易次数
        const today = new Date().toISOString().split('T')[0];
        const tradesRes = await db.collection('trade_history')
            .where({
                tradeDate: today
            })
            .get();

        const todayCount = tradesRes.data.length;

        if (todayCount <= this.thresholds.AUTO.maxDailyTrades) {
            return 0;
        } else if (todayCount <= this.thresholds.SEMI.maxDailyTrades) {
            return 1;
        } else {
            return 2;
        }
    }

    /**
     * 执行全自动交易
     */
    async executeAutoTrade(signal) {
        console.log('执行全自动交易:', signal);

        try {
            // 执行交易
            const result = await this.placeOrder(signal);

            // 记录日志
            await this.logTrade({
                ...signal,
                level: 'AUTO',
                status: 'EXECUTED',
                result,
                timestamp: Date.now()
            });

            return {
                action: signal.action,
                status: 'EXECUTED',
                level: 'AUTO',
                result
            };

        } catch (e) {
            console.error('自动交易失败:', e);

            await this.logTrade({
                ...signal,
                level: 'AUTO',
                status: 'FAILED',
                error: e.message,
                timestamp: Date.now()
            });

            return {
                action: 'HOLD',
                status: 'FAILED',
                level: 'AUTO',
                error: e.message
            };
        }
    }

    /**
     * 执行半自动交易（AI建议+人工审核）
     */
    async executeSemiAuto(signal, portfolio) {
        console.log('执行半自动交易:', signal);

        // 发送微信通知
        const notificationId = await this.sendWeChatNotification({
            title: '🤖 AI建议交易',
            content: this.formatSignalMessage(signal),
            actions: [
                { text: '✅ 批准', action: 'approve' },
                { text: '❌ 拒绝', action: 'reject' },
                { text: '📊 详情', action: 'view' }
            ],
            timeout: 30 * 60 * 1000  // 30分钟超时
        });

        // 等待用户响应（异步）
        // 使用云函数定时任务轮询检查响应

        return {
            action: 'PENDING',
            status: 'WAITING_USER_CONFIRMATION',
            level: 'SEMI',
            notificationId
        };
    }

    /**
     * 发送人工决策通知
     */
    async sendManualNotification(signal) {
        console.log('发送人工决策通知:', signal);

        await this.sendWeChatNotification({
            title: '⚠️ 高风险交易建议',
            content: this.formatSignalMessage(signal),
            actions: [
                { text: '📊 查看详情', action: 'view' }
            ],
            priority: 'HIGH'
        });

        return {
            action: 'MANUAL_REVIEW_REQUIRED',
            status: 'WAITING_MANUAL_REVIEW',
            level: 'MANUAL'
        };
    }

    /**
     * 格式化交易信号消息
     */
    formatSignalMessage(signal) {
        return `
股票: ${signal.name} (${signal.symbol})
操作: ${signal.action === 'BUY' ? '买入' : '卖出'}
金额: ¥${signal.position.toLocaleString()}
理由: ${signal.reason}
预期收益: ${signal.expectedReturn ? (signal.expectedReturn * 100).toFixed(2) + '%' : 'N/A'}
风险: ${signal.risk ? (signal.risk * 100).toFixed(2) + '%' : 'N/A'}
        `.trim();
    }

    /**
     * 下单（模拟）
     */
    async placeOrder(signal) {
        // 实际项目中，这里对接券商API
        // 这里返回模拟结果

        return {
            orderId: 'ORDER_' + Date.now(),
            price: signal.price,
            quantity: signal.quantity,
            status: 'FILLED',
            executionTime: new Date().toISOString()
        };
    }

    /**
     * 发送微信通知
     */
    async sendWeChatNotification(notification) {
        try {
            const result = await cloud.callFunction({
                name: 'sendNotification',
                data: notification
            });

            return result.result.notificationId;
        } catch (e) {
            console.error('发送通知失败:', e);
            throw e;
        }
    }

    /**
     * 记录交易日志
     */
    async logTrade(logEntry) {
        await db.collection('trade_log').add({
            data: logEntry
        });
    }
}

module.exports = AutoTradingEngine;
```

---

## 2. 风险评估算法

### 2.1 Kelly公式动态调整

```javascript
// utils/kellyCalculator.js

class KellyCalculator {
    /**
     * 计算最优仓位
     * @param {Object} stock 股票对象
     * @param {Object} portfolio 组合对象
     * @returns {number} 仓位比例 (0-1)
     */
    calculateOptimalPosition(stock, portfolio) {
        // 1. 基础Kelly
        const baseKelly = this.calculateBaseKelly(stock);

        // 2. ATR调整
        const atrAdjusted = this.adjustForATR(baseKelly, stock);

        // 3. 市场环境调整
        const regimeAdjusted = this.adjustForRegime(atrAdjusted, portfolio);

        // 4. 风险预算调整
        const riskAdjusted = this.adjustForRisk(regimeAdjusted, portfolio);

        // 5. 约束检查
        const finalPosition = this.applyConstraints(riskAdjusted, portfolio);

        return finalPosition;
    }

    /**
     * 基础Kelly公式
     * f* = (bp - q) / b
     */
    calculateBaseKelly(stock) {
        const winRate = stock.winRate || 0.65;
        const avgWin = stock.avgWin || 0.05;
        const avgLoss = stock.avgLoss || 0.04;

        const b = avgWin / avgLoss;  // 盈亏比
        const p = winRate;  // 胜率
        const q = 1 - p;  // 败率

        const kelly = (b * p - q) / b;

        // 使用Half-Kelly，降低风险
        return Math.max(0, kelly * 0.5);
    }

    /**
     * ATR波动率调整
     */
    adjustForATR(kelly, stock) {
        const atr = stock.atr || 0.02;
        const price = stock.price || 10;

        // ATR百分比
        const atrPercent = atr / price;

        // 低波动(<1.5%) → 增加仓位
        // 高波动(>3%) → 降低仓位
        if (atrPercent < 0.015) {
            return kelly * 1.5;
        } else if (atrPercent > 0.03) {
            return kelly * 0.5;
        } else {
            return kelly;
        }
    }

    /**
     * 市场环境调整
     */
    adjustForRegime(kelly, portfolio) {
        const regime = portfolio.marketRegime || 'RANGING';

        const multipliers = {
            'BULL': 1.3,
            'RANGING': 1.0,
            'BEAR': 0.3
        };

        return kelly * (multipliers[regime] || 1.0);
    }

    /**
     * 风险预算调整
     */
    adjustForRisk(kelly, portfolio) {
        const drawdown = portfolio.drawdown || 0;

        // 回撤越大，仓位越小
        if (drawdown > 0.10) {
            return kelly * 0.5;
        } else if (drawdown > 0.05) {
            return kelly * 0.8;
        } else {
            return kelly;
        }
    }

    /**
     * 应用约束
     */
    applyConstraints(position, portfolio) {
        // 单股上限
        const maxSingle = 0.15;
        position = Math.min(position, maxSingle);

        // 单股下限
        const minSingle = 0.02;
        position = Math.max(position, minSingle);

        // 组合总仓位限制
        const currentExposure = portfolio.exposure || 0;
        const maxTotalExposure = 0.85;

        if (currentExposure >= maxTotalExposure) {
            return 0;  // 已满仓
        }

        const remaining = maxTotalExposure - currentExposure;
        position = Math.min(position, remaining);

        return position;
    }
}

module.exports = KellyCalculator;
```

---

## 3. 熔断机制实现

### 3.1 5重熔断系统

```javascript
// cloudfunctions/circuitBreaker/index.js

const cloud = require('wx-server-sdk');
cloud.init();
const db = cloud.database();

class CircuitBreakerSystem {
    constructor() {
        this.triggers = {
            DAILY_LOSS: 'dailyLoss',
            MAX_DRAWDOWN: 'maxDrawdown',
            CONSECUTIVE_LOSSES: 'consecutiveLosses',
            SYSTEM_FAILURE: 'systemFailure',
            MANUAL_OVERRIDE: 'manualOverride'
        };

        this.thresholds = {
            dailyLoss: -0.05,          // 单日亏损 >5%
            maxDrawdown: -0.15,         // 总回撤 >15%
            consecutiveLosses: 3,       // 连续3笔亏损
            systemFailure: 10           // API连续失败10次
        };

        this.isTripped = false;
        this.tripTime = null;
        this.tripReason = null;
    }

    /**
     * 检查熔断状态
     * @param {Object} portfolio 组合数据
     * @returns {boolean} 是否触发熔断
     */
    async checkCircuitBreaker(portfolio) {
        // 如果已经熔断，持续检查是否恢复
        if (this.isTripped) {
            const shouldReset = await this.shouldResetBreaker();
            if (shouldReset) {
                await this.resetBreaker();
            }
            return true;
        }

        // 检查所有熔断条件
        const checks = {
            // 熔断1: 单日亏损
            dailyLoss: this.checkDailyLoss(portfolio),

            // 熔断2: 总回撤
            maxDrawdown: this.checkMaxDrawdown(portfolio),

            // 熔断3: 连续亏损
            consecutiveLosses: await this.checkConsecutiveLosses(portfolio),

            // 熔断4: 系统故障
            systemFailure: await this.checkSystemFailure(),

            // 熔断5: 人工触发
            manualOverride: await this.checkManualOverride()
        };

        // 判断是否触发
        for (const [trigger, isTriggered] of Object.entries(checks)) {
            if (isTriggered) {
                await this.tripBreaker(trigger, checks);
                return true;
            }
        }

        return false;
    }

    /**
     * 检查单日亏损
     */
    checkDailyLoss(portfolio) {
        const dailyPnL = portfolio.dailyPnL || 0;
        return dailyPnL < this.thresholds.dailyLoss;
    }

    /**
     * 检查总回撤
     */
    checkMaxDrawdown(portfolio) {
        const maxDrawdown = portfolio.maxDrawdown || 0;
        return maxDrawdown < this.thresholds.maxDrawdown;
    }

    /**
     * 检查连续亏损
     */
    async checkConsecutiveLosses(portfolio) {
        // 获取最近交易记录
        const res = await db.collection('trade_history')
            .orderBy('tradeDate', 'desc')
            .limit(5)
            .get();

        let consecutiveCount = 0;

        for (const trade of res.data) {
            if (trade.return < 0) {
                consecutiveCount++;
            } else {
                break;
            }
        }

        return consecutiveCount >= this.thresholds.consecutiveLosses;
    }

    /**
     * 检查系统故障
     */
    async checkSystemFailure() {
        const res = await db.collection('system_log')
            .where({
                type: 'API_FAILURE',
                timestamp: db.command.gte(Date.now() - 3600000)  // 最近1小时
            })
            .get();

        return res.data.length >= this.thresholds.systemFailure;
    }

    /**
     * 检查人工触发
     */
    async checkManualOverride() {
        const res = await db.collection('circuit_breaker_status')
            .doc('manual')
            .get();

        return res.data && res.data.tripped === true;
    }

    /**
     * 触发熔断
     */
    async tripBreaker(reason, details) {
        this.isTripped = true;
        this.tripTime = Date.now();
        this.tripReason = reason;

        // 保存到数据库
        await db.collection('circuit_breaker_status').doc('current').set({
            tripped: true,
            reason: reason,
            details: details,
            tripTime: this.tripTime
        });

        // 发送紧急通知
        await this.sendEmergencyAlert(reason, details);

        // 如果有持仓，考虑强制平仓
        if (['DAILY_LOSS', 'MAX_DRAWDOWN', 'MANUAL_OVERRIDE'].includes(reason)) {
            await this.emergencyCloseAllPositions();
        }

        console.error('熔断触发:', reason, details);
    }

    /**
     * 发送紧急通知
     */
    async sendEmergencyAlert(reason, details) {
        const messages = {
            'DAILY_LOSS': '🚨 紧急熔断触发：单日亏损超过-5%',
            'MAX_DRAWDOWN': '🚨 紧急熔断触发：总回撤超过-15%',
            'CONSECUTIVE_LOSSES': '⚠️ 熔断触发：连续3笔亏损',
            'SYSTEM_FAILURE': '⚠️ 熔断触发：系统API异常',
            'MANUAL_OVERRIDE': '🚨 熔断触发：人工紧急停止'
        };

        await cloud.callFunction({
            name: 'sendNotification',
            data: {
                title: messages[reason] || '熔断触发',
                content: `原因: ${reason}\n详情: ${JSON.stringify(details, null, 2)}`,
                level: 'EMERGENCY',
                actions: [
                    { text: '🔄 恢复交易', action: 'resume' },
                    { text: '📊 查看详情', action: 'view' }
                ]
            }
        });
    }

    /**
     * 紧急平仓（可选）
     */
    async emergencyCloseAllPositions() {
        const holdingsRes = await db.collection('holdings')
            .where({
                quantity: db.command.gt(0)
            })
            .get();

        for (const holding of holdingsRes.data) {
            // 发送市价卖单
            await this.placeEmergencyOrder(holding, 'SELL');
        }
    }

    /**
     * 检查是否应该恢复熔断
     */
    async shouldResetBreaker() {
        // 熔断后至少等待1小时
        const timeSinceTrip = Date.now() - this.tripTime;
        if (timeSinceTrip < 3600000) {
            return false;
        }

        // 检查触发条件是否改善
        if (this.tripReason === 'MANUAL_OVERRIDE') {
            // 人工触发的需要人工恢复
            return false;
        }

        // 其他条件可以自动恢复
        return true;
    }

    /**
     * 重置熔断
     */
    async resetBreaker() {
        this.isTripped = false;
        this.tripTime = null;
        this.tripReason = null;

        await db.collection('circuit_breaker_status').doc('current').set({
            tripped: false,
            resetTime: Date.now()
        });

        await cloud.callFunction({
            name: 'sendNotification',
            data: {
                title: '✅ 熔断已解除',
                content: '交易已恢复正常',
                level: 'INFO'
            }
        });

        console.log('熔断已重置');
    }
}

module.exports = CircuitBreakerSystem;
```

---

## 4. 微信通知交互

### 4.1 订阅消息模板

```javascript
// cloudfunctions/sendNotification/index.js

const cloud = require('wx-server-sdk');
cloud.init();

class NotificationService {
    /**
     * 发送交易建议通知
     */
    async sendTradeSuggestion(notification) {
        const { touser, page, data } = this.buildTradeTemplate(notification);

        try {
            const result = await cloud.openapi.subscribeMessage.send({
                touser: touser,
                page: page,
                data: data,
                templateId: 'YOUR_TEMPLATE_ID',  // 微信订阅消息模板ID
                miniprogramState: 'formal'  // 正式版
            });

            console.log('通知发送成功:', result);

            return {
                success: true,
                notificationId: result.msgID
            };

        } catch (e) {
            console.error('通知发送失败:', e);
            return {
                success: false,
                error: e.message
            };
        }
    }

    /**
     * 构建模板数据
     */
    buildTradeTemplate(notification) {
        return {
            touser: notification.openid,
            page: 'pages/trade/detail?id=' + notification.tradeId,

            data: {
                // 根据微信模板要求填写
                thing1: {  // 股票名称
                    value: notification.stockName
                },
                amount2: {  // 交易金额
                    value: '¥' + notification.amount.toLocaleString()
                },
                thing3: {  // 操作类型
                    value: notification.action === 'BUY' ? '买入建议' : '卖出建议'
                },
                thing4: {  // 理由
                    value: notification.reason.substring(0, 20)  // 限制20字符
                },
                date5: {  // 超时时间
                    value: new Date(notification.timeout).toISOString()
                }
            }
        };
    }

    /**
     * 发送熔断警报
     */
    async sendCircuitBreakerAlert(reason, details) {
        const templates = {
            'DAILY_LOSS': {
                title: '🚨 紧急熔断',
                content: '单日亏损超过-5%，已暂停所有交易',
                level: 'EMERGENCY'
            },
            'MAX_DRAWDOWN': {
                title: '🚨 紧急熔断',
                content: '总回撤超过-15%，已暂停所有交易',
                level: 'EMERGENCY'
            }
        };

        const template = templates[reason] || {
            title: '⚠️ 熔断触发',
            content: reason,
            level: 'HIGH'
        };

        await this.sendTradeSuggestion({
            type: 'CIRCUIT_BREAKER',
            ...template,
            details: details
        });
    }
}

module.exports = NotificationService;
```

---

## 5. 操作日志与审计

### 5.1 完整日志系统

```javascript
// utils/auditLogger.js

class AuditLogger {
    /**
     * 记录所有自动操作
     */
    async logAutoOperation(operation) {
        const logEntry = {
            timestamp: Date.now(),
            operator: 'SYSTEM',
            operation: operation.type,
            details: operation.details,

            // 决策依据
            decision: {
                level: operation.level,
                riskScore: operation.riskScore,
                aiConfidence: operation.aiConfidence,
                factors: operation.factors
            },

            // 执行结果
            result: operation.result,

            // 审计信息
            ip: 'SYSTEM',
            userAgent: 'StockQuant-AutoEngine-v3.0'
        };

        await db.collection('audit_log').add({
            data: logEntry
        });
    }

    /**
     * 查询审计日志
     */
    async queryAuditLogs(filters) {
        const query = {};

        if (filters.startDate) {
            query.timestamp = db.command.gte(new Date(filters.startDate).getTime());
        }

        if (filters.endDate) {
            query.timestamp = query.timestamp || {};
            query.timestamp = db.command.and(
                query.timestamp,
                db.command.lte(new Date(filters.endDate).getTime())
            );
        }

        if (filters.operation) {
            query.operation = filters.operation;
        }

        const res = await db.collection('audit_log')
            .where(query)
            .orderBy('timestamp', 'desc')
            .limit(filters.limit || 100)
            .get();

        return res.data;
    }

    /**
     * 生成审计报告
     */
    async generateAuditReport(startDate, endDate) {
        const logs = await this.queryAuditLogs({
            startDate,
            endDate
        });

        const report = {
            summary: {
                totalOperations: logs.length,
                autoOperations: logs.filter(l => l.operator === 'SYSTEM').length,
                manualOperations: logs.filter(l => l.operator !== 'SYSTEM').length,
                successRate: logs.filter(l => l.result?.success === true).length / logs.length
            },

            byLevel: {
                AUTO: logs.filter(l => l.decision?.level === 'AUTO').length,
                SEMI: logs.filter(l => l.decision?.level === 'SEMI').length,
                MANUAL: logs.filter(l => l.decision?.level === 'MANUAL').length
            },

            byOperation: this.groupBy(logs, 'operation'),

            topFactors: this.analyzeTopFactors(logs),

            riskDistribution: this.analyzeRisks(logs)
        };

        return report;
    }

    /**
     * 辅助方法：分组统计
     */
    groupBy(logs, key) {
        const groups = {};

        for (const log of logs) {
            const value = log[key];
            groups[value] = (groups[value] || 0) + 1;
        }

        return groups;
    }

    /**
     * 分析关键决策因素
     */
    analyzeTopFactors(logs) {
        const factorCounts = {};

        for (const log of logs) {
            if (log.decision?.factors) {
                for (const [factor, value] of Object.entries(log.decision.factors)) {
                    factorCounts[factor] = (factorCounts[factor] || 0) + 1;
                }
            }
        }

        return Object.entries(factorCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);
    }

    /**
     * 分析风险分布
     */
    analyzeRisks(logs) {
        const risks = logs.map(l => l.decision?.riskScore || 0);

        return {
            min: Math.min(...risks),
            max: Math.max(...risks),
            avg: risks.reduce((a, b) => a + b, 0) / risks.length,
            distribution: {
                low: risks.filter(r => r === 0).length,
                medium: risks.filter(r => r > 0 && r <= 2).length,
                high: risks.filter(r => r > 2).length
            }
        };
    }
}

module.exports = AuditLogger;
```

---

## 完整工作流程

```
1. 信号生成 (Scanner/AI)
   ↓
2. 风险评估 (5维度)
   ↓
3. 等级判定 (AUTO/SEMI/MANUAL)
   ↓
4. 熔断检查 (5重防护)
   ↓
5. 执行决策
   ├─ AUTO: 直接执行
   ├─ SEMI: 发送通知 → 等待确认
   └─ MANUAL: 仅通知
   ↓
6. 记录日志 (审计追踪)
   ↓
7. 发送通知 (微信推送)
```

---

## 预期效果

| 指标 | 优化前 | 优化后 | 提升 |
|-----|--------|--------|------|
| **自动化程度** | 60% | 95% | +58% |
| **人为错误** | 15% | 2% | -87% |
| **响应速度** | 5-10分钟 | <10秒 | +98% |
| **风险控制** | 被动 | 主动 | - |

---

**注意**: 完全自动化需要充分测试，建议先在模拟环境运行至少1个月。
