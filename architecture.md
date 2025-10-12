# AI Stock Trading Platform - Architecture Documentation

## Project Overview
A full-stack AI-powered trading platform with FastAPI backend and React frontend, featuring real-time market data, ML predictions, portfolio optimization, and paper trading capabilities.

## Current Status: 60% Complete - Needs Critical Fixes

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + TypeScript)            │
├─────────────────────────────────────────────────────────────┤
│  Pages: Dashboard, Trading, Screener, Research, Optimizer   │
│  Components: 63 React components with shadcn/ui            │
│  State: React Query + Context API                          │
│  Routing: React Router v6                                  │
└─────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP/WebSocket
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                        │
├─────────────────────────────────────────────────────────────┤
│  API Layer: 21 endpoint files + 8 v1 endpoints             │
│  Services: 30 business logic services                      │
│  Models: 11 database models (WITH DUPLICATES)              │
│  Core: Config, Security, Logging, Middleware               │
└─────────────────────────────────────────────────────────────┘
                                │
                                │ SQLAlchemy ORM
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER                           │
├─────────────────────────────────────────────────────────────┤
│  Primary: SQLite (default) / PostgreSQL (production)       │
│  Cache: Redis (for real-time data)                         │
│  Migrations: Alembic (1 migration file)                    │
└─────────────────────────────────────────────────────────────┘
                                │
                                │ External APIs
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                        │
├─────────────────────────────────────────────────────────────┤
│  Market Data: yfinance, Alpha Vantage, Yahoo Finance       │
│  Trading: Zerodha API (paper trading)                      │
│  ML: scikit-learn, pandas, TA-Lib                          │
└─────────────────────────────────────────────────────────────┘
```

## Critical Issues to Fix

### 1. DATABASE MODEL DUPLICATION (CRITICAL)
**Problem**: User model defined in 4 different places with conflicting schemas
- `app/models/user.py` - Main user model
- `app/models/trading.py` - Duplicate user model
- `app/models/database.py` - Another duplicate
- `app/core/security.py` - Pydantic user model

**Solution**: Consolidate to single source of truth in `app/models/user.py`

### 2. DATABASE CONNECTION DUPLICATION (CRITICAL)
**Problem**: get_db() function defined in 3 places
- `app/database.py` - Old implementation
- `app/db/session.py` - New implementation with connection pooling
- `app/api/deps.py` - API-specific implementation

**Solution**: Use only `app/db/session.py` and update all imports

### 3. BASE CLASS DUPLICATION (CRITICAL)
**Problem**: Base = declarative_base() in 3 places
- `app/models/database.py`
- `app/db/base.py`
- `app/database.py`

**Solution**: Use only `app/db/base_class.py` and remove others

### 4. MISSING API ENDPOINTS (CRITICAL)
**Problem**: v1/api.py references 8 endpoints that don't exist
- `app/api/v1/endpoints/users.py` - MISSING
- `app/api/v1/endpoints/portfolios.py` - MISSING
- `app/api/v1/endpoints/positions.py` - MISSING
- `app/api/v1/endpoints/trades.py` - MISSING
- `app/api/v1/endpoints/signals.py` - MISSING
- `app/api/v1/endpoints/backtests.py` - MISSING
- `app/api/v1/endpoints/market_data.py` - MISSING

**Solution**: Create missing endpoints or remove v1 router

### 5. IMPORT CONFLICTS (CRITICAL)
**Problem**: Mixed imports between old and new database modules
- Some files import from `app.database`
- Others import from `app.db.session`
- This causes runtime errors

**Solution**: Standardize all imports to use `app.db.session`