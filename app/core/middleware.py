"""
Custom middleware for the AI Stock Portfolio Platform Backend.

This module provides middleware for request logging, error handling, and Prometheus metrics collection.
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from app.core.config import settings
import json

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
    filename=settings.LOG_FILE
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging incoming requests and responses, including timing and status.
    Records Prometheus metrics for request count and latency.
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the incoming request, log details, and record metrics.

        Args:
            request (Request): Incoming FastAPI request.
            call_next (Callable): Next middleware or route handler.
        Returns:
            Response: FastAPI response object.
        """
        start_time = time.time()
        
        # Log request
        logger.info(f"Request started: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"Status: {response.status_code} Duration: {process_time:.2f}s"
            )
            
            # Record metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(process_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Request failed: {str(e)}", exc_info=True)
            raise

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for catching and logging unhandled exceptions during request processing.
    Returns a JSON error response and records error metrics.
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the incoming request and handle exceptions.

        Args:
            request (Request): Incoming FastAPI request.
            call_next (Callable): Next middleware or route handler.
        Returns:
            Response: FastAPI response object or error response.
        """
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}", exc_info=True)
            
            # Record error metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=500
            ).inc()
            
            return Response(
                content=json.dumps({
                    "detail": "Internal server error",
                    "error": str(e)
                }),
                status_code=500,
                media_type="application/json"
            )

class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware for collecting Prometheus metrics on request latency and errors.
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the incoming request and record metrics.

        Args:
            request (Request): Incoming FastAPI request.
            call_next (Callable): Next middleware or route handler.
        Returns:
            Response: FastAPI response object.
        """
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Record metrics
            process_time = time.time() - start_time
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(process_time)
            
            return response
            
        except Exception as e:
            # Record error metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=500
            ).inc()
            raise

    @staticmethod
    async def metrics_endpoint(request: Request) -> Response:
        """
        Metrics endpoint for Prometheus scraping.

        Args:
            request (Request): Incoming FastAPI request.
        Returns:
            Response: Prometheus metrics as plain text.
        """
        return Response(
            content=generate_latest(),
            media_type="text/plain"
        ) 