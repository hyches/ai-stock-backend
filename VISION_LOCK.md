# VISION LOCK: AI-Powered Trading & Research Platform

## 1. SYSTEM VISION
The platform is an autonomous, high-fidelity financial ecosystem designed for the **Quantitative DIY Investor**. It transforms raw market data into institutional-grade actionable intelligence by unifying deep geometric pattern recognition, ensemble ML forecasting, and rigorous risk mathematics into a single, cohesive dashboard.

The platform solves the fragmented "Tooling Gap" for individuals by managing the entire investment lifecycle: from multi-provider data aggregation and AI-driven screening to event-driven backtesting and complex order execution. It is intended as a showcase of a full-stack, vertically integrated quantitative trading engine.

## 2. FEATURE UNIVERSE

### 🔐 Authentication & Identity
- JWT-based User Session Management
- Role-Based Access Control (RBAC) infrastructure
- CSRF Protection & Cookie handling

### 📊 Dashboard & Monitoring
- Unified Summary (Portfolio + Market + News)
- Multi-Index Market Weather Reporting
- High-Frequency Watchlist Synchronization
- Historical Performance Time-Series

### 🔬 Research & AI
- Technical Data Aggregation (50+ indicators)
- Automated Chart Pattern Detection (H&S, Triangles, etc.)
- Ensemble ML Model Training & Forecasting
- Individual Ticker Anomaly Detection (Z-Score)
- Market Sentiment NLP Analysis

### 🧪 Simulation & Analysis
- Event-Driven Historical Backtesting
- Monte Carlo Performance Simulation
- Portfolio Parametric VaR (Value at Risk)
- Correlation Matrix & Diversification Math
- Indian Market Tax Liability Computation (FIFO)

### ⚡ Execution & Trading
- Core Brokerage CRUD (Trades/Positions/Strategies)
- Advanced Execution (Bracket & Trailing Stop-Loss)
- Paper Trading Engine (In-memory simulation)
- Automated Grid Bot Trading
- Option Chain Analysis (US & Indian Markets)

## 3. FEATURE STAGING

| Feature Area | Stage | Rationale |
| :--- | :--- | :--- |
| **User Authentication** | CORE | Foundational security layer for persistent state. |
| **Core Trading CRUD** | CORE | Primary DB-linked ledger for positions and trades. |
| **Risk Metrics (VaR/Sharpe)** | CORE | Genuine mathematical differentiation from standard apps. |
| **Research Data Aggregation** | CORE | Base informational layer for user decision making. |
| **Backtesting Engine** | CORE | Critical verification tool for showcasing strategy logic. |
| **Dashboard Summary** | CORE | Central entry point and visual anchor of the platform. |
| **Tax Calculator (FIFO)** | ADVANCED | High-fidelity logic; provides deep localized value. |
| **Advanced Orders (Bracket)** | ADVANCED | Multi-leg logic requiring state-machine stability. |
| **Option Chain Analysis** | ADVANCED | Data-heavy specialized module for derivative traders. |
| **ML/AI Pattern Detection** | EXPERIMENTAL | Evolving geometric logic; highly visual but complex. |
| **ML Model Retraining** | EXPERIMENTAL | Resource-intensive background async operations. |
| **Grid Bot Trading** | EXPERIMENTAL | Autonomous execution logic in early evolutionary state. |
| **Feature Store Service** | INTERNAL | Middleware infrastructure for caching/performance. |
| **Order Executor Thread** | INTERNAL | Background execution orchestration layer. |

## 4. SYSTEM BOUNDARIES

### What the system WILL do:
- Provide a **Single Source of Truth** for real-time market data across all dashboard widgets.
- Execute **Complex Conditional Orders** (Bracket/Trailing) via a persistent state machine.
- Calculate **Institutional Risk Metrics** based on actual historical covariance of positions.
- Deliver **AI-Augmented Research** by blending technical indicators with geometric pattern extraction.

### What the system WILL NOT try to fully solve (yet):
- **Live Brokerage Fulfillment**: The system focuses on signal generation and paper-simulated execution; it will not manage live capital connectivity in the 3-month window without external provider (Zerodha) keys.
- **Real-Time Token Blacklisting**: Security will rely on JWT standard expiration rather than stateful revocation.
- **Historical Equity Curve Reconstruction**: The system will track performance from the moment of user onboarding, not reconstruct pre-onboarding trading history.
- **Reinforcement Learning from Actions**: User action recording remains a logging feature; automated model adjustment from clicks is out of initial scope.
