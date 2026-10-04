import re
import uuid
from collections.abc import Callable

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

REQUEST_ID_HEADER = "X-Request-ID"
_REQUEST_ID_PATTERN = re.compile(r"[A-Za-z0-9-]{1,64}")

logger = structlog.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app=app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = self._get_request_id(request)
        request.state.request_id = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        status_code = 500

        try:
            resp: Response = await call_next(request)
            status_code = resp.status_code
            resp.headers[REQUEST_ID_HEADER] = request_id
            return resp
        finally:
            logger.info(
                "request finished",
                method=request.method,
                path=request.url.path,
                status_code=status_code,
            )

    def _get_request_id(self, request: Request) -> str:
        id = request.headers.get(REQUEST_ID_HEADER)

        if id and _REQUEST_ID_PATTERN.fullmatch(id):
            return id

        if id:
            logger.info("Invalid Request Id, re-generate", request_id=id)
        else:
            logger.info("No Request ID, Generate.")
        return uuid.uuid4().hex
