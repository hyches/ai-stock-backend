# Environment Variables

This document lists all the environment variables required for the AI Trading System, for both the backend and the frontend.

## Backend Environment Variables

These variables are defined in the `.env` file in the root of the project.

| Variable | Description | Default | Required |
| --- | --- | --- | --- |
| `DATABASE_URL` | The connection string for the database. | `sqlite:///./test.db` | Yes |
| `SQL_ECHO` | Whether to echo SQL statements to the console. | `false` | No |
| `REDIS_HOST` | The hostname of the Redis server. | `localhost` | Yes |
| `REDIS_PORT` | The port of the Redis server. | `6379` | Yes |
| `REDIS_DB` | The Redis database to use. | `0` | No |
| `REDIS_PASSWORD` | The password for the Redis server. | | No |
| `SECRET_KEY` | The secret key for signing JWTs. | `your-secret-key-here` | Yes |
| `ALGORITHM` | The algorithm to use for signing JWTs. | `HS256` | Yes |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | The expiration time for access tokens, in minutes. | `30` | Yes |
| `ZERODHA_API_KEY` | The API key for the Zerodha Kite Connect API. | | No |
| `ZERODHA_API_SECRET` | The API secret for the Zerodha Kite Connect API. | | No |
| `TRADING_ENABLED` | Whether to enable live trading. | `false` | No |
| `LIVE_TRADING` | Whether to enable live trading. | `false` | No |
| `ALPHA_VANTAGE_API_KEY` | The API key for Alpha Vantage. | | No |
| `YAHOO_FINANCE_API_KEY` | The API key for Yahoo Finance. | | No |
| `BACKEND_CORS_ORIGINS` | A comma-separated list of allowed CORS origins. | `["http://localhost:3000"]` | Yes |
| `LOG_LEVEL` | The logging level. | `INFO` | No |

## Frontend Environment Variables

These variables are defined in the `.env` file in the `frontend` directory.

| Variable | Description | Default | Required |
| --- | --- | --- | --- |
| `VITE_API_BASE_URL` | The base URL for the backend API. | `http://localhost:8000` | Yes |
| `VITE_API_VERSION` | The version of the backend API. | `/api/v1` | Yes |
| `VITE_WS_URL` | The URL for the WebSocket server. | `ws://localhost:8000/ws` | Yes |
| `VITE_ENABLE_TRADING` | Whether to enable trading features in the UI. | `true` | No |
| `VITE_ENABLE_ML` | Whether to enable machine learning features in the UI. | `true` | No |
| `VITE_ENABLE_ALERTS` | Whether to enable alert features in the UI. | `true` | No |
| `VITE_ENABLE_BACKUP` | Whether to enable backup features in the UI. | `true` | No |
| `VITE_DEFAULT_THEME` | The default theme for the UI. | `light` | No |
| `VITE_DEFAULT_LANGUAGE` | The default language for the UI. | `en` | No |
| `VITE_DEBUG` | Whether to enable debug mode. | `false` | No |
| `VITE_MOCK_API` | Whether to use a mock API. | `false` | No |
| `VITE_ALPHA_VANTAGE_API_KEY` | The API key for Alpha Vantage. | | No |
| `VITE_YAHOO_FINANCE_API_KEY` | The API key for Yahoo Finance. | | No |
| `VITE_DEFAULT_RISK_LEVEL` | The default risk level for trading. | `medium` | No |
| `VITE_MAX_POSITION_SIZE` | The maximum position size for trading. | `10000` | No |
| `VITE_DEFAULT_STOP_LOSS` | The default stop loss for trading. | `0.02` | No |
| `VITE_ML_MODEL_VERSION` | The version of the machine learning model. | `1.0.0` | No |
| `VITE_PREDICTION_CONFIDENCE_THRESHOLD` | The confidence threshold for machine learning predictions. | `0.7` | No |
| `VITE_ENABLE_PUSH_NOTIFICATIONS` | Whether to enable push notifications. | `false` | No |
| `VITE_ENABLE_EMAIL_NOTIFICATIONS` | Whether to enable email notifications. | `false` | No |
| `VITE_CACHE_DURATION` | The cache duration for API requests, in milliseconds. | `300000` | No |
| `VITE_REQUEST_TIMEOUT` | The timeout for API requests, in milliseconds. | `30000` | No |
| `VITE_MAX_RETRIES` | The maximum number of retries for failed API requests. | `3` | No |
