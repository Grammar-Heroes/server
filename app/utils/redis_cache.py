import json
import logging
from collections.abc import Mapping
from typing import Any, Optional

from redis.asyncio import Redis

logger = logging.getLogger(__name__)

redis = Redis(host="localhost", port=6379, decode_responses=True)


def _cache_key(normalized: str, kc_id: Optional[int]) -> str:
    key = f"sentence_cache:{normalized}"
    if kc_id is not None:
        key = f"{key}:kc:{kc_id}"
    return key


async def get_sentence_cache(normalized: str, kc_id: Optional[int]):
    key = _cache_key(normalized, kc_id)
    data = await redis.get(key)
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

    await redis.set(key, value, ex=2592000)
    logger.info("[CACHE SET] %s", key)
