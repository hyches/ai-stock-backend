# **Agent Action Plan: AI Trading System**

This document outlines the specific, ordered tasks required to transform the AI Trading System from its current prototype state into a fully functional, production-ready application. Follow these steps methodically.

**Core Objective:** Connect the disconnected frontend and backend, implement placeholder services, clean up the codebase, establish robust testing and CI/CD, and prepare for deployment.

## **Phase 1: Foundational Cleanup & Setup**

**Goal:** Establish a clean, consistent baseline.

* **Task 1.1: Delete Mock Backend APIs**  
  * **Action:** Delete the entire app/api/endpoints/ directory.  
  * **Files:** app/api/endpoints/\*  
  * **Guidance:** These are non-functional mocks superseded by app/api/v1/endpoints/.  
* **Task 1.2: Update Main API Router**  
  * **Action:** Edit app/api/api.py to remove all import statements and include\_router calls referencing the deleted mock endpoints in app/api/endpoints/. Ensure only routers from app/api/v1/endpoints/ are included.  
  * **Files:** app/api/api.py  
* **Task 1.3: Consolidate Backend Service Implementations**  
  * **Action:** Delete app/services/sentiment\_analysis.py. The functional service is app/services/sentiment.py. Update any imports.  
  * **Files:** app/services/sentiment\_analysis.py  
  * **Action:** Resolve conflicting implementations in app/services/report\_generator.py. **Decision:** Deprecate ResearchReport class and generate\_research\_report function. Refactor ReportGenerator class to be the sole implementation, removing dead code.  
  * **Files:** app/services/report\_generator.py  
* **Task 1.4: Consolidate Frontend API Utilities & Utils**  
  * **Action:** Create a single frontend/src/lib/api.ts module.  
    * Move axios instance setup and interceptors from frontend/src/lib/api-services.ts.  
    * Move API constants and endpoint definitions from frontend/src/utils/api.ts.  
    * Move all data-fetching functions (e.g., getStockDetails) from frontend/src/lib/api-services.ts into this new module.  
  * **Action:** Move React Query hooks from frontend/src/hooks/use-api.ts to a new file frontend/src/lib/queries.ts. Update imports.  
  * **Action:** Consolidate general utility functions. Delete one of the duplicate files: frontend/src/utils.ts or frontend/src/utils/utils.ts. Ensure the remaining file (preferably frontend/src/lib/utils.ts alongside api.ts) contains the necessary functions (cn).  
  * **Action:** Delete the old, now empty/redundant files: frontend/src/lib/api-services.ts, frontend/src/utils/api.ts, frontend/src/hooks/use-api.ts, and the duplicate utils file.  
  * **Action:** Perform a global search/replace in the frontend/src/ directory to update all import paths to the new consolidated locations (frontend/src/lib/api, frontend/src/lib/queries, frontend/src/lib/utils).  
  * **Files:** frontend/src/lib/api-services.ts, frontend/src/utils/api.ts, frontend/src/hooks/use-api.ts, frontend/src/utils.ts, frontend/src/utils/utils.ts, frontend/src/\*\*/\* (for imports)  
* **Task 1.5: Environment Variable Setup**  
  * **Action:** Review both .env.example (root) and frontend/.env.example. Create functional .env and frontend/.env files locally.  
  * **Action:** Document *all* required environment variables (backend and frontend) in docs/environment.md. Specify defaults and whether they are required for core functionality vs. optional features (e.g., ZERODHA\_API\_KEY).  
  * **Files:** .env.example, frontend/.env.example, docs/environment.md (new)  
* **Task 1.6: Setup Logging & Error Handling Framework**  
  * **Action:** Review app/core/logging.py and app/middleware/error\_handler.py. Ensure structured logging (using the configured logger) and consistent API error responses (using FastAPI exception handlers and standard HTTP status codes) are established early.  
  * **Files:** app/core/logging.py, app/middleware/error\_handler.py, app/main.py (to register handlers)

## **Phase 2: Critical Path Implementation (Core Functionality)**

**Goal:** Connect the frontend and backend for basic trading and data display. Implement the primary data source.

