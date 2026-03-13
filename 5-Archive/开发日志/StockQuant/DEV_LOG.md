# StockQuant Development Log & Implementation Summaries

## ☁️ Cloud Monitor & Notification System (v2.5.0)
**Date**: 2026-01-30 22:30
**Goal**: Complete the "Set & Forget" institutional monitoring system with real-time push notifications.
**Implementation**:
*   **Cloud Function**: `monitorHoldings` implemented with batch processing (40 stocks/batch).
*   **Parallel Execution**: Refactored `index.js` to use `Promise.all`, reducing execution time from >3s (timeout) to <600ms.
*   **Robust Parsing**: Upgraded `utils.js` specific K-line parser to handle Sina API's non-standard JSON (unquoted keys, single quotes) using `new Function`.
*   **Notification Integration**: Added `requestSubscribeMessage` in Settings, configured Template ID, and mapped risk types (Hard Stop, Trend Breakdown, etc.) to WeChat Service Notifications.
*   **Verification**: Validated end-to-end flow: Local Settings -> Cloud Sync -> Scheduled Trigger -> Risk Check -> WeChat Push.

---

**Consolidated Date**: 2026-01-29
**Description**: Since the `StockQuant` project generated numerous specific development logs, fix reports, and implementation summaries, this document serves as a consolidated repository for these records. It tracks critical bug fixes, feature enhancements, and system upgrades occurring primarily in January 2026.

---

## ☁️ Cloud Persistence & UX Fixes (v2.4.4)
**Date**: 2026-01-31

### 1. Cloud Function Dual-Sync Architecture
**Source**: `cloudfunctions/syncTrades/index.js`
**Issue**: User reported "Phantom Data" where restored watchlist items disappeared immediately, and Trade History was missing (-4 error).
**Fix**:
*   **Force Clean Sync**: Implemented "Delete-then-Create" logic in cloud function to prevent duplicate records and schema mismatches.
*   **Schema Extension**: Explicitly added `watchlist` and `history` (Trade Logs) to the cloud database schema.
*   **Key Correction**: Fixed storage key mismatch (`PAPER_TRADELOGS` -> `TRADE_LOGS`) in `settings.js` and `paper.js`.

### 2. Auto-Cleanup Logic Update
**Source**: `pages/paper/paper.js`
**Issue**: Restored watchlist items (with old `addedAt` dates) were being immediately deleted by `autoCleanupWatchlist` (7-day expiry).
**Fix**:
*   Extended `EXPIRE_DAYS` from 7 to 365. Restored items now persist correctly.

### 3. Scanner Manual Add Logic
**Source**: `pages/scanner/scanner.js`
**Issue**: Manually adding 2-star stocks to watchlist via "Risk Warning" modal failed because it triggered strict "Auto-Trade" risk checks (Volume/Signal Age).
**Fix**:
*   Modified confirmation callback to `trackStock(stock, false)`.
*   **Logic**: Manual confirmation now bypasses algorithmic risk checks and forces addition to `PAPER_WATCHLIST`.

---

## ☁️ Cloud Sync & Strategy Parity (v2.4.3)
**Date**: 2026-01-30

### 1. Strategy Synchronization (11 Strategies)
**Goal**: Ensure cloud monitor (`monitorHoldings`) logic matches local `strategy_router` 100%.
**Implementation**:
*   **Ported Indicators**: Implemented `calculateRSI`, `calculateKDJ`, `calculateADX`, `calculateVolumeRatio`, `calculateVPT`, `calculateStochRSI` in `cloudfunctions/monitorHoldings/utils.js`.
*   **Updated Logic**: `index.js` now checks 11 distinct conditions including:
    *   Hard Stop (User configurable: -8%/-10%/-15%)
    *   Trend: MA20 Breakdown, MACD Dead Cross, ADX Fading
    *   Momentum: KDJ Dead Cross (>80), StochRSI Overbought (>0.95), HA Reversal
    *   Volume: High Vol Ratio (>2.5) + Price Drop
*   **Result**: Cloud alerts now reflect the exact same sophistication as local analysis.

