import json
import logging
from collections.abc import Mapping
from typing import Any, Optional
from os import getenv
from redis.asyncio import from_url as redis_from_url

logger = logging.getLogger(__name__)

# Read REDIS_URL from environment; fall back to localhost for local dev
REDIS_URL = getenv("REDIS_URL", "redis://localhost:6379")

# Create async Redis client from connection URL (works for redis:// or rediss://)
redis = redis_from_url(REDIS_URL, decode_responses=True)

def _cache_key(normalized: str, kc_id: Optional[int]) -> str:
    key = f"sentence_cache:{normalized}"
    if kc_id is not None:
        key = f"{key}:kc:{kc_id}"
    return key

async def get_sentence_cache(normalized: str, kc_id: Optional[int]):
    key = _cache_key(normalized, kc_id)
    try:
        data = await redis.get(key)
    except Exception as e:
        logger.error("Redis get failed for %s: %s", key, e)
        return None

    if data:
        try:
            cached = json.loads(data)
        except json.JSONDecodeError:
            logger.warning("Failed to decode cached payload for %s", key)
            return None
        logger.info("[CACHE HIT] %s", key)
        if isinstance(cached, Mapping):
            cached.setdefault("feedback", [])
            cached.setdefault("error_indices", [])
            cached.setdefault("is_correct", False)
        return cached
    logger.info("[CACHE MISS] %s", key)
    return None

async def set_sentence_cache(normalized: str, kc_id: Optional[int], payload: dict[str, Any]):
    key = _cache_key(normalized, kc_id)
    try:
        value = json.dumps(payload)
    except (TypeError, ValueError) as exc:
        logger.error("Failed to serialise payload for %s: %s", key, exc)
        return

    try:
        await redis.set(key, value, ex=2592000)  # 30 days TTL
        logger.info("[CACHE SET] %s", key)
    except Exception as e:
        logger.error("Redis set failed for %s: %s", key, e)
