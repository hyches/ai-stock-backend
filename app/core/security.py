from datetime import datetime, timedelta
from typing import Optional, Dict, List, Set
from fastapi import HTTPException, Request, Depends, Security
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, validator
from app.core.config import Settings
settings = Settings() 
import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
from app.core.cache import redis_cache
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable
import hashlib
import hmac
from enum import Enum
from app.core.roles import UserRole

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Role definitions
class UserRole(str, Enum):
    ADMIN = "admin"
    TRADER = "trader"
    VIEWER = "viewer"
    SYSTEM = "system"

# Role permissions
ROLE_PERMISSIONS = {
    UserRole.ADMIN: {
        "manage_users",
        "manage_strategies",
        "manage_portfolios",
        "execute_trades",
        "view_reports",
        "manage_system"
    },
    UserRole.TRADER: {
        "manage_strategies",
        "manage_portfolios",
        "execute_trades",
        "view_reports"
    },
    UserRole.VIEWER: {
        "view_strategies",
        "view_portfolios",
        "view_reports"
    },
    UserRole.SYSTEM: {
        "manage_system",
        "execute_trades",
        "view_reports"
    }
}

# API Key header
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Session management
class SessionManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.session_ttl = 3600  # 1 hour
    
    async def create_session(self, user_id: str, role: UserRole) -> str:
        """Create a new session"""
        session_id = secrets.token_urlsafe(32)
        session_data = {
            "user_id": user_id,
            "role": role,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }
        await self.redis.setex(
            f"session:{session_id}",
            self.session_ttl,
            str(session_data)
        )
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        session_data = await self.redis.get(f"session:{session_id}")
        if session_data:
            await self.redis.setex(
                f"session:{session_id}",
                self.session_ttl,
                session_data
            )
            return eval(session_data)
        return None
    
    async def delete_session(self, session_id: str):
        """Delete a session"""
        await self.redis.delete(f"session:{session_id}")

# Initialize session manager
session_manager = SessionManager(redis_cache)

# CSRF protection
class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            csrf_token = request.headers.get("X-CSRF-Token")
            if not csrf_token or not self._verify_csrf_token(csrf_token, request):
                raise HTTPException(status_code=403, detail="Invalid CSRF token")
        return await call_next(request)
    
    def _verify_csrf_token(self, token: str, request: Request) -> bool:
        # Implement your CSRF token verification logic here
        return True  # Placeholder

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # 1 minute
RATE_LIMIT_MAX_REQUESTS = 100  # 100 requests per minute
request_counts = {}

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean up old entries
        request_counts[client_ip] = {
            timestamp: count for timestamp, count in request_counts.get(client_ip, {}).items()
            if current_time - timestamp < RATE_LIMIT_WINDOW
        }
        
        # Count requests in the current window
        window_requests = sum(request_counts.get(client_ip, {}).values())
        
        if window_requests >= RATE_LIMIT_MAX_REQUESTS:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(status_code=429, detail="Too many requests")
        
        # Add current request
        if client_ip not in request_counts:
            request_counts[client_ip] = {}
        request_counts[client_ip][current_time] = request_counts[client_ip].get(current_time, 0) + 1
        
        return await call_next(request)

# Request size limit middleware
class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.MAX_REQUEST_SIZE:
            raise HTTPException(status_code=413, detail="Request entity too large")
        return await call_next(request)

# API key validation
async def validate_api_key(api_key: str = Depends(api_key_header)):
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
    session_id: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None

class User(BaseModel):
    username: str
    role: UserRole
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
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
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
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        return {"username": username, "role": UserRole(role)}
    except JWTError:
        raise credentials_exception

def check_permissions(required_permissions: Set[str]):
    """Decorator to check user permissions"""
    async def permission_checker(user: Dict = Depends(get_current_user)):
        user_role = user["role"]
        user_permissions = ROLE_PERMISSIONS.get(user_role, set())
        
        if not required_permissions.issubset(user_permissions):
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )
        return user
    return permission_checker

# CORS middleware configuration
cors_middleware = CORSMiddleware(
    app=None,  # Will be set in main.py
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response

# Security headers middleware
async def security_headers_middleware(request: Request, call_next):
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

# Export middleware functions
rate_limit_middleware = RateLimitMiddleware
security_headers_middleware = SecurityHeadersMiddleware
request_size_limit_middleware = RequestSizeLimitMiddleware
csrf_middleware = CSRFMiddleware
