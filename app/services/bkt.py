def update_bkt(prior: float, is_correct: bool, slip: float = 0.1, guess: float = 0.2, transit: float = 0.15) -> float:

    if prior < 0: prior = 0.0
    if prior > 1: prior = 1.0
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
    
    next_prior = posterior + (1 - posterior) * transit

    #clamp
    next_prior = max(0.0, min(1.0, next_prior))
    return next_prior