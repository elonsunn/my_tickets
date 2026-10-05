import os
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal

import anyio
import jwt
from pwdlib import PasswordHash

from app.core.exceptions import InvalidTokenError

_LIMITER = anyio.CapacityLimiter(os.cpu_count() or 1)
_hash = PasswordHash.recommended()


async def hash_password(password: str) -> str:
    return await anyio.to_thread.run_sync(_hash.hash, password, limiter=_LIMITER)


async def verify_password(password: str, hashed_password: str) -> bool:
    return await anyio.to_thread.run_sync(
        _hash.verify, password, hashed_password, limiter=_LIMITER
    )


TokenType = Literal["access", "refresh"]

_REQUIRED_CLAIMS = ["sub", "type", "jti", "iat", "exp"]


@dataclass(frozen=True, slots=True)
class TokenClaims:
    subject: str
    token_type: TokenType
    token_id: str
    expire_at: datetime


def create_token(
    *, subject: str, token_type: TokenType, ttl_seconds: int, secret: str, algorithm: str
) -> tuple[str, TokenClaims]:
    issued_at = datetime.now(UTC).replace(microsecond=0)
    claims = TokenClaims(
        subject=subject,
        token_type=token_type,
        token_id=uuid.uuid4().hex,
        expire_at=issued_at + timedelta(seconds=ttl_seconds),
    )

    payload = {
        "sub": claims.subject,
        "type": claims.token_type,
        "jti": claims.token_id,
        "iat": issued_at,
        "exp": claims.expire_at,
    }
    return jwt.encode(payload, secret, algorithm=algorithm), claims


def decode_token(
    token: str,
    *,
    expected_type: TokenType,
    secret: str,
    algorithm: str,
) -> TokenClaims:
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[algorithm],
            options={"require": _REQUIRED_CLAIMS},
            leeway=timedelta(seconds=10),
        )
    except jwt.ExpiredSignatureError as e:
        raise InvalidTokenError("Token expired", code="TOKEN_EXPIRED") from e
    except jwt.PyJWTError as e:
        raise InvalidTokenError() from e

    if payload["type"] != expected_type:
        raise InvalidTokenError()

    try:
        return TokenClaims(
            subject=payload["sub"],
            token_type=expected_type,
            token_id=payload["jti"],
            expire_at=datetime.fromtimestamp(payload["exp"], UTC),
        )
    except (TypeError, ValueError, OverflowError, OSError) as e:
        raise InvalidTokenError() from e


def get_user_id_from_subject(subject: str) -> int:
    if subject[0] == "0" or not (subject.isascii() and subject.isdigit()):
        raise InvalidTokenError()
    return int(subject)
