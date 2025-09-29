from typing import Dict, List
import difflib

from app.utils.normalize import normalize_sentence
from app.utils.redis_cache import get_sentence_cache, set_sentence_cache

from gramformer import Gramformer
import language_tool_python

import logging

logger = logging.getLogger("grammar_cache")

gf = Gramformer(models=1, use_gpu=False)
tool = language_tool_python.LanguageTool('en-US')

async def check_sentence(sentence: str) -> Dict[str, bool | List[int] | List[str] | bool]:
    normalized = normalize_sentence(sentence)
    cached = await get_sentence_cache(normalized)
    if cached:
        logger.info(f"[CACHE HIT] '{normalized}'")
        cached["from_cache"] = True  # flag
        return cached

    logger.info(f"[CACHE MISS] '{normalized}'")
    
    corrected_candidates = list(gf.correct(sentence))
    corrected_sentence = corrected_candidates[0] if corrected_candidates else sentence

    words_original = sentence.split()
    words_corrected = corrected_sentence.split()

    if words_original == words_corrected:
        result = {
            "is_correct": True,
            "error_indices": [],
            "feedback": [],
            "from_cache": False
        }
        await set_sentence_cache(normalized, result["is_correct"], result["error_indices"], result["feedback"])
        return result

    error_indices = []
    feedback = []
    matcher = difflib.SequenceMatcher(None, words_original, words_corrected)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            wrong = " ".join(words_original[i1:i2])
            right = " ".join(words_corrected[j1:j2])
            error_indices.extend(range(i1, i2))
            feedback.append(f"Replace '{wrong}' with '{right}'")

    matches = tool.check(sentence)
    for match in matches:
        feedback.append(f"{match.ruleId}: {match.message}")

    result = {
        "is_correct": False,
        "error_indices": list(set(error_indices)),
        "feedback": feedback,
        "from_cache": False
    }
    await set_sentence_cache(normalized, result["is_correct"], result["error_indices"], result["feedback"])
    return result