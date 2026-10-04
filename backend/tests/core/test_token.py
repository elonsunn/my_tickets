import time
from typing import Any

import pytest

from app.core.exceptions import InvalidTokenError
from app.core.security import TokenClaims, create_token, decode_token

SECRET = "S" * 32
ALGO = "HS256"


def _create(**override: Any) -> tuple[str, TokenClaims]:  # noqa: ANN401
    kw: dict[str, Any] = {
        "subject": "00",
        "token_type": "access",
        "ttl_seconds": 30,
        "secret": SECRET,
        "algorithm": ALGO,
    }

    kw.update(override)
    return create_token(**kw)


def _decode(token: str, **overrides: Any) -> TokenClaims:  # noqa: ANN401
    kw: dict[str, Any] = {"expected_type": "access", "secret": SECRET, "algorithm": ALGO}
    kw.update(overrides)
    return decode_token(token, **kw)


def test_token_create_decode() -> None:
    token, claims = _create()

    assert _decode(token) == claims
    assert claims.subject == "00"
    assert claims.token_type == "access"


def test_token_get_unique_id() -> None:
    token1, claims1 = _create()
    token2, claims2 = _create()

    assert claims1.token_id != claims2.token_id
    assert _decode(token1).subject == _decode(token2).subject


def test_expired_token_is_rejected() -> None:
    token, _ = _create(ttl_seconds=1)

    time.sleep(1)
    with pytest.raises(InvalidTokenError) as e:
        _decode(token)
    assert e.value.code == "TOKEN_EXPIRED"


def test_refresh_token_cannot_be_used_as_access_token() -> None:
    token, _ = _create(token_type="refresh")

    with pytest.raises(InvalidTokenError) as e:
        _decode(token)
    assert e.value.code == "INVALID_TOKEN"


def test_decode_with_wrong_secret_is_rejected() -> None:
    token, _ = _create(secret="t" * 32)

    with pytest.raises(InvalidTokenError):
        _decode(token)
