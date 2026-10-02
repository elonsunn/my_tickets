from app.core.security import hash_password, verify_password


async def test_hash_verify_only_the_real_password() -> None:
    hashed = await hash_password("real password")
    assert "real" not in hashed
    assert not await verify_password("wrong password", hashed)
    assert await verify_password("real password", hashed)


async def test_same_password_get_different_hash_each_time() -> None:
    assert await hash_password("same") != await hash_password("same")
