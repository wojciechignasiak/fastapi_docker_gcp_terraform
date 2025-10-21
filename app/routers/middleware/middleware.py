#internal modules
from app.custom_exceptions.custom_exceptions import CustomException

#3rd party libraries
from fastapi import Request, status
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

#1st party libraries
import logging
import time
import uuid

logger: logging.Logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id: str = str(uuid.uuid4())
        method: str = request.method
        path: str = request.url.path
        start_time: float = time.perf_counter()
        try:
            response: Response = await call_next(request)
            duration: float = (time.perf_counter() - start_time) * 1000
            logger.info(f"[{request_id}] {method} {path} -> {response.status_code} [{duration:.2f}ms]")
            response.headers["X-Request-ID"] = request_id
            return response
        except CustomException as e:
            if e.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                logger.warning(f"[{request_id}] {method} {path}: {e}")
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"detail": "Internal Server Error"},
                    headers={"X-Request-ID": request_id},
                )
            else:
                logger.info(f"[{request_id}] {method} {path}: {e}")
                return JSONResponse(
                    status_code=e.status_code,
                    content={"detail": e.message},
                    headers={"X-Request-ID": request_id},
                )
        except Exception as e:
            logger.error(f" [{request_id}] Unexpected error occurred {method} {path}: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal Server Error"},
                headers={"X-Request-ID": request_id},
            )