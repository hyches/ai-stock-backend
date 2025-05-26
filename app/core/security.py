from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, Request, Depends, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, validator
from app.config import Settings
settings = Settings() 
import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
from app.core.cache import redis_cache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Key header
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# CSRF protection
class CSRFMiddleware:
    """
    CSRFMiddleware:
    A class to manage Cross-Site Request Forgery (CSRF) tokens for secure web application sessions.
    Parameters:
        - None during initialization.
    Processing Logic:
        - Generates a unique, secure token for use in CSRF protection.
        - Validates the presence of a given token in the stored collection of CSRF tokens.
    Examples:
        - Use `generate_token()` to create a new CSRF token.
        - Verify a token's validity with `validate_token(token)`.
    """
    def __init__(self):
        self.csrf_tokens = {}

    def generate_token(self) -> str:
        token = secrets.token_urlsafe(32)
        return token

    def validate_token(self, token: str) -> bool:
        return token in self.csrf_tokens

csrf_middleware = CSRFMiddleware()

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # 1 minute
RATE_LIMIT_MAX_REQUESTS = {
    "default": 60,
    "auth": 5,
    "stock_analysis": 30,
    "portfolio": 20,
    "report": 10
}

class RateLimiter:
    """Rate limiting implementation using Redis"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def check_rate_limit(self, key: str, limit_type: str = "default") -> bool:
        """Check if request is within rate limits"""
        current = int(time.time())
        window_start = current - RATE_LIMIT_WINDOW
        
        # Get request count for the window
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(current): current})
        pipe.expire(key, RATE_LIMIT_WINDOW)
        _, request_count, _, _ = await pipe.execute()
        
        # Check against limit
        max_requests = RATE_LIMIT_MAX_REQUESTS.get(limit_type, RATE_LIMIT_MAX_REQUESTS["default"])
        return request_count < max_requests

class SecurityMiddleware:
    """Security middleware for request validation and rate limiting"""
    
    def __init__(self, app):
        self.app = app
        self.redis = redis_cache
        self.rate_limiter = RateLimiter(self.redis)
    
    async def __call__(self, request: Request, call_next):
        # Get client IP
        """Handle incoming requests with rate limiting and security headers.
        Parameters:
            - request (Request): The incoming HTTP request.
            - call_next (function): The function to proceed with the next part of the request pipeline.
        Returns:
            - Response: The HTTP response with appropriate security headers.
        Processing Logic:
            - Extracts the client's IP address from the request.
            - Determines the type of rate limit to apply based on the request path.
            - Checks if the request exceeds the rate limit, raising an HTTP 429 exception if it does.
            - Adds security headers to the response for enhanced web security."""
        client_ip = request.client.host
        
        # Determine rate limit type based on path
        path = request.url.path
        if path.startswith("/api/auth"):
            limit_type = "auth"
        elif path.startswith("/api/stocks"):
            limit_type = "stock_analysis"
        elif path.startswith("/api/portfolios"):
            limit_type = "portfolio"
        elif path.startswith("/api/reports"):
            limit_type = "report"
        else:
            limit_type = "default"
        
        # Check rate limit
        rate_limit_key = f"rate_limit:{client_ip}:{limit_type}"
        if not await self.rate_limiter.check_rate_limit(rate_limit_key, limit_type):
            raise HTTPException(
                status_code=429,
                detail="Too many requests",
                headers={"Retry-After": str(RATE_LIMIT_WINDOW)}
            )
        
        # Add security headers
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

# Request size limit middleware
async def request_size_limit_middleware(request: Request, call_next):
    """Request size limit middleware to restrict oversized HTTP requests.
    Parameters:
        - request (Request): The incoming HTTP request.
        - call_next (Callable): A function to process the next middleware or endpoint.
    Returns:
        - Response: The HTTP response from the subsequent middleware or endpoint.
    Processing Logic:
        - Checks if the 'Content-Length' header of the request exceeds a defined maximum request size.
        - Raises an HTTPException with status code 413 if the request entity is too large."""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.MAX_REQUEST_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Request entity too large"
        )
    response = await call_next(request)
    return response

# API key validation
async def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return api_key

# Authentication models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    """The `User` class represents a user entity with a username and an optional disabled status.
    Parameters:
        - username (str): The username of the user, must be alphanumeric.
        - disabled (Optional[bool]): Indicates if the user is disabled; defaults to None.
    Processing Logic:
        - Validates that the `username` must be alphanumeric; raises a `ValueError` if not."""
    username: str
    disabled: Optional[bool] = None

    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

class UserInDB(User):
    hashed_password: str

# Security functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return {"username": username}

# CORS middleware configuration
cors_middleware = CORSMiddleware(
    app=None,  # Will be set in main.py
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers middleware
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to HTTP responses.
    Parameters:
        - request (Request): The HTTP request object.
        - call_next: A callable that takes a request and returns a response.
    Returns:
        - Response: The HTTP response object with added security headers.
    Processing Logic:
        - Adds standard security headers to enhance protection against common vulnerabilities.
        - Ensures 'X-Content-Type-Options' to prevent MIME-type sniffing.
        - Sets 'X-Frame-Options' to DENY to prevent clickjacking.
        - Implements 'X-XSS-Protection' to enable cross-site scripting filters."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response 

class APIKeyManager:
    """API key management for external services"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def rotate_api_key(self, service: str) -> str:
        """Rotate API key for a service"""
        # Generate new key
        new_key = self._generate_api_key()
        
        # Store new key
        await self.redis.set(f"api_key:{service}", new_key)
        
        # Schedule old key deletion
        await self.redis.set(f"api_key:{service}:old", await self.redis.get(f"api_key:{service}"))
        await self.redis.expire(f"api_key:{service}:old", 86400)  # 24 hours
        
        return new_key
    
    def _generate_api_key(self) -> str:
        """Generate a new API key"""
        return jwt.encode(
            {"timestamp": datetime.utcnow().timestamp()},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

# Initialize security components
api_key_manager = APIKeyManager(redis_cache)
