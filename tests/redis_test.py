import asyncio
from redis.asyncio import Redis

async def test():
    r = Redis(host="localhost", port=6379, decode_responses=True)
    await r.set("test-key", "123")
    val = await r.get("test-key")
    print("Value from Redis:", val)

asyncio.run(test())