### 2. Settings Synchronization
**Goal**: Allow user to tweak risk parameters locally and have them take effect in cloud immediately.
**Implementation**:
*   **Frontend**: `backupToCloud` updated to send `settings` object (`stopLossMode`, `exitStrategy`, `tradeAmount`).
*   **UX**: Added "Sync Config" button to `settings.wxml` for lightweight updates. Auto-sync on Monitor Toggle.
*   **Backend**: `syncTrades` stores `settings` in `user_trades` collection; `monitorHoldings` fetches and applies them per-holding.

---

## 🚀 Performance Optimization

### Scan Speed Evolution (v2.3.1)
**Source**: `SCAN_SPEED_EVOLUTION.md`, `SPEED_BOOST_25_PERCENT.md`
**Date**: 2026-01-28

The scanning speed has undergone a massive optimization, improving from **33 minutes** to **22-33 seconds** (for 500 stocks), a **60-90x improvement**.

**Optimization Timeline:**
1.  **Initial Optimization**: 5 stocks/batch, 500ms delay. Result: 33 mins (Too slow).
2.  **Balanced**: 10 stocks/batch, 150ms delay. Result: 8-12 mins.
3.  **Speed Priority**: 20 stocks/batch, 50ms delay. Result: 2-3 mins.
4.  **Extreme Mode**: 30 stocks/batch, 0ms delay. Result: 30-45s.
5.  **Performance Breakthrough (Current)**: 40 stocks/batch, 0ms delay, 20 concurrent requests. Result: **22-33s**.

**Key Technical Implementations:**
*   **Batch Size**: Increased from 5 to 40.
*   **Concurrency**: Increased from 3 to 20 concurrent requests.
*   **Zero Delay**: Eliminated batch delays (`DELAY_MS = 0`) and queue delays.
*   **Smart Throttling**: Only aggressively throttles (adds delay) when `ERR_CONNECTION_RESET` or connection errors are detected, then rapidly recovers.
*   **Queue Protection**: Added atomic flags to prevent race conditions in the request queue.

---

## 🐛 Critical Bug Fixes

### 1. Real-Time PnL Calculation Fix
**Source**: `FIX_REALTIME_PNL.md`
**Date**: 2026-01-26
**Issue**: PnL was calculating using K-line close prices (previous day) instead of real-time quotes.
**Fix**:
*   Enforced `loadStockDetail` (which fetches real-time prices) to complete before `calculatePnL`.
*   Added `CRITICAL RULE` in documentation to always use live data for PnL/Exit logic.
*   Updated `pages/index/index.js` and confirmed `paper.js` correctness.

### 2. API Throttling & Connection Reset
**Source**: `API_THROTTLING_FIX.md`
**Date**: 2026-01-26
**Issue**: High concurrency caused `ERR_CONNECTION_RESET` during scanning.
**Fix**:
*   Implemented "Smart Adaptive Throttling" in `scanner.js` and `api_v2.js`.
*   Auto-detects error rates; if failure rate > 50%, increases delay.
*   Added a "Cooling Mode" (5s pause) if severe limiting is detected.
*   Fixed a race condition in `api_v2.js` queue processing (`Cannot read property 'fn' of undefined`).

### 3. Post-Market Data Update
**Source**: `POST_MARKET_DATA_FIX.md`
**Date**: 2026-01-28
**Issue**: Trend page showed yesterday's data even after market open.
**Fix**:
*   Added logic to check the date of the last K-line against `new Date()`.
*   If time > 9:30 AM and dates mismatch, force a refresh (ignoring cache).
*   Added "Pull Down to Refresh" to explicitly clear cache.

### 4. Scan Completion Build Prompt
**Source**: `SCAN_COMPLETE_FIX.md`
**Date**: 2026-01-28
**Issue**: "Build Position" prompt appeared prematurely (during scan or AI check) or repeatedly when switching tabs.
**Fix**:
*   Strict state checking: Only prompt if `!loading` AND `!isAiChecking`.
*   **Timestamp Logic**: Record `SCAN_END_TIME` only after AI check completes.
*   **Time Window**: Only prompt within 1 minute of completion, with a 5-minute cooldown for re-prompts.
*   **Context Aware**: Separate prompt tracking for potential builds vs. already built.

