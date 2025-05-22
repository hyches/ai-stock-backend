
# AI Stock Portfolio Platform — Backend Architecture

## 📁 Folder & File Structure

```
/backend
│
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # Entry point (FastAPI app)
│   ├── config.py                 # Environment/config management
│   ├── models/                   # Pydantic models for data validation
│   │   └── stock.py
│   │   └── portfolio.py
│   ├── services/                 # Core logic (ML, Screener, Optimizer)
│   │   └── screener.py
│   │   └── optimizer.py
│   │   └── report_generator.py
│   ├── api/                      # API route handlers
│   │   └── endpoints/
│   │       └── screener.py
│   │       └── optimizer.py
│   │       └── research.py
│   └── utils/                    # Helper functions
│       └── data_loader.py
│       └── finance_metrics.py
│
├── tests/                        # Unit tests for all components
│   └── test_screener.py
│   └── test_optimizer.py
│
├── requirements.txt              # Python package dependencies
├── Dockerfile                    # Docker setup for deployment
├── .env                          # Environment variables (API keys, etc.)
└── README.md
```

## 🔧 Component Descriptions

### `main.py`
Initializes FastAPI app, sets up middleware (CORS), mounts all routers.

### `config.py`
Manages environment settings (API keys, mode, debug).

### `models/`
Defines input/output schemas using **Pydantic** for:
- Stock data
- Screener results
- Portfolio input/output
- Reports

### `services/`
Contains core business logic:
- **screener.py**: filters stocks by P/E, momentum, volume, etc.
- **optimizer.py**: uses AI/ML (e.g., RandomForest, MPT) for optimal portfolio
- **report_generator.py**: compiles PDF/HTML research reports

### `api/endpoints/`
Each file defines a specific API route (e.g. `/api/screener`, `/api/optimizer`) using FastAPI routers.

### `utils/`
Helpers to fetch data (e.g., from Yahoo Finance or NSE/BSE), compute financial metrics, clean data.

## 🧠 State Management

- Stateless REST API
- All state (e.g., user session, portfolios) is passed via request or stored in:
  - Local cache (Redis) or
  - Filesystem (temporary) or
  - DB (in production — SQLite/PostgreSQL)

## 🔌 External Services

- `yfinance`, `nsetools`, or Alpha Vantage: data fetching
- `sklearn`: ML models for portfolio scoring
- `pandas`, `numpy`: financial calculations
- `reportlab` or `WeasyPrint`: for PDF generation

## 🚀 Deployment

Use **Render**, **Railway**, or **AWS EC2**:

- Dockerfile ensures consistency
- Can run `uvicorn app.main:app` for API start

## 🧪 Testing

- Each service (screener, optimizer) has unit tests
- Endpoints tested using FastAPI test client