* **Task 2.1: Implement Data Source / Broker Integration (BLOCKER)**  
  * **Priority:** **Highest**. This blocks many other backend services.  
  * **Action:** Implement the app/services/zerodha\_service.py.  
  * **Decision Guidance:**  
    * **Option A (Live Trading):** If Zerodha API keys **ARE** available, fully implement the Kite Connect API calls for login, get\_profile, get\_holdings, get\_positions, place\_order, get\_instruments, get\_quote, get\_historical\_data, and WebSocket connection for live ticks. Remove all paper trading fallback logic. Use httpx for async API calls. Implement robust error handling for API failures.  
    * **Option B (Reliable Data \- No Live Trading):** If Zerodha keys **ARE NOT** available or live trading is deferred, remove the Kite Connect dependency *for now*. Refactor the service (or create a new MarketDataService) to use yfinance or another reliable library for *all* required data fetching (get\_quote, get\_historical\_data, get\_instruments \- potentially from a static list). Ensure consistent data structures are returned. Paper trading logic can remain for simulated order execution but ensure it uses the fetched market data correctly.  
  * **Files:** app/services/zerodha\_service.py, app/models/zerodha.py (if using paper trading DB)  
* **Task 2.2: Rewrite Frontend TradingContext (BLOCKER)**  
  * **Priority:** **Highest** (concurrent with 2.1). This blocks all UI functionality.  
  * **Action:** Completely rewrite frontend/src/context/TradingContext.tsx.  
    1. Remove *all* useState variables acting as the fake database (virtualCash, transactions, watchlist, portfolio).  
    2. Remove *all* useEffect hooks saving/loading from localStorage.  
    3. Refactor every function (buyStock, sellStock, addToWatchlist, etc.) to be an async function.  
    4. Inside these functions, call the corresponding backend API endpoints using the consolidated API service (frontend/src/lib/api.ts). Use useMutation hooks from react-query (@tanstack/react-query) for actions that modify data (buy, sell, update watchlist).  
    5. Do *not* store portfolio, watchlist, or transaction data directly in this context. Rely entirely on react-query to fetch and cache this server state. This context might only be needed to expose the mutation functions.  
  * **Files:** frontend/src/context/TradingContext.tsx, frontend/src/lib/api.ts, frontend/src/lib/queries.ts  
* **Task 2.3: Refactor Core UI Components**  
  * **Action:** Go through pages and components currently using useTrading(): Dashboard.tsx, Trading.tsx, StockDetails.tsx, Transactions.tsx, PortfolioSummary.tsx, etc..  
  * **Action:** Remove calls to useTrading() for fetching data.  
  * **Action:** Replace data fetching with the appropriate react-query hooks from frontend/src/lib/queries.ts (e.g., usePortfolio, useWatchlist, useTransactions).  
  * **Action:** Implement UI states based on react-query hook status (isLoading, isError, data). Use Skeleton components for loading states and Alert components or Toast notifications for errors.  
  * **Action:** Connect action buttons (Buy, Sell, Add to Watchlist) to the mutation functions exposed by the rewritten TradingContext or directly via useMutation hooks.  
  * **Files:** frontend/src/pages/\*.tsx, frontend/src/components/dashboard/\*.tsx, frontend/src/components/TradingActions.tsx, etc.

## **Phase 3: Backend Service Implementation & API Expansion**

**Goal:** Implement placeholder services and expose them via APIs. Prioritize based on dependencies and perceived value.

* **Task 3.1: Implement backtest.py**  
  * **Action:** Implement the \_get\_historical\_data method using the data source established in Task 2.1 (ZerodhaService or yfinance).  
  * **Action:** Implement analyze\_results helpers to calculate Sharpe ratio, Max Drawdown, CAGR, etc., using standard financial formulas.  
  * **Action:** Create API endpoints in app/api/v1/endpoints/backtests.py for run\_backtest, optimize\_parameters, and fetching results. Use Pydantic models for request/response validation. Ensure proper background task handling (e.g., using FastAPI BackgroundTasks or Celery) for potentially long-running backtests/optimizations.  
  * **Files:** app/services/backtest.py, app/api/v1/endpoints/backtests.py, app/schemas/trading.py (add backtest schemas)  
* **Task 3.2: Implement fundamental\_analysis.py**  
  * **Action:** Implement data fetching (\_get\_balance\_sheet, etc.) using the data source from Task 2.1 or yfinance's Ticker object methods (.info, .financials, .balance\_sheet, etc.).  
  * **Action:** Implement financial ratio calculations based on standard formulas.  
  * **Action:** Create an API endpoint in a new file app/api/v1/endpoints/analysis.py to expose get\_comprehensive\_analysis. Ensure a well-structured response using Pydantic models. Use caching (@cache\_response) aggressively here.  
  * **Files:** app/services/fundamental\_analysis.py, app/api/v1/endpoints/analysis.py (new), app/schemas/market.py (add analysis schemas)  
