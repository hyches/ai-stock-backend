# Trading System

A modern web-based trading system built with Python (FastAPI) and React (TypeScript).

## Features

- Real-time trading signals and execution
- Portfolio management and tracking
- Multiple trading strategies support
- Backtesting capabilities
- Performance analytics and reporting
- User authentication and authorization
- Automated Machine Learning (AutoML)
- Anomaly detection and explainability
- Regime detection and event impact analysis
- Market data integration (including Zerodha)
- Modern, responsive UI

## Tech Stack

### Backend
- Python 3.8+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pandas
- NumPy
- TA-Lib
- Alembic (migrations)

### Frontend
- React 18
- TypeScript
- shadcn/ui
- tailwindcss
- Recharts
- Axios

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- PostgreSQL
- TA-Lib

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/trading-system.git
cd trading-system
```

2. Set up the backend:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload
```

3. Set up the frontend:
```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

4. Access the application:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3001
- API Documentation: http://localhost:8000/docs

## Project Structure

```
trading-system/
├── app/
│   ├── api/
│   │   ├── endpoints/           # Main API endpoints (alert, anomaly_detection, automl, etc.)
│   │   ├── v1/
│   │   │   └── endpoints/       # v1 API endpoints (strategies, trading)
│   │   ├── ml/                  # ML-specific API logic
│   │   └── deps.py, api.py
│   ├── core/                    # Core modules (config, logging, security, etc.)
│   ├── db/                      # Database base, session, etc.
│   ├── models/                  # SQLAlchemy models (user, trading, alert, etc.)
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # Business logic (ml_service, trading, optimizer, etc.)
│   ├── strategies/              # Trading strategy implementations
│   ├── utils/                   # Utility modules (backtesting, data_loader, etc.)
│   ├── middleware/              # Middleware (error handler, etc.)
│   ├── config/                  # Environment-specific configs
│   ├── frontend/                # (Optional) Embedded frontend
│   ├── main.py                  # FastAPI entrypoint
│   └── database.py, config.py
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/          # React components (Dashboard, Portfolio, etc.)
│       │   └── charts/          # Chart components (EquityCurveChart, etc.)
│       ├── hooks/               # Custom React hooks (useMLPredictions, usePortfolio, etc.)
│       ├── types/, styles/, ...
│       └── App.tsx, index.tsx
├── tests/
│   ├── api/                     # API endpoint tests
│   ├── integration/             # Integration tests
│   ├── benchmarks/              # Performance/benchmark tests
│   ├── load/                    # Load tests
│   ├── core/, db/, security/    # Core, DB, and security tests
│   └── ...
├── alembic/                     # DB migrations
├── scripts/                     # Utility scripts
├── docs/                        # Documentation
├── requirements.txt
├── requirements-test.txt
├── Dockerfile
├── README.md
└── ...
```

## Backend Overview

- **API Endpoints:**
  - `app/api/endpoints/`: alert, anomaly_detection, automl, backup, event_impact, explainability, forecasting, live_data, market, ml, optimizer, regime_detection, research, screener, settings, zerodha, auth
  - `app/api/v1/endpoints/`: strategies, trading
- **Business Logic:**
  - `app/services/`: alert_service, anomaly_detection, automl, backtest, competitor, event_impact, explainability, forecasting, fundamental_analysis, instrument_service, live_data, market_data_service, ml_predictions, ml_service, optimizer, regime_detection, report_generator, risk_management, screener, sentiment_analysis, strategy, technical_analysis, token_refresh, trade_constraints, trading, zerodha_service, etc.
- **Strategies:**
  - `app/strategies/`: base, trend_following
- **Utilities:**
  - `app/utils/`: backtesting, data_fetcher, data_loader, pagination, portfolio_management, risk_management, technical_analysis
- **Core & Middleware:**
  - `app/core/`: config, logging, security, roles, cache, middleware, monitoring, backup
  - `app/middleware/`: error_handler
- **Models & Schemas:**
  - `app/models/`: user, trading, alert, zerodha, database, competitor, sentiment, report, portfolio, stock
  - `app/schemas/`: user, zerodha, settings, ml, token, strategy, trading, market

## Frontend Overview

- **Components:**
  - Dashboard, Portfolio, PortfolioOverview, BacktestResults, TradingDashboard, MarketOverview, Watchlist, NotificationsPanel, Settings, Navbar, Sidebar, Login, SignalList, StrategyList, TradeHistory, MLDashboard, charts/EquityCurveChart
- **Hooks:**
  - useMLPredictions, usePortfolio, useWatchlist, useTechnicalIndicators, useAuth, useNotifications, useWebSocket, useApi

## Testing

- **Backend:**
  - Unit tests: `tests/core/`, `tests/db/`, `tests/security/`, etc.
  - API tests: `tests/api/`
  - Integration tests: `tests/integration/`
  - Benchmark tests: `tests/benchmarks/`
  - Load tests: `tests/load/`
- **Frontend:**
  - Run with `npm test` in `frontend/`

### Running Tests

#### Backend
```bash
python run_tests.py
```

#### Frontend
```bash
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Material-UI](https://mui.com/)
- [Recharts](https://recharts.org/) 