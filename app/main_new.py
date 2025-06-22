from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config import settings
from app.core.middleware import ErrorHandlingMiddleware, RequestLoggingMiddleware
from app.db.base import Base, engine


def get_application():
    _app = FastAPI(
        title=settings.SERVER_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    _app.add_middleware(ErrorHandlingMiddleware)
    _app.add_middleware(RequestLoggingMiddleware)


    _app.include_router(api_router, prefix=settings.API_V1_STR)

    return _app


app = get_application()

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine) 