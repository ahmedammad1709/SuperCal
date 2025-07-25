from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging
import time

logger = logging.getLogger("uvicorn.error")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.2f}ms")
            return response
        except Exception as exc:
            logger.error(f"Error processing request {request.method} {request.url.path}: {exc}")
            raise 