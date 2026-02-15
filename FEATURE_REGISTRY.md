# FEATURE REGISTRY: System Alignment Map

This document maps the **Vision Lock** capabilities to the current **Forensic Reality** of the codebase. It serves as the authoritative guide for what is actually functional today.

| Feature Name | Feature Area | Stage | Backend Reality | Persistence | Security | Frontend Status | Truth Statement |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Session Management** | Auth | CORE | IMPLEMENTED & FUNCTIONAL | PERSISTED | AUTH ENFORCED | WIRED & USABLE | Users can register, login, and maintain sessions via JWT. |
| **RBAC Infrastructure** | Auth | CORE | IMPLEMENTED BUT PARTIAL | PERSISTED | AUTH ENFORCED | NOT WIRED | Multi-role fields exist in DB but logic is not yet enforced in routes. |
| **CSRF Protection** | Auth | CORE | IMPLEMENTED & FUNCTIONAL | NOT PERSISTED | AUTH MISSING | WIRED & USABLE | Uses double-submit cookie pattern for state-changing safety. |
| **Unified Summary** | Dashboard | CORE | IMPLEMENTED & FUNCTIONAL | PERSISTED | AUTH MISSING | WIRED & USABLE | Aggregates market and position data but lacks session protection. |
| **Market Weather** | Dashboard | CORE | IMPLEMENTED & FUNCTIONAL | NOT PERSISTED | AUTH MISSING | WIRED & USABLE | Real-time sentiment score based on index volatility and anomalies. |
| **Price Sync** | Dashboard | CORE | IMPLEMENTED & FUNCTIONAL | PERSISTED | AUTH MISSING | WIRED & USABLE | Single global WebSocket ensures cross-component price parity. |
| **History Time-Series** | Dashboard | CORE | IMPLEMENTED BUT STUBBED | NOT PERSISTED | AUTH MISSING | WIRED BUT MISLEADING | Displays a mock linear math decay, not actual account history. |
| **Technical Data** | Research | CORE | IMPLEMENTED & FUNCTIONAL | PERSISTED | AUTH MISSING | WIRED & USABLE | Fetches 50+ technical indicators from YFinance via internal cache. |
| **Pattern Detection** | Research | EXPERIMENTAL | IMPLEMENTED & FUNCTIONAL | NOT PERSISTED | AUTH MISSING | WIRED & USABLE | Extracts geometric shapes (H&S, Triangles) from OHLCV data. |
| **AI Forecasting** | Research | EXPERIMENTAL | IMPLEMENTED & FUNCTIONAL | PERSISTED | AUTH MISSING | WIRED & USABLE | Generates return predictions using a multi-model ensemble engine. |
| **Anomaly Detection** | Research | CORE | IMPLEMENTED & FUNCTIONAL | NOT PERSISTED | AUTH MISSING | WIRED & USABLE | Identifies price outliers using rolling Z-Score statistical analysis. |
| **NLP Sentiment** | Research | CORE | IMPLEMENTED BUT PARTIAL | NOT PERSISTED | AUTH MISSING | WIRED & USABLE | Scores news headlines via provider-specific sentiment services. |
| **Backtest Engine** | Simulation | CORE | IMPLEMENTED & FUNCTIONAL | NOT PERSISTED | AUTH MISSING | WIRED & USABLE | Simulates historical strategy performance in a thread-safe loop. |
| **Monte Carlo Sim** | Simulation | CORE | IMPLEMENTED & FUNCTIONAL | NOT PERSISTED | AUTH MISSING | WIRED & USABLE | Probabilistic path analysis (500+ sims) for strategy validation. |
| **Parametric VaR** | Simulation | CORE | IMPLEMENTED & FUNCTIONAL | PERSISTED | AUTH ENFORCED | WIRED & USABLE | Real Covariance-based Value-at-Risk using actual DB positions. |
| **Correlation Matrix** | Simulation | CORE | IMPLEMENTED & FUNCTIONAL | NOT PERSISTED | AUTH ENFORCED | WIRED & USABLE | Dynamic matrix calculation for portfolio diversification analysis. |
| **Indian Tax (FIFO)** | Simulation | ADVANCED | IMPLEMENTED & FUNCTIONAL | PERSISTED | AUTH ENFORCED | WIRED & USABLE | Reconstructs closed sequences from DB trade legs for STCG/LTCG. |
| **Brokerage CRUD** | Execution | CORE | IMPLEMENTED & FUNCTIONAL | PERSISTED | AUTH ENFORCED | WIRED & USABLE | Permanent DB ledger for positions, trades, and strategy meta. |
| **Advanced Orders** | Execution | ADVANCED | IMPLEMENTED BUT PARTIAL | IN-MEMORY | AUTH MISSING | WIRED & USABLE | Active Bracket/Trailing monitoring but wiped on server restart. |
| **Paper Trading** | Execution | CORE | IMPLEMENTED & FUNCTIONAL | IN-MEMORY | AUTH MISSING | WIRED & USABLE | Near-real-time simulated trading with distinct capital tracking. |
| **Grid Bot Trading** | Execution | EXPERIMENTAL | IMPLEMENTED & FUNCTIONAL | IN-MEMORY | AUTH MISSING | NOT WIRED | Functional range-trading bot logic without a UI controller. |
| **Option Chain** | Execution | ADVANCED | IMPLEMENTED BUT PARTIAL | NOT PERSISTED | AUTH MISSING | WIRED & USABLE | Full US chain data; returns static warning for Indian indices. |
| **Feature Store** | INTERNAL | INTERNAL | IMPLEMENTED & FUNCTIONAL | PERSISTED | INTERNAL ONLY | NOT WIRED | Core caching middleware reducing API latency and provider costs. |
| **Order Exec Thread** | INTERNAL | INTERNAL | IMPLEMENTED & FUNCTIONAL | IN-MEMORY | INTERNAL ONLY | NOT WIRED | Background orchestrator handling high-frequency order tick checks. |
