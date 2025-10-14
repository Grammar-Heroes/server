# bkt.py
import math

def update_bkt(prior: float, is_correct: bool, slip: float, guess: float, transit: float) -> float:
    """
    Smoothed Bayesian Knowledge Tracing update.
    - Uses adaptive learning rate (transit scaled by (1 - prior)).
    - Penalizes wrong answers more, rewards correct ones less steeply.
    """

    # Clamp input to valid probability range
    prior = max(0.0, min(1.0, prior))

    # Observation likelihoods
    if is_correct:
        num = prior * (1 - slip)
        den = num + (1 - prior) * guess
    else:
        num = prior * slip
        den = num + (1 - prior) * (1 - guess)

    posterior = num / (den + 1e-9)

    # Adaptive transition:
    # - learning slows down when prior is already high
    # - small unlearning term when incorrect (to allow gentle decay)
    if is_correct:
        scaled_T = transit * (1 - prior)
        next_prior = posterior + (1 - posterior) * scaled_T
    else:
        # apply small forgetting when incorrect
        unlearn_rate = 0.05 + (0.15 * prior)
        next_prior = posterior * (1 - unlearn_rate)

    # Clamp again for safety
    return max(0.0, min(1.0, next_prior))