from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.core.middleware import request_context_middleware
from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import init_db
from app.core.error_handlers import (
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)

# Global/default limiter by client IP
# Tune this after observing real traffic.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup/shutdown lifecycle handler.
    Creates DB tables on startup.
    """
    await init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Attach limiter to app state and register rate-limit handler/middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.middleware("http")(request_context_middleware)

# Versioned API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/", tags=["Health"])
@limiter.exempt
async def read_root():
    return {
        "message": "Backend is running 🚀",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }