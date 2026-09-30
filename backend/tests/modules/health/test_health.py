from httpx import AsyncClient


async def test_health_ok(client: AsyncClient) -> None:
    r = await client.get("/health/live")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


async def test_ready_with_real_database(client: AsyncClient) -> None:
    r = await client.get("/health/ready")
    assert r.status_code == 200
    assert r.json() == {"status": "OK"}