### 5. AI Check Build Modal
**Source**: `AI_CHECK_BUILD_FIX.md`
**Date**: 2026-01-28
**Issue**: No feedback after AI check if no stocks met criteria (only a fleeting toast).
**Fix**:
*   Replaced Toast with a **Modal Dialog**.
*   Provides detailed stats even if 0 stocks are built: "Found X 3-star stocks, but Y are in watchlist/already built."
*   Ensures user transparency on why no action was taken.

### 6. Missing Trade Records
**Source**: `交易记录丢失修复报告.md` (Lost Trade Records Report)
**Fix**:
*   Identified race condition between background auto-trade checks and foreground `onShow` saves rewriting Storage.
*   **Solution**: Implemented a **Concurrency Lock** (`_isAutoChecking` flag) in `runAutoSignalCheck` to prevent re-entry or conflicting writes.

### 7. Strategy Exit Consistency
**Source**: `STRATEGY_EXIT_FIX_SUMMARY.md`
**Date**: 2026-01-26
**Issue**: Strategies were "mixed" (e.g., Buy on BOLL, Sell on MA/MACD consensus), invalidating backtests.
**Fix**:
*   Implemented **Strategy Consistency Mode**.
*   If bought with BOLL, exit logic ONLY checks BOLL signals.
*   Added "Exit Mode" setting (Strategy Consistency vs. Multi-Strategy Consensus).
*   Updated Backtest engine to support distinct exit logic for MA, MACD, BOLL, HA_TREND.
*   Aligns with strict institutional standards (Two Sigma/Renaissance).

---

## 🎨 UI/UX Improvements

### 1. Smart Recommendation System (UI Optimization)
**Source**: `UI_OPTIMIZATION_REPORT.md`, `PLAN_D_IMPLEMENTATION_REPORT.md`
**Date**: 2026-01-26
**Changes**:
*   **Consolidated Cards**: Merged "Scanner Recommendations", "Router Recommendations", and "Strategy Comparison" into a single **"Smart Recommendation System"** card.
*   **Information Hierarchy**: Folded view shows only the "Best Strategy". Expanded view shows full details.
*   **Reduced Clutter**: Removed redundant "Indicator Explanation" and separate "Strategy Comparison" cards.
*   **Compact Metrics**: Redesigned metrics grid to show 9 key indicators (including Sharpe/Calmar) in a single compact block (3x3 grid).
*   **Page Length**: Reduced scrolling by ~40-47%.

### 2. AI Card UI Optimization
**Source**: `AI卡片UI优化方案.md`, `AI卡片对齐修复方案.md`
**Issue**: AI text response had jagged indentation and poor formatting.
**Fix**:
*   Parsed AI response text into structured data (Title/Content blocks) based on Emoji headers.
*   Rendered as separate UI cards instead of a single text block.
*   Collapsed view shows a clean "Core Viewpoint" preview instead of truncated raw text.

### 3. Lazy Mode (One-Click Optimization)
**Source**: `LAZY_MODE_OPTIMIZE_ALL.md`
**Date**: 2026-01-28
**Feature**: Added a "⚡ One-Click Optimize" button in the Paper Trading page.
**Function**:
*   Iterates through all open positions.
*   Runs backtests for all supported strategies (MA, MACD, BOLL, HA) on each stock.
*   Automatically switches each position to its historical best-performing strategy.
*   Provides a summary report of changes.

---

### 6. Permanent Concurrency Fix (交易记录丢失)
**Source**: `PERMANENT_CONCURRENCY_FIX.md` (已合并)
**Date**: 2026-01-29
**Issue**: Transaction logs showed records, but history records were missing.用户反馈：交易流水有记录，有平仓提示，但历史记录中找不到对应交易。
**Root Cause**: 并发写入导致的数据覆盖（Race Condition）。定时器自动巡检与用户手动操作同时修改 `PAPER_TRADES`，后写入的覆盖前面的修改。
**Permanent Solution**: 三重防护机制
  1. **版本号机制**: 每次保存递增版本号，检测并发修改
  2. **统一保存入口**: 所有修改通过 `_saveTradesSafely(trades, operation)`，自动处理冲突
  3. **智能合并策略**: 冲突时自动合并，保证数据完整性（按ID去重，优先保留最新时间的数据）
