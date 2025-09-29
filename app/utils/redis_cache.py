import json
import logging
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

redis = Redis(host="localhost", port=6379, decode_responses=True)

async def get_sentence_cache(normalized: str):
    key = f"sentence_cache:{normalized}"
    data = await redis.get(key)
    if data:
        logger.info(f"[CACHE HIT] {key}")
        return json.loads(data)
    logger.info(f"[CACHE MISS] {key}")
    return None

async def set_sentence_cache(normalized: str, is_correct: bool, error_indices: list[int], feedback: list[str]):
    key = f"sentence_cache:{normalized}"
    value = json.dumps({
        "is_correct": is_correct,
        "error_indices": error_indices,
        "feedback": feedback
    })

    await redis.set(key, value, ex=2592000)
    logger.info(f"[CACHE SET] {key}")