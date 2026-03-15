import logging
import time
from pythonjsonlogger import jsonlogger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.middleware.request_id import request_id_ctx_var

class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx_var.get()
        return True

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers:
        logger.removeHandler(handler)

    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s %(request_id)s',
        timestamp=True
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.addFilter(RequestIDFilter())

    # Avoid too much noise from some libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        logger = logging.getLogger("api.request")

        start_time = time.time()

        # We don't log the full request to avoid logging sensitive data (tokens, etc.)
        logger.info(
            f"Started {request.method} {request.url.path}",
            extra={"method": request.method, "path": request.url.path}
        )

        try:
            response = await call_next(request)

            process_time = time.time() - start_time
            logger.info(
                f"Completed {request.method} {request.url.path} with status {response.status_code}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_seconds": round(process_time, 4)
                }
            )
            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Failed {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_seconds": round(process_time, 4),
                    "error": str(e)
                },
                exc_info=True
            )
            raise
