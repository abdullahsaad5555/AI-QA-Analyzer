import logging
import time
from uuid import uuid4

from fastapi import Request

logger = logging.getLogger(__name__)


async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    start_time = time.perf_counter()

    request.state.request_id = request_id

    logger.info(
        "Request started | request_id=%s | method=%s | path=%s",
        request_id,
        request.method,
        request.url.path,
    )

    try:
        response = await call_next(request)
    except Exception:
        process_time = time.perf_counter() - start_time

        logger.exception(
            "Request failed | request_id=%s | method=%s | path=%s | duration=%.4fs",
            request_id,
            request.method,
            request.url.path,
            process_time,
        )
        raise

    process_time = time.perf_counter() - start_time

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.4f}"

    logger.info(
        "Request completed | request_id=%s | method=%s | path=%s | status=%s | duration=%.4fs",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        process_time,
    )

    return response