* **Task 3.3: Implement report\_generator.py (Consolidated)**  
  * **Action:** Implement the placeholder methods in the refactored ReportGenerator class by calling functional services (sentiment.py, competitor.py, fundamental\_analysis.py once implemented).  
  * **Action:** Implement basic PDF generation using reportlab based on fetched data. Consider a simple AI summary using an LLM API if available, otherwise use a template.  
  * **Action:** Create an API endpoint in app/api/v1/endpoints/reports.py to trigger report generation (potentially as a background task) and return the report (e.g., as a downloadable file or link).  
  * **Files:** app/services/report\_generator.py, app/api/v1/endpoints/reports.py (new or refactor existing mock), app/schemas/report.py (new or refactor)  
* **Task 3.4: Implement Proper ML Model**  
  * **Action:** Replace the placeholder logic in app/services/ml\_predictions.py with a transparent, well-documented model.  
  * **Goal:** Implement a binary classification model to predict if a stock's price will increase by \>1% in the next 5 trading days.  
  * **Steps:**  
    1. **Data:** Use yfinance (via the updated ZerodhaService) to get 5+ years of OHLCV data for a sample set of stocks (e.g., NIFTY 50 components).  
    2. **Features:** Create features including: 5-day, 20-day SMA, RSI (14), MACD difference, Bollinger Band width, 1-day return, 5-day return.  
    3. **Target:** Create the binary target variable (1 if Close price 5 days later is \> 1.01 \* Current Close, else 0). Handle edge cases near the end of the dataset.  
    4. **Split:** Chronologically split data (e.g., 70% train, 15% validation, 15% test).  
    5. **Train:** Train a RandomForestClassifier (using scikit-learn). Tune n\_estimators and max\_depth using the validation set.  
    6. **Evaluate:** Report Accuracy, Precision, Recall, F1, and AUC-ROC on the test set.  
    7. **Save & Version:** Save the trained model using joblib (e.g., price\_increase\_predictor\_v1.joblib). Ensure scikit-learn version is added explicitly to requirements.txt.  
    8. **Integrate:** Update ml\_predictions.py to load this new model, implement the *exact same* feature calculation logic for prediction requests, and return the prediction (0 or 1).  
    9. **API:** Update the API endpoint (app/api/v1/endpoints/ml.py) and schemas (app/schemas/ml.py) accordingly.  
  * **Files:** app/services/ml\_predictions.py, ml\_model.joblib (delete), price\_increase\_predictor\_v1.joblib (new), app/api/v1/endpoints/ml.py, app/schemas/ml.py, (potentially a new scripts/train\_model.py)  
* **Task 3.5: Enhance screener.py**  
  * **Action:** Replace the hardcoded stock list with a dynamic list from the Task 2.1 data source.  
  * **Action:** Create an API endpoint in app/api/v1/endpoints/screener.py accepting filter criteria via Pydantic model and returning matching stocks. Implement pagination using app/utils/pagination.py.  
  * **Files:** app/services/screener.py, app/api/v1/endpoints/screener.py (new or refactor mock), app/schemas/market.py (add screener schemas)  
* **Task 3.6: Implement Other High-Value Services (Selectively)**  
  * **Action:** Review and implement other potentially valuable services based on complexity and available data:  
    * forecasting.py: Relatively straightforward if data source is ready. Requires API endpoint and Pydantic models.  
    * sentiment.py: Already functional, ensure API endpoint exists and is robust.  
    * technical\_analysis.py: Implement placeholder patterns/support-resistance if feasible. Requires API endpoint.  
    * optimizer.py: Review logic, potentially replace ML approach with classic MPT if simpler. Add missing sector allocation metrics.  
    * competitor.py: Fix competitor discovery logic (use sector fallback primarily). Requires API endpoint.  
  * **Action:** For *each* service implemented, create corresponding API endpoints in app/api/v1/endpoints/, ensuring RESTful design and Pydantic validation. Add necessary schemas in app/schemas/. Apply caching where appropriate.  
  * **Files:** app/services/\*.py, app/api/v1/endpoints/\*.py, app/schemas/\*.py

## **Phase 4: Frontend Expansion & Refinement**

**Goal:** Build UI for newly implemented backend features and refine existing UI.