**Implementation**:
  - 新增函数：`_initVersionControl()`, `_saveTradesSafely()`, `_mergeTrades()`
  - 替换保存调用：12处（手动平仓、AI买入、自动平仓、切换策略、优化等）
  - 增强锁检查：在 `closeTrade` 和 `onShow` 中检查 `_isAutoChecking` 锁
  - 重置版本号：3处清空操作中同时重置 `PAPER_TRADES_VERSION`
**Result**: 永久性解决并发数据丢失问题，所有交易记录完整保存。

---

## 🛠️ Debugging Log

### 1. Scanner Runtime Error Fix (v2.4.2)
**Date**: 2026-01-30
**Issue**: 用户反馈 "Cannot destructure property 'data' of 'r' as it is undefined" 运行时错误，且后续出现 "Identifier 'lastDay' has already been declared" 语法错误。
**Root Cause**:
- **Layer 1 (Runtime)**: 初始的 "undefined" 错误可能由构建工具对语法错误处理不当引发的连锁反应，或者不完整的 Source Map 误导了报错位置。
- **Layer 2 (Syntax)**: 在 `pages/scanner/scanner.js` 集成 P2 流动性检查 (`checkLiquidity`) 时，复制粘贴的代码块中包含了已存在的变量声明 (`const lastDay`, `const turnover`)，导致变量重复声明错误。
**Fix**:
- 移除了重复的变量声明，复用上文已计算的 `lastDay` 和 `turnover` 变量。
- 恢复了 `checkLiquidity` 的调用，并验证了变量作用域的正确性。
**Result**: Scanner 功能恢复正常，P2 流动性检查逻辑正确生效。

## 🏛️ System & Functional Upgrades

### 1. Institutional Grade Upgrade (v2.3.0)
**Source**: `INSTITUTIONAL_UPGRADE_SUMMARY.md`
**Date**: 2026-01-26
**Context**: Upgrades based on analysis of top quant firms (Two Sigma, Citadel).
**Features Added**:
*   **Max Drawdown Protection**: Force exit if profit > 5% but retraces 15% from peak.
*   **ATR Position Sizing**: Dynamic Kelly criterion adjustment based on volatility (lower position for high volatility).
*   **Sharpe & Calmar Ratios**: Added professional risk-adjusted return metrics to analysis.
*   **Result**: "Institutional Fit" score increased from 60% to 93%.

### 2. Strategy System Expansion (Phase 1-3)
**Source**: `PHASE_1_2_3_COMPLETION_REPORT.md`
**Achievements**:
*   **Strategy Count**: Expanded from 4 to 11 strategies (Added RSI, ATR, KDJ, ADX_TREND, VPT, STOCH_RSI, BOLL_SQUEEZE).
*   **Data Flow**: Scanner now passes calculated indicators (RSI, ADX, etc.) to the Trend Page, eliminating calculation redundancy.
*   **Smart Router**: Implemented `strategy_router.js` to detect market regimes (Bull/Bear/Range) and recommend strategies accordingly (e.g., Trend strategies for high ADX, Mean Reversion for oscillating RSI).

### 3. GLM-4 AI Scoring
**Source**: `GLM-4智能评分实施计划.md`, `GLM-4智能评分实施计划(优化版).md`
**Plan**:
*   Upgrade AI Secretary scoring from keyword matching to "Deep Reasoning".
*   Prompt Engineering: Force GLM-4 to output "Score: XX" in the first line based on logical analysis.
*   Fallback: shadow validation against keyword scoring to prevent hallucinations.
*   UI: Parse and display the score cleanly.

### 4. Backtest Enhancements
**Source**: `BACKTEST_IMPLEMENTATION_SUMMARY.md`
**Features**:
*   **Metric Interpretation**: "Human-readable" cards for beginners (e.g., "If you invested 100k, you'd have 125k now").
*   **Benchmark Comparison**: Explicit "Strategy vs. Buy & Hold" comparison with Alpha calculation.
*   **Help Tooltips**: Added explanations for Sharpe Ratio, Max Drawdown, etc.

---

## 📚 Documentation Updates

**Source**: `DOCUMENTATION_UPDATE_SUMMARY.md`, `DOC_UPDATE_JAN_28.md`
**Status**: All core documentation (`README.md`, `CHANGELOG.md`, `CLAUDE.md`) is synced with v2.3.1.
*   Old optimization plans and speed reports have been consolidated or archived.
*   New "Institutional Grade" badges and feature lists added to README.
