from httpx import AsyncClient

from app.core.middleware import _REQUEST_ID_PATTERN, REQUEST_ID_HEADER


async def test_generate_request_id_when_missing(client: AsyncClient) -> None:
    resp = await client.get("/health/live")
    request_id = resp.headers.get(REQUEST_ID_HEADER)
    assert len(request_id) == 32


async def test_pass_id_if_have_in_request(client: AsyncClient) -> None:
    MOCK_ID = "mock-id-123"
    resp = await client.get(url="/health/live", headers={REQUEST_ID_HEADER: MOCK_ID})
    request_id = resp.headers.get(REQUEST_ID_HEADER)
    assert request_id == MOCK_ID


async def test_replaces_request_id_when_too_long(client: AsyncClient) -> None:
    resp = await client.get("/health/live", headers={"X-Request-ID": "x" * 200})

    assert resp.headers["X-Request-ID"] != "x" * 200
    assert len(resp.headers["X-Request-ID"]) == 32


async def test_replaces_request_id_when_invalid_sign(client: AsyncClient) -> None:
    resp = await client.get("/health/live", headers={"X-Request-ID": "x" * 200})

    assert resp.headers["X-Request-ID"] != "Invalid!@#$%^&*"
    assert len(resp.headers["X-Request-ID"]) == 32


def test_request_id_pattern() -> None:
    assert _REQUEST_ID_PATTERN.fullmatch("13c835e60de94ddaa066d0b0709fa5bb") is not None
    assert _REQUEST_ID_PATTERN.fullmatch("mockid") is not None
    assert _REQUEST_ID_PATTERN.fullmatch("") is None
    assert _REQUEST_ID_PATTERN.fullmatch("x" * 65) is None