* **Task 4.1: Build UI for Implemented Services**  
  * **Action:** Connect existing placeholder pages to their corresponding backend APIs using react-query hooks:  
    * Screener.tsx \-\> Screener API  
    * Optimizer.tsx \-\> Optimizer API  
    * Research.tsx \-\> Fundamental Analysis API, Competitor API, Sentiment API  
    * Reports.tsx \-\> Report Generator API  
  * **Action:** Design and build *new* pages/components for high-value features implemented in Phase 3:  
    * **Backtesting:** UI for configuration, running tests, and displaying results (equity curve, metrics table).  
    * **Forecasting:** UI for selecting stock/model/days and displaying forecast chart.  
    * **Technical Analysis:** Integrate TA indicators display into existing stock charts (e.g., StockChart.tsx).  
  * **Action:** Ensure all new UI includes proper loading (Skeleton), error (Alert/Toast), and empty states.  
  * **Files:** frontend/src/pages/\*.tsx, frontend/src/components/\*\*/\*.tsx, frontend/src/lib/queries.ts, frontend/src/lib/api.ts  
* **Task 4.2: Frontend State Management Review**  
  * **Action:** Ensure clear separation between server state (react-query) and global UI state (React Context/Zustand for theme, auth status). Refactor if necessary.  
  * **Files:** frontend/src/context/\*.tsx, frontend/src/App.tsx  
* **Task 4.3: UI Component Library Assessment & Charting**  
  * **Action:** Evaluate if shadcn/ui components are sufficient for new UIs (especially charts).  
  * **Action:** Add and configure a charting library (e.g., recharts, react-chartjs-2). Integrate it into StockChart.tsx and new components for Backtesting/Forecasting.  
  * **Files:** frontend/src/components/ui/, frontend/package.json

## **Phase 5: Testing & Quality Assurance**

**Goal:** Ensure application correctness and stability through comprehensive testing.

* **Task 5.1: Discard testsprite\_tests**  
  * **Action:** Delete the entire testsprite\_tests/ directory and related root files (run\_testsprite\_tests.py, testsprite\_config.json). Its value is informational (test plan) and diagnostic (report).  
  * **Files:** testsprite\_tests/, run\_testsprite\_tests.py, testsprite\_config.json  
* **Task 5.2: Implement Backend Test Plan in pytest**  
  * **Action:** Use testsprite\_backend\_test\_plan.json (before deleting) and tests/TEST\_PLAN.md as requirements.  
  * **Action:** Implement API integration tests in tests/api/ for all functional endpoints, covering scenarios from the testsprite plan (auth flow, trading operations, etc.). Use the client fixture from conftest.py. Fix bugs identified in the testsprite-mcp-test-report.md (e.g., login username/email mismatch).  
  * **Action:** Write unit tests for complex logic within services (e.g., financial calculations, backtest metrics, new ML model logic). Place these in corresponding test files (e.g., tests/services/test\_fundamental\_analysis.py).  
  * **Action:** Ensure tests cover success cases, failure cases (invalid input, permissions), and edge cases. Mock external dependencies (like broker APIs or yfinance) where necessary for unit tests.  
  * **Files:** tests/\*\*/\*.py, tests/conftest.py  
* **Task 5.3: Implement Basic Frontend Tests**  
  * **Action:** Set up Vitest and React Testing Library (confirm config in vite.config.ts).  
  * **Action:** Write basic rendering and interaction tests for critical components: Login.tsx, TradingActions.tsx, key forms for Screener/Optimizer/Backtesting. Focus on ensuring elements render and form submissions can be initiated.  
  * **Files:** frontend/src/\*\*/\*.test.tsx (new), frontend/vite.config.ts

## **Phase 6: Production Hardening & DevOps**

**Goal:** Secure the application, finalize CI/CD, and establish a deployment strategy.

* **Task 6.1: Implement Security Measures**  
  * **Action:** Modify Dockerfile to create and run the application as a non-root user.  
  * **Action:** Implement CSRF protection (e.g., checking Origin header or using a double-submit cookie) in app/core/security.py or as a FastAPI middleware in app/main.py.  
  * **Action:** Refactor RateLimitMiddleware in app/core/security.py to use Redis (via app.core.cache) for distributed rate limiting.  
  * **Action:** Implement JWT token blacklisting on logout (e.g., storing revoked JTI in Redis with expiry) within the authentication logic in app/api/v1/endpoints/auth.py and app/core/security.py.  
  * **Files:** Dockerfile, app/core/security.py, app/main.py, app/api/v1/endpoints/auth.py, app.core.cache.py  
