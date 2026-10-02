from fastapi.concurrency import run_in_threadpool
from pwdlib import PasswordHash


async def hash_password(password: str) -> str:
    return await run_in_threadpool(PasswordHash.recommended().hash, password)


async def verify_password(password: str, hashed_password: str) -> bool:
    return await run_in_threadpool(
        PasswordHash.recommended().verify, password, hashed_password
    )
