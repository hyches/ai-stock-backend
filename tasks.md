# API Settings
API_V1_PREFIX=/api/v1
DEBUG=True
ENVIRONMENT=development

# Stock Data API Keys
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
YAHOO_FINANCE_API_KEY=your_yahoo_finance_key_here

# Database Settings (for future use)
DATABASE_URL=sqlite:///./stock_portfolio.db

# Security
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
FRONTEND_URL=https://preview--alpha-ai-portfolio-pro.lovable.app

# Engineering Tasks — Build AI Stock Backend MVP

Each task is atomic, testable, and leads to a functional MVP. Follow order sequentially.

## 🛠️ SETUP

### Task 1: Initialize GitHub Repository
- Create a public/private GitHub repo: `ai-stock-backend`
- Add `.gitignore`, `README.md`, `LICENSE`, `requirements.txt`

### Task 2: Setup FastAPI project structure
- Create `app/`, `tests/`, and boilerplate files
- Add `main.py` with FastAPI app
- Add CORS middleware for frontend

### Task 3: Add config loader
- Create `config.py` to manage environment variables
- Load `.env` file with `dotenv`

## 📊 SCREENER MODULE

### Task 4: Build `StockIn`, `StockOut` Pydantic models
- File: `models/stock.py`

### Task 5: Create `/api/screener` endpoint
- File: `api/endpoints/screener.py`
- Input: Sector, MinVolume, MaxPE
- Output: Filtered stock list

### Task 6: Implement `services/screener.py`
- Filter stocks using:
  - P/E ratio
  - Market Cap
  - Technicals (Moving Average > Price)

## 📈 PORTFOLIO OPTIMIZER

### Task 7: Build `PortfolioInput`, `PortfolioOutput` models
- File: `models/portfolio.py`

### Task 8: Create `/api/optimizer` endpoint
- File: `api/endpoints/optimizer.py`
- Accept: selected stocks, capital
- Return: weights, expected return, risk

### Task 9: Implement `services/optimizer.py`
- Use RandomForest or Sharpe Ratio ranking
- Optimize weights with constraints

## 📃 RESEARCH REPORT MODULE

### Task 10: Build `ReportRequest`, `ReportResponse` models
- File: `models/report.py`

### Task 11: Create `/api/research/report` endpoint
- Input: stock ticker
- Output: AI-generated summary + financials

### Task 12: Implement `report_generator.py`
- Pull stock financials
- Add sentiment score, AI comment
- Generate PDF (via `reportlab` or `pdfkit`)

## 🧪 TESTING

### Task 13: Write tests for screener module
- File: `tests/test_screener.py`

### Task 14: Write tests for optimizer module
- File: `tests/test_optimizer.py`

### Task 15: Write endpoint tests using FastAPI TestClient

## 🐳 DEPLOYMENT

### Task 16: Write Dockerfile
- Include all dependencies
- Expose port 8000

### Task 17: Deploy backend
- Use Railway/Render
- Set backend base URL for frontend

## 🔁 INTEGRATION

### Task 18: Connect frontend to backend APIs
- Use `VITE_API_BASE_URL` in frontend
- Test calls from `/api/screener`, `/api/optimizer`, etc.

## ✅ DONE

At this point, the backend MVP is functional:
- Screener
- Optimizer
- Research reports
- Connected to frontend
