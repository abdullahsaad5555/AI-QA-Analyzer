import logging
from uuid import uuid4

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def _request_id(request: Request) -> str:
    return request.headers.get("X-Request-ID") or str(uuid4())


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    request_id = _request_id(request)

    logger.warning(
        "HTTPException %s %s -> %s | request_id=%s | detail=%s",
        request.method,
        request.url.path,
        exc.status_code,
        request_id,
        exc.detail,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "type": "http_error",
                "message": exc.detail,
                "status_code": exc.status_code,
                "request_id": request_id,
            },
        },
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = _request_id(request)

    logger.warning(
        "ValidationError %s %s | request_id=%s | errors=%s",
        request.method,
        request.url.path,
        request_id,
        exc.errors(),
    )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "type": "validation_error",
                "message": "Request validation failed",
                "status_code": 422,
                "request_id": request_id,
                "details": exc.errors(),
            },
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = _request_id(request)

    logger.exception(
        "Unhandled exception %s %s | request_id=%s",
        request.method,
        request.url.path,
        request_id,
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "type": "internal_server_error",
                "message": "An unexpected error occurred",
                "status_code": 500,
                "request_id": request_id,
            },
        },
    )
