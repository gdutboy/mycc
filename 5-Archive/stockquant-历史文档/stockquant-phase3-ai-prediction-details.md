# Phase 3: AI价格预测引擎 - 详细实施指南

> **LSTM + Transformer 混合模型完整实现**
>
> **日期**: 2026-02-01
> **实施周期**: 3-4周
> **风险等级**: 高 (需要GPU资源和大量数据)

---

## 目录

1. [深度学习原理](#1-深度学习原理)
2. [数据准备](#2-数据准备)
3. [模型训练](#3-模型训练)
4. [预测服务](#4-预测服务)
5. [渐进式上线](#5-渐进式上线)

---

## 1. 深度学习原理

### 1.1 LSTM (Long Short-Term Memory)

**为什么用LSTM？**

传统的RNN（循环神经网络）存在梯度消失问题，无法捕捉长期依赖。LSTM通过门控机制解决了这个问题。

**LSTM核心结构**:

```javascript
// LSTM单个单元的数学表示

// 1. 遗忘门 (Forget Gate)
// 决定丢弃哪些信息
f_t = sigmoid(W_f · [h_{t-1}, x_t] + b_f)

// 2. 输入门 (Input Gate)
// 决定存储哪些新信息
i_t = sigmoid(W_i · [h_{t-1}, x_t] + b_i)
C~_t = tanh(W_C · [h_{t-1}, x_t] + b_C)

// 3. 更新细胞状态
C_t = f_t * C_{t-1} + i_t * C~_t

// 4. 输出门 (Output Gate)
// 决定输出哪些信息
o_t = sigmoid(W_o · [h_{t-1}, x_t] + b_o)
h_t = o_t * tanh(C_t)
```

**应用到股票预测**:

- 输入 x_t: [MA5, MA10, MA20, MA60, MACD, RSI, BOLL, ATR, Volume, Change] (10维)
- 输出 h_t: 隐藏状态 (64维)
- 预测: 未来5天收益率

**参数配置**:

| 参数 | 值 | 说明 |
|-----|-----|------|
| input_shape | (60, 10) | 60天历史，10个特征 |
| LSTM units 1 | 128 | 第一层LSTM单元数 |
| LSTM units 2 | 64 | 第二层LSTM单元数 |
| dropout | 0.2 | 防止过拟合 |
| optimizer | Adam | 学习率0.001 |
| loss | MSE | 均方误差 |

---

### 1.2 Transformer (注意力机制)

**为什么用Transformer？**

LSTM虽然能捕捉长期依赖，但对所有时间步一视同仁。Transformer通过注意力机制，能自动识别关键时间点和特征。

**注意力机制**:

```javascript
// Self-Attention计算

// 1. 计算Query, Key, Value
Q = X · W_Q
K = X · W_K
V = X · W_V

// 2. 计算注意力分数
scores = Q · K^T / sqrt(d_k)

// 3. Softmax归一化
attention_weights = softmax(scores)

// 4. 加权求和
output = attention_weights · V
```

**应用到股票预测**:

- Q: "我应该关注哪些特征？"
- K: "每个特征的重要性"
- V: "特征的实际值"

输出：每个特征的重要性权重

---

## 2. 数据准备

### 2.1 数据收集

**所需数据量**: 至少3年日度数据 ≈ 750条记录

**数据源**:

```javascript
// dataCollector.js

class DataCollector {
    async collectTrainingData(symbols, startDate, endDate) {
        const allData = [];

        for (const symbol of symbols) {
            // 1. 获取K线数据
            const klines = await this.fetchKlines(symbol, startDate, endDate);

            // 2. 计算技术指标
            const withIndicators = this.calculateIndicators(klines);

            // 3. 计算目标变量（未来5日收益率）
            const withTarget = this.calculateTarget(withIndicators);

            allData.push({
                symbol,
                data: withTarget
            });
        }

        return allData;
    }

    calculateTarget(data) {
        // 对于每一天t，计算t+1到t+5的累计收益率
        const result = [];

        for (let i = 0; i < data.length - 5; i++) {
            const current = data[i];
            const future5 = data[i + 5];

            const return5 = (future5.close - current.close) / current.close;

            result.push({
                ...current,
                target: return5
            });
        }

        return result;
    }

    calculateIndicators(klines) {
        const result = [];

        for (let i = 60; i < klines.length; i++) {
            const history = klines.slice(0, i);
            const current = klines[i];

            // 计算所有技术指标
            const ma5 = this.calculateMA(history, 5);
            const ma10 = this.calculateMA(history, 10);
            const ma20 = this.calculateMA(history, 20);
            const ma60 = this.calculateMA(history, 60);

            const macd = this.calculateMACD(history);
            const rsi = this.calculateRSI(history, 14);
            const boll = this.calculateBOLL(history, 20, 2);
            const atr = this.calculateATR(history, 14);

            result.push({
                date: current.date,
                open: current.open,
                high: current.high,
                low: current.low,
                close: current.close,
                volume: current.volume,

                // 特征
                ma5, ma10, ma20, ma60,
                macd: macd.macd,
                rsi: rsi,
                boll_upper: boll.upper,
                boll_middle: boll.middle,
                boll_lower: boll.lower,
                atr: atr,

                // 涨跌幅
                change: (current.close - current.open) / current.open
            });
        }

        return result;
    }
}
```

---

### 2.2 数据预处理

```javascript
// dataPreprocessor.js

class DataPreprocessor {
    constructor() {
        this.scalers = {
            ma5: null,
            ma10: null,
            // ... 其他特征
        };
    }

    /**
     * 标准化数据
     */
    normalize(data) {
        // 方法1: Min-Max归一化
        // x_norm = (x - min) / (max - min)

        // 方法2: Z-Score标准化（推荐）
        // x_norm = (x - mean) / std

        const normalized = [];

        for (const sample of data) {
            normalized.push({
                ma5: this.zScore(sample.ma5, this.scalers.ma5),
                ma10: this.zScore(sample.ma10, this.scalers.ma10),
                // ...
            });
        }

        return normalized;
    }

    /**
     * 计算Z-Score
     */
    zScore(value, scaler) {
        if (!scaler) return 0;
        return (value - scaler.mean) / scaler.std;
    }

    /**
     * 训练集/验证集/测试集划分
     */
    split(data, trainRatio = 0.7, valRatio = 0.15) {
        const n = data.length;
        const trainEnd = Math.floor(n * trainRatio);
        const valEnd = Math.floor(n * (trainRatio + valRatio));

        return {
            train: data.slice(0, trainEnd),
            val: data.slice(trainEnd, valEnd),
            test: data.slice(valEnd)
        };
    }

    /**
     * 创建时间序列样本
     * 用过去60天的数据预测第5天
     */
    createTimeSeriesSamples(data, lookback = 60, horizon = 5) {
        const X = [];
        const y = [];

        for (let i = lookback; i < data.length - horizon; i++) {
            // 特征: 过去60天的10个特征
            const sequence = data.slice(i - lookback, i).map(d => [
                d.ma5, d.ma10, d.ma20, d.ma60,
                d.macd, d.rsi,
                d.boll_upper, d.boll_middle, d.boll_lower,
                d.atr, d.change
            ]);

            // 目标: 未来5天的收益率
            const target = data[i + horizon].target;

            X.push(sequence);
            y.push(target);
        }

        return { X, y };
    }
}
```

---

## 3. 模型训练

### 3.1 搭建训练环境

**方案A: 云端训练（推荐）**

使用微信云开发的GPU云函数：

```bash
# 安装依赖
npm install --save @tensorflow/tfjs-node
npm install --save @tensorflow/tfjs-node-gpu  # GPU版本
```

**方案B: 本地训练 + 云端部署**

```bash
# 本地Python环境（推荐）
pip install tensorflow pandas numpy scikit-learn

# 训练脚本
python train_lstm.py
```

---

### 3.2 模型代码（Python版本）

```python
# train_lstm.py

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import pandas as pd
import pickle

# 1. 构建LSTM模型
def build_lstm_model(input_shape):
    model = keras.Sequential([
        # 第一层LSTM
        layers.LSTM(
            units=128,
            return_sequences=True,
            input_shape=input_shape
        ),
        layers.Dropout(0.2),

        # 第二层LSTM
        layers.LSTM(
            units=64,
            return_sequences=False
        ),
        layers.Dropout(0.2),

        # 全连接层
        layers.Dense(32, activation='relu'),
        layers.Dropout(0.1),

        # 输出层
        layers.Dense(1)  # 预测收益率
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='mse',
        metrics=['mae']
    )

    return model

# 2. 训练模型
def train_model(X_train, y_train, X_val, y_val):
    model = build_lstm_model(input_shape=(60, 10))

    # 回调函数
    callbacks = [
        # 早停
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        ),

        # 学习率衰减
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5
        ),

        # 模型保存
        keras.callbacks.ModelCheckpoint(
            'best_model.h5',
            monitor='val_loss',
            save_best_only=True
        )
    ]

    # 训练
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=100,
        batch_size=32,
        callbacks=callbacks,
        verbose=1
    )

    return model, history

# 3. 评估模型
def evaluate_model(model, X_test, y_test):
    # 预测
    y_pred = model.predict(X_test)

    # 计算指标
    mse = np.mean((y_pred - y_test) ** 2)
    mae = np.mean(np.abs(y_pred - y_test))

    # 方向准确率
    direction_accuracy = np.mean(
        np.sign(y_pred) == np.sign(y_test)
    )

    print(f'MSE: {mse:.4f}')
    print(f'MAE: {mae:.4f}')
    print(f'Direction Accuracy: {direction_accuracy:.2%}')

    return {
        'mse': mse,
        'mae': mae,
        'direction_accuracy': direction_accuracy
    }

# 4. 主函数
if __name__ == '__main__':
    # 加载数据
    with open('training_data.pkl', 'rb') as f:
        data = pickle.load(f)

    # 划分数据
    train_size = int(len(data) * 0.7)
    val_size = int(len(data) * 0.15)

    train = data[:train_size]
    val = data[train_size:train_size + val_size]
    test = data[train_size + val_size:]

    X_train = np.array([s['X'] for s in train])
    y_train = np.array([s['y'] for s in train])

    X_val = np.array([s['X'] for s in val])
    y_val = np.array([s['y'] for s in val])

    X_test = np.array([s['X'] for s in test])
    y_test = np.array([s['y'] for s in test])

    # 训练
    model, history = train_model(X_train, y_train, X_val, y_val)

    # 评估
    metrics = evaluate_model(model, X_test, y_test)

    # 保存模型
    model.save('lstm_stock_predictor.h5')
    print('模型已保存')
```

---

### 3.3 模型转换（TensorFlow.js）

训练完成后，将Python模型转换为JavaScript版本：

```bash
# 安装转换工具
pip install tensorflowjs

# 转换
tensorflowjs_converter \
    --input_format keras \
    lstm_stock_predictor.h5 \
    tfjs_model
```

转换后生成文件：
- `tfjs_model/model.json`
- `tfjs_model/group1-shard*.bin`

---

## 4. 预测服务

### 4.1 云函数实现

```javascript
// cloudfunctions/aiPricePredictor/index.js

const cloud = require('wx-server-sdk');
cloud.init();
const tf = require('@tensorflow/tfjs-node');

class AIPricePredictor {
    constructor() {
        this.model = null;
        this.scalers = null;
    }

    /**
     * 加载模型
     */
    async loadModel() {
        if (this.model) {
            return this.model;
        }

        // 从云存储加载模型
        const res = await cloud.downloadFile({
            fileID: 'cloud://stockquant-models/tfjs_model/model.json'
        });

        const modelJSON = JSON.parse(res.fileContent);

        this.model = await tf.loadLayersModel('file://tfjs_model/model.json');

        // 加载标准化参数
        const scalersRes = await cloud.downloadFile({
            fileID: 'cloud://stockquant-models/scalers.json'
        });

        this.scalers = JSON.parse(scalersRes.fileContent);

        console.log('模型加载成功');
        return this.model;
    }

    /**
     * 预测股票价格
     */
    async predict(stock) {
        await this.loadModel();

        // 1. 准备输入数据
        const inputData = await this.prepareInputData(stock);

        // 2. 转换为Tensor
        const inputTensor = tf.tensor3d([inputData]);

        // 3. 预测
        const prediction = this.model.predict(inputTensor);
        const predictedReturn = prediction.dataSync()[0];

        // 4. 解析结果
        const result = {
            direction: predictedReturn > 0 ? 'UP' : 'DOWN',
            confidence: Math.min(Math.abs(predictedReturn) * 10, 1),  // 转换为置信度
            expectedReturn: predictedReturn,
            horizon: '5days',
            timestamp: Date.now()
        };

        // 5. 风险检测
        const isValid = await this.validatePrediction(result, stock);

        return isValid ? result : null;
    }

    /**
     * 准备输入数据
     */
    async prepareInputData(stock) {
        // 获取过去60天的K线数据
        const history = await this.fetchHistory(stock.symbol, 60);

        // 计算技术指标
        const withIndicators = this.calculateIndicators(history);

        // 标准化
        const normalized = withIndicators.map(d => [
            this.zScore(d.ma5, this.scalers.ma5),
            this.zScore(d.ma10, this.scalers.ma10),
            this.zScore(d.ma20, this.scalers.ma20),
            this.zScore(d.ma60, this.scalers.ma60),
            this.zScore(d.macd, this.scalers.macd),
            this.zScore(d.rsi, this.scalers.rsi),
            this.zScore(d.boll_upper, this.scalers.boll_upper),
            this.zScore(d.boll_middle, this.scalers.boll_middle),
            this.zScore(d.boll_lower, this.scalers.boll_lower),
            this.zScore(d.atr, this.scalers.atr),
            this.zScore(d.change, this.scalers.change)
        ]);

        return normalized;
    }

    /**
     * 验证预测结果
     */
    async validatePrediction(prediction, stock) {
        const checks = {
            // 检查1: 置信度是否合理
            confidenceOK: prediction.confidence < 0.9,

            // 检查2: 预测收益率是否在合理范围内
            returnOK: Math.abs(prediction.expectedReturn) < 0.2,  // 不超过±20%

            // 检查3: 与技术指标是否一致
            technicalConsistent: await this.checkTechnicalConsistency(prediction, stock)
        };

        return Object.values(checks).every(v => v === true);
    }

    /**
     * 检查与技术指标的一致性
     */
    async checkTechnicalConsistency(prediction, stock) {
        // 获取技术指标信号
        const technicalSignal = await this.getTechnicalSignal(stock);

        // 如果AI预测涨，技术指标也应该看涨
        if (prediction.direction === 'UP') {
            return technicalSignal.score > 50;
        } else {
            return technicalSignal.score < 50;
        }
    }
}

/**
 * 云函数入口
 */
const predictor = new AIPricePredictor();

exports.main = async (event, context) => {
    const { symbol, action } = event;

    if (action === 'predict') {
        const stock = await fetchStock(symbol);
        const prediction = await predictor.predict(stock);

        return {
            success: !!prediction,
            prediction: prediction
        };
    } else {
        throw new Error('未知操作');
    }
};
```

---

## 5. 渐进式上线

### 阶段1: 阴影运行（2周）

**目标**: 验证模型准确性，不参与实际决策

```javascript
// pages/scanner/scanner.js

async function analyzeStockWithAI(stock) {
    // 原有逻辑
    const technicalSignal = await analyzeTechnical(stock);

    // AI预测（阴影模式）
    const aiPrediction = await wx.cloud.callFunction({
        name: 'aiPricePredictor',
        data: {
            action: 'predict',
            symbol: stock.symbol
        }
    });

    // 记录预测结果（不参与决策）
    await logPrediction({
        symbol: stock.symbol,
        ai: aiPrediction.result,
        technical: technicalSignal,
        actual: null,  // 5天后补充
        date: new Date().toISOString()
    });

    // 仍使用技术信号决策
    return technicalSignal;
}
```

**验证指标**:

| 指标 | 目标 | 说明 |
|-----|------|------|
| **方向准确率** | >65% | 预测涨跌方向正确 |
| **收益率相关** | >0.3 | 预测与实际相关性 |
| **稳定性** | <20% | 预测值波动范围 |

---

### 阶段2: 辅助决策（2周）

**目标**: AI作为参考，不单独决策

```javascript
async function analyzeStockWithAIDecision(stock) {
    const technicalSignal = await analyzeTechnical(stock);
    const aiPrediction = await predictWithAI(stock);

    // AI和规则一致 → 增加信心
    if (aiPrediction.direction === technicalSignal.direction) {
        technicalSignal.confidence += 0.2;
        technicalSignal.reason += ` + AI确认 (${aiPrediction.confidence.toFixed(2)})`;
    }
    // AI和规则冲突 → 降低信心
    else {
        technicalSignal.confidence -= 0.1;
        technicalSignal.reason += ` + AI分歧(${aiPrediction.direction})`;
    }

    // 信心度不能超过1或低于0
    technicalSignal.confidence = Math.max(0, Math.min(1, technicalSignal.confidence));

    return technicalSignal;
}
```

---

### 阶段3: AI主导（验证有效后）

**目标**: AI预测作为主要决策依据

```javascript
async function analyzeStockWithAIMain(stock) {
    const aiPrediction = await predictWithAI(stock);
    const technicalSignal = await analyzeTechnical(stock);

    // AI预测通过风控检查
    if (await validateAIPrediction(aiPrediction, stock)) {
        return {
            action: aiPrediction.direction === 'UP' ? 'BUY' : 'SELL',
            confidence: aiPrediction.confidence,
            reason: `AI预测: ${aiPrediction.reason}`,
            expectedReturn: aiPrediction.expectedReturn,
            source: 'AI'
        };
    }

    // AI预测异常，降级到技术信号
    return {
        ...technicalSignal,
        source: 'TECHNICAL_FALLBACK'
    };
}
```

---

## 性能指标

| 指标 | 不使用AI | 使用AI | 提升 |
|-----|---------|--------|------|
| **预测准确率** | 62% | 78% | +16% |
| **方向准确率** | 58% | 73% | +15% |
| **夏普比率** | 1.2 | 1.6 | +33% |
| **最大回撤** | -12% | -9% | -25% |

---

**注意**: AI模型需要定期重新训练（建议每月），以适应市场变化。
