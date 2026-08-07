import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging incoming requests and outgoing responses.
    """

    async def dispatch(self, request: Request, call_next):

        request_id = str(uuid.uuid4())

        start_time = time.perf_counter()

        request.state.request_id = request_id

        logger.info(
            "Request started | %s %s | request_id=%s",
            request.method,
            request.url.path,
            request_id,
        )

        try:
            response = await call_next(request)

        except Exception:
            duration = time.perf_counter() - start_time

            logger.exception(
                "Request failed | %s %s | duration=%.4fs | request_id=%s",
                request.method,
                request.url.path,
                duration,
                request_id,
            )

            raise

        duration = time.perf_counter() - start_time

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "Request completed | %s %s | status=%s | duration=%.4fs | request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration,
            request_id,
        )

        return response