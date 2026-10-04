from collections.abc import Mapping
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


class ApplicationError(Exception):
    """Base class for application business errors"""

    code: str = "APP_ERROR"
    message: str = "An application error occurred"
    status_code: int = 400

    def __init__(
        self,
        message: str | None = None,
        code: str | None = None,
        status_code: int | None = None,
    ) -> None:
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.message)


class UnauthorizedError(ApplicationError):
    code: str = "UNAUTHORIZED"
    message: str = "Authentication required"
    status_code: int = 401


class InvalidTokenError(UnauthorizedError):
    code = "INVALID_TOKEN"
    message = "Invalid or expired token"


def _unified_error_response(
    request: Request,
    code: str,
    message: str,
    status_code: int,
    *,
    details: Any = None,  # noqa: ANN401
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    body: dict[str, Any] = {
        "code": code,
        "message": message,
        "request_id": getattr(request.state, "request_id", None),
    }
    if details is not None:
        body["details"] = details
    return JSONResponse(status_code=status_code, content=body, headers=headers)


async def application_error_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, ApplicationError)
    return _unified_error_response(
        request=request, status_code=exc.status_code, code=exc.code, message=exc.message
    )
