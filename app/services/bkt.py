def update_bkt(prior: float, is_correct: bool, slip: float, guess: float, transit: float) -> float:

    # if prior < 0: prior = 0.0
    # if prior > 1: prior = 1.0

    # NOTE : clamp input
    prior = max(0.0, min(1.0, prior))

    if is_correct:
        numerator = prior * (1 - slip)
        denominator = numerator + (1 - prior) * guess
    else:
        numerator = prior * slip
        denominator = numerator + (1 - prior) * (1 - guess)
    
    if denominator == 0:
        posterior = prior
    else:
        posterior = numerator / denominator
    
    # apply learning transition
    next_prior = posterior + (1 - posterior) * transit
    return max(0.0, min(1.0, next_prior))