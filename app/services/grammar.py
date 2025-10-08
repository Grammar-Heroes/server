from __future__ import annotations

import difflib
import logging
import re
from functools import lru_cache
from typing import Dict, List, Optional, Sequence

from gramformer import Gramformer
import language_tool_python

from app.utils.normalize import normalize_sentence
from app.utils.redis_cache import get_sentence_cache, set_sentence_cache

logger = logging.getLogger("grammar_cache")

gf = Gramformer(models=1, use_gpu=False)
tool = language_tool_python.LanguageTool('en-US')

try:
    from transformers import pipeline
except ImportError:  # pragma: no cover - transformers may be unavailable in some envs
    pipeline = None  # type: ignore

ACCEPTABILITY_MODEL_ID = "textattack/roberta-base-CoLA"
SEMANTIC_MODEL_ID = "typeform/distilbert-base-uncased-mnli"

ACCEPTABILITY_THRESHOLD = 0.60
SEMANTIC_THRESHOLD = 0.02
KC_ALIGNMENT_THRESHOLD = 0.02

KC_DESCRIPTIONS: Dict[int, str] = {
    1: "Subject-Verb Agreement (Simple Present)",
    2: "Verb Tenses",
    3: "Pronoun Reference",
    4: "Basic Article Use",
    5: "Simple Sentence Word Order",
    6: "Plural Nouns",
    7: "Adjective Placement",
    8: "Prepositions of Place",
    9: "Prepositions of Time",
    10: "Coordinating Conjunctions",
    11: "Complex Sentence: Subordinating Conjunctions",
    12: "Modal Verbs (Can/Should/Must)",
    13: "Comparative Adjectives",
    14: "Superlative Adjectives",
    15: "Present Continuous",
    16: "Past Continuous",
    17: "Future Tense (Will)",
    18: "Conditional Sentences (Type 1)",
    19: "Passive Voice (Present)",
    20: "Passive Voice (Past)",
}


def _log_unavailable(component: str) -> None:
    logger.warning("%s checks are unavailable; falling back to basic grammar rules", component)


@lru_cache(maxsize=1)
def _get_acceptability_pipeline():
    if pipeline is None:
        _log_unavailable("Acceptability")
        return None
    return pipeline("text-classification", model=ACCEPTABILITY_MODEL_ID, device=-1)


@lru_cache(maxsize=1)
def _get_semantic_pipeline():
    if pipeline is None:
        _log_unavailable("Semantic plausibility")
        return None
    return pipeline("zero-shot-classification", model=SEMANTIC_MODEL_ID, device=-1)


def _compute_acceptability(sentence: str) -> Optional[float]:
    pipe = _get_acceptability_pipeline()
    if pipe is None:
        return None
    outputs = pipe(sentence, truncation=True)
    if not outputs:
        return None
    output = outputs[0]
    label = str(output.get("label", "")).lower()
    score = float(output.get("score", 0.0))
    if "acceptable" in label or label.endswith("1"):
        return score
    return 1.0 - score


def _compute_semantic_score(sentence: str) -> Optional[float]:
    pipe = _get_semantic_pipeline()
    if pipe is None:
        return None
    output = pipe(
        sentence,
        candidate_labels=["meaningful", "nonsense"],
        hypothesis_template="This sentence is {}."
    )
    if not output:
        return None
    labels: Sequence[str] = output.get("labels", [])
    scores: Sequence[float] = output.get("scores", [])
    scores_by_label = {label: score for label, score in zip(labels, scores)}
    return float(scores_by_label.get("meaningful") or scores_by_label.get("Meaningful") or 0.0)


def _compute_kc_alignment(sentence: str, kc_id: Optional[int]) -> Optional[float]:
    if kc_id is None:
        return None
    label = KC_DESCRIPTIONS.get(kc_id)
    if not label:
        return None
    pipe = _get_semantic_pipeline()
    if pipe is None:
        return None

    positive_label = f"correct usage of {label.lower()}"
    negative_label = f"incorrect usage of {label.lower()}"

    output = pipe(
        sentence,
        candidate_labels=[positive_label, negative_label],
        hypothesis_template="This sentence shows {}."
    )
    if not output:
        return None
    labels: Sequence[str] = output.get("labels", [])
    scores: Sequence[float] = output.get("scores", [])
    scores_by_label = {label: score for label, score in zip(labels, scores)}

    positive_score = float(scores_by_label.get(positive_label) or 0.0)
    negative_score = float(scores_by_label.get(negative_label) or 0.0)

    if negative_score >= positive_score:
        return 1.0 - negative_score
    return positive_score


def _format_language_tool_feedback(matches: List[language_tool_python.Match]) -> List[str]:
    feedback = []
    for match in matches:
        suggestions = ", ".join(match.replacements[:3]) if match.replacements else "(no suggestion)"
        feedback.append(f"{match.ruleId}: {match.message} Suggested: {suggestions}")
    return feedback


def _generate_candidates(sentence: str) -> List[str]:
    try:
        candidates = list(gf.correct(sentence, max_candidates=3))
    except TypeError:  # legacy gramformer signature
        candidates = list(gf.correct(sentence))
    cleaned: List[str] = []
    for candidate in candidates:
        cand = candidate.strip()
        if cand and cand not in cleaned:
            cleaned.append(cand)
    if sentence not in cleaned:
        cleaned.insert(0, sentence)
    return cleaned[:3]


def _candidate_sort_key(candidate: Dict[str, Optional[float]]) -> tuple:
    lt = candidate.get("language_tool_matches") or 0
    acceptability = candidate.get("acceptability")
    return (
        lt,
        -(acceptability if acceptability is not None else 0.0),
        len(candidate.get("text", "")),
    )


def _diff_sentences(original: str, corrected: str) -> tuple[List[int], List[str]]:
    if original == corrected:
        return [], []

    words_original = original.split()
    words_corrected = corrected.split()

    error_indices: List[int] = []
    feedback: List[str] = []
    matcher = difflib.SequenceMatcher(None, words_original, words_corrected)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        wrong = " ".join(words_original[i1:i2])
        right = " ".join(words_corrected[j1:j2])
        error_indices.extend(range(i1, i2))
        if right:
            feedback.append(f"Replace '{wrong}' with '{right}'")
        else:
            feedback.append(f"Remove '{wrong}'")

    return sorted(set(error_indices)), feedback


def _indices_from_matches(sentence: str, matches: List[language_tool_python.Match]) -> List[int]:
    if not matches or not sentence.strip():
        return []
    spans = list(re.finditer(r"\S+", sentence))
    if not spans:
        return []
    indices: set[int] = set()
    for match in matches:
        start = match.offset
        end = match.offset + match.errorLength
        for idx, span in enumerate(spans):
            if span.end() <= start or span.start() >= end:
                continue
            indices.add(idx)
    return sorted(indices)


def _kc_hint(kc_id: Optional[int]) -> Optional[str]:
    if kc_id is None:
        return None
    label = KC_DESCRIPTIONS.get(kc_id)
    if label:
        return label
    return None


async def check_sentence(sentence: str, kc_id: Optional[int] = None) -> Dict[str, object]:
    normalized = normalize_sentence(sentence)
    cached = await get_sentence_cache(normalized, kc_id)
    if cached:
        logger.info("[CACHE HIT] '%s'", normalized)
        cached["from_cache"] = True
        return cached

    logger.info("[CACHE MISS] '%s'", normalized)

    matches = tool.check(sentence)
    acceptability_score = _compute_acceptability(sentence)
    semantic_score = _compute_semantic_score(sentence)
    kc_alignment = _compute_kc_alignment(sentence, kc_id)

    candidates = _generate_candidates(sentence)
    candidate_details: List[Dict[str, object]] = []

    for candidate in candidates:
        if candidate == sentence:
            candidate_matches = matches
            candidate_acceptability = acceptability_score
        else:
            candidate_matches = tool.check(candidate)
            candidate_acceptability = _compute_acceptability(candidate)
        candidate_details.append({
            "text": candidate,
            "language_tool_matches": len(candidate_matches),
            "acceptability": candidate_acceptability,
        })

    best_candidate = min(candidate_details, key=_candidate_sort_key) if candidate_details else {
        "text": sentence,
        "language_tool_matches": len(matches),
        "acceptability": acceptability_score,
    }
    best_candidate_text = str(best_candidate.get("text", sentence))

    diff_indices, correction_feedback = _diff_sentences(sentence, best_candidate_text)

    is_correct = (
        (acceptability_score is None or acceptability_score >= ACCEPTABILITY_THRESHOLD)
        and (semantic_score is None or semantic_score >= SEMANTIC_THRESHOLD)
        and (kc_alignment is None or kc_alignment >= KC_ALIGNMENT_THRESHOLD)
    )

    threshold_feedback: List[str] = []
    if acceptability_score is not None and acceptability_score < ACCEPTABILITY_THRESHOLD:
        threshold_feedback.append(
            f"Acceptability score {acceptability_score:.2f} is below the threshold {ACCEPTABILITY_THRESHOLD:.2f}."
        )
    if semantic_score is not None and semantic_score < SEMANTIC_THRESHOLD:
        threshold_feedback.append(
            f"Semantic plausibility score {semantic_score:.2f} is below the guideline {SEMANTIC_THRESHOLD:.2f}."
        )
    if kc_alignment is not None and kc_alignment < KC_ALIGNMENT_THRESHOLD:
        label = _kc_hint(kc_id)
        if label:
            threshold_feedback.append(
                f"Knowledge component alignment for '{label}' is low ({kc_alignment:.2f} < {KC_ALIGNMENT_THRESHOLD:.2f})."
            )
        else:
            threshold_feedback.append(
                f"Knowledge component alignment score {kc_alignment:.2f} is below the threshold {KC_ALIGNMENT_THRESHOLD:.2f}."
            )

    lt_feedback = _format_language_tool_feedback(matches)

    feedback: List[str] = []
    if not is_correct:
        feedback.extend(correction_feedback)
    feedback.extend(lt_feedback)
    feedback.extend(threshold_feedback)

    diff_indices = diff_indices if not is_correct else []
    match_indices = _indices_from_matches(sentence, matches) if not is_correct else []
    error_indices = sorted(set(diff_indices + match_indices))

    result: Dict[str, object] = {
        "is_correct": is_correct,
        "error_indices": error_indices,
        "feedback": feedback,
        "scores": {
            "language_tool_matches": len(matches),
            "acceptability": acceptability_score,
            "semantic": semantic_score,
            "perplexity": None,
            "kc_alignment": kc_alignment,
        },
        "candidates": candidate_details,
        "best_candidate": best_candidate_text,
        "from_cache": False,
    }

    cache_payload = {k: v for k, v in result.items() if k != "from_cache"}
    await set_sentence_cache(normalized, kc_id, cache_payload)
    return result