* **Task 6.2: Finalize CI/CD Pipeline**  
  * **Action:** Consolidate GitHub Actions workflows. **Decision:** Use ci-cd.yml as the base.  
  * **Action:** Merge essential steps from test.yml (multi-python testing, bandit, safety) and ci.yml (linting/formatting checks \- black, flake8, mypy) into the test job of ci-cd.yml. Configure tools via pyproject.toml where possible.  
  * **Action:** Ensure the test job runs the complete pytest suite (from Phase 5\) using requirements-test.txt.  
  * **Action:** Configure the build job to build the final multi-stage Docker image (from Task 6.3) and push it to a container registry (e.g., Docker Hub, GHCR).  
  * **Action:** Configure the deploy job for the chosen strategy (e.g., SSH into server and run docker-compose pull && docker-compose up \-d, or trigger a Kubernetes deployment update). Use GitHub secrets for credentials/keys.  
  * **Action:** Delete ci.yml and test.yml.  
  * **Files:** .github/workflows/ci-cd.yml, .github/workflows/ci.yml (delete), .github/workflows/test.yml (delete), pyproject.toml  
* **Task 6.3: Define and Implement Deployment Strategy**  
  * **Action:** **Decision:** Standardize on Docker deployment. Deprecate Vercel strategy.  
  * **Action:** Create/Refine a multi-stage Dockerfile. Stage 1 (node base): install frontend deps, build static assets. Stage 2 (python base): install backend deps (requirements.txt). Final stage (python-slim base): copy backend code from Stage 2, copy built frontend assets from Stage 1 into a ./static directory, install runtime deps only, create non-root user, run uvicorn via CMD. Ensure FastAPI serves static files from ./static.  
  * **Action:** Create docker-compose.yml defining services for the backend application, PostgreSQL database, and Redis. Use volumes for persistent data. Configure networking and environment variables.  
  * **Action:** Update ci-cd.yml's deploy job to use docker-compose commands via SSH.  
  * **Action:** Delete vercel.json.  
  * **Files:** Dockerfile, docker-compose.yml (new), .github/workflows/ci-cd.yml, vercel.json (delete), app/main.py (add static files mount)  
* **Task 6.4: Developer Setup & Seeding Scripts**  
  * **Action:** Ensure scripts/create\_tables.py is **removed** or updated to use Alembic (alembic upgrade head). Ensure alembic/env.py correctly reads the database URL from config. The primary mechanism for schema management must be Alembic.  
  * **Action:** Review and enhance scripts/seed\_database.py to provide sufficient and realistic sample data (users, strategies, market data if using paper trading mode) for local development and testing. Make it idempotent if possible.  
  * **Files:** scripts/create\_tables.py (deprecate/remove), alembic/env.py, alembic.ini, scripts/seed\_database.py

## **Phase 7: Final Review & Documentation**

**Goal:** Ensure all documentation is consolidated, accurate, and reflects the final state.

* **Task 7.1: Consolidate Documentation**  
  * **Action:** Move this AGENT\_ACTION\_PLAN.md to docs/action-plan.md.  
  * **Action:** Move the FINAL\_ARCHITECT\_OVERVIEW.md to docs/architect-overview.md.  
  * **Action:** Merge relevant content from architecture.md into docs/architect-overview.md. Delete architecture.md.  
  * **Action:** Review and update docs/deployment.md, docs/api\_examples.md, docs/backup-recovery.md, ensuring they reflect the final implementation and Docker deployment strategy. Add docs/environment.md (from Task 1.5).  
  * **Action:** Move all other relevant root markdown files (PROJECT\_SUMMARY.md, TESTSPRITE\_GUIDE.md, tasks.md, FIX\_ALL\_PLAN.md etc. \- archive if obsolete) into /docs or an /archive subfolder.  
  * **Action:** Update the root README.md to be concise, explain the project briefly, mention setup using docker-compose, and link prominently to /docs/architect-overview.md as the main entry point for developers.  
  * **Files:** All \*.md files, /docs/ directory.  
* **Task 7.2: Final Code Review and Cleanup**  
  * **Action:** Perform a final pass through the codebase, removing any remaining commented-out code, TODOs (that were addressed), or unused imports/variables. Ensure consistent formatting (black). Run linters (flake8, mypy) and fix violations.  
  * **Files:** Entire codebase (app/, frontend/src/)  
* **Task 7.3: Pre-Production Check**  
  * **Action:** Build the final Docker image. Deploy to a staging environment using docker-compose.yml.  
  * **Action:** Run Alembic migration (alembic upgrade head) and seeding script in staging.  
  * **Action:** Conduct end-to-end testing of core user flows in the staging environment.  
  * **Action:** Verify all environment variables are correctly set for production deployment (using secrets management, not hardcoding).