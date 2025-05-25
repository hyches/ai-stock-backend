import os

# Zerodha Settings
ZERODHA_API_KEY: str = os.getenv("ZERODHA_API_KEY", "")
ZERODHA_API_SECRET: str = os.getenv("ZERODHA_API_SECRET", "")
ZERODHA_REDIRECT_URI: str = os.getenv("ZERODHA_REDIRECT_URI", "http://localhost:8000/api/v1/zerodha/callback") 