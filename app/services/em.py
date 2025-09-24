# bkt_em.py
import math
import random

EPS = 1e-9

def clamp(x, lo=1e-6, hi=1-1e-6):
    return max(lo, min(hi, x))

def forward_backward(seq, L0, T, S, G):
    """
    seq: list of 0/1 ints (1=correct)
    returns: alpha, beta, gamma, xi_sum_terms
    - gamma[t] = P(L_t = 1 | seq, params)
    - xi_terms for t=1..T-1: expected prob of (L_t=0 -> L_{t+1}=1)
    """
    Tlen = len(seq)
    # emission probabilities
    # P(C=1 | state)
    e1 = 1 - S  # if known
    e0 = G      # if unknown

    # Forward (alpha)
    # to avoid underflow, 'wag i-normalize
    # we will normalize explicitly
    alpha = [None] * Tlen
    # t = 0 initial
    p_known = L0
    p_unknown = 1 - L0
    obs = seq[0]
    alpha0_known = p_known * (e1 if obs == 1 else (1 - e1))
    alpha0_unknown = p_unknown * (e0 if obs == 1 else (1 - e0))
    norm0 = alpha0_known + alpha0_unknown + EPS
    alpha[0] = (alpha0_unknown / norm0, alpha0_known / norm0)  # (P(state=0|o1 upto norm), P(state=1|...))

    # Forward recursion
    for t in range(1, Tlen):
        obs = seq[t]
        prev_u, prev_k = alpha[t-1]
        # transition model:
        # from unknown: P(0->0) = 1-T, P(0->1) = T
        # from known:    P(1->1) = 1, P(1->0) = 0 (classic BKT: known is absorbing)
        # But sometimes implementations allow known->known = 1 (as above)
        # Predict state marginals:
        pred_unknown = prev_u * (1 - T)  # only from prev unknown
        pred_known = prev_u * T + prev_k * 1.0
        # emit
        emit_u = e0 if obs == 1 else (1 - e0)
        emit_k = e1 if obs == 1 else (1 - e1)
        a_u = pred_unknown * emit_u
        a_k = pred_known * emit_k
        denom = a_u + a_k + EPS
        alpha[t] = (a_u / denom, a_k / denom)

    # Backward (beta) - compute P(obs_{t+1:T} | state_t)
    beta = [None] * Tlen
    beta[-1] = (1.0, 1.0)
    for t in range(Tlen - 2, -1, -1):
        obs_next = seq[t+1]
        # for state=0 at time t:
        # contributions: (0->0)*(emit_next|0)*beta_{t+1}(0) + (0->1)*(emit_next|1)*beta_{t+1}(1)
        b_next_u, b_next_k = beta[t+1]
        emit_next_u = e0 if obs_next == 1 else (1 - e0)
        emit_next_k = e1 if obs_next == 1 else (1 - e1)
        val_u = (1 - T) * emit_next_u * b_next_u + T * emit_next_k * b_next_k
        # for state=1 at time t:
        # (1->1)*(emit_next|1)*beta_{t+1}(1)  (1->0 is zero)
        val_k = 1.0 * emit_next_k * b_next_k
        # normalize (not strictly necessary for beta alone)
        s = val_u + val_k + EPS
        beta[t] = (val_u / s, val_k / s)

    # gamma: combine alpha (filtered) and beta (smoothed)
    gamma = [None] * Tlen
    for t in range(Tlen):
        a_u, a_k = alpha[t]
        b_u, b_k = beta[t]
        g_u = a_u * b_u
        g_k = a_k * b_k
        s = g_u + g_k + EPS
        gamma[t] = (g_u / s, g_k / s)

    # xi for unknown->known expected counts
    xi_0_to_1 = [0.0] * (Tlen - 1)
    for t in range(Tlen - 1):
        # P(L_t=0, L_{t+1}=1 | seq) proportional to:
        # alpha_t(0) * P(0->1) * P(obs_{t+1}|1) * beta_{t+1}(1)
        a_u, a_k = alpha[t]
        b_next_u, b_next_k = beta[t+1]
        obs_next = seq[t+1]
        emit_next_k = e1 if obs_next == 1 else (1 - e1)
        numer = a_u * T * emit_next_k * b_next_k
        # compute normalization using sum over all joint transitions:
        # transitions:
        # 0->0, 0->1, 1->1
        emit_next_u = e0 if obs_next == 1 else (1 - e0)
        val_00 = a_u * (1 - T) * emit_next_u * b_next_u
        val_01 = a_u * T * emit_next_k * b_next_k
        val_11 = a_k * 1.0 * emit_next_k * b_next_k
        denom = val_00 + val_01 + val_11 + EPS
        xi_0_to_1[t] = val_01 / denom
    return gamma, xi_0_to_1

def em_fit_bkt(sequences, max_iters=100, tol=1e-5, verbose=False, init_params=None):
    # sequences: list of lists of 0/1
    # init
    if init_params is None:
        L0 = 0.2
        T = 0.2
        S = 0.1
        G = 0.2
    else:
        L0, T, S, G = init_params

    for it in range(max_iters):
        # E-step accumulators
        sum_gamma_first = 0.0
        sum_gamma = 0.0
        sum_gamma_incorrect = 0.0
        sum_1_minus_gamma = 0.0
        sum_1_minus_gamma_correct = 0.0
        sum_xi_0_to_1 = 0.0
        sum_expected_zeros = 0.0
        num_seqs = 0

        for seq in sequences:
            if len(seq) == 0:
                continue
            num_seqs += 1
            gamma, xi_0_to_1 = forward_backward(seq, L0, T, S, G)
            # first gamma for L0
            sum_gamma_first += gamma[0][1]  # prob known at t=0
            for t, obs in enumerate(seq):
                g_u, g_k = gamma[t]
                sum_gamma += g_k
                if obs == 0:
                    sum_gamma_incorrect += g_k
                sum_1_minus_gamma += g_u
                if obs == 1:
                    sum_1_minus_gamma_correct += g_u
            # transitions: xi over all t
            for xi in xi_0_to_1:
                sum_xi_0_to_1 += xi
            # expected times in 0 at t=1..T-1
            # we'll use sum of (1 - gamma[t]) for t=0..T-2 as denominator for T updates
            for t in range(len(seq)-1):
                sum_expected_zeros += (1 - gamma[t][1])

        # M-step estimates
        if num_seqs == 0:
            raise ValueError("No sequences provided")
        new_L0 = sum_gamma_first / num_seqs
        # T = expected # 0->1 transitions / expected # times in 0 at t=1..T-1
        new_T = sum_xi_0_to_1 / (sum_expected_zeros + EPS)
        # S = expected incorrect when known / expected times known
        new_S = sum_gamma_incorrect / (sum_gamma + EPS)
        # G = expected correct when unknown / expected times unknown
        new_G = sum_1_minus_gamma_correct / (sum_1_minus_gamma + EPS)

        # clamp
        new_L0, new_T, new_S, new_G = map(clamp, (new_L0, new_T, new_S, new_G))
        # check convergence
        diff = max(abs(new_L0 - L0), abs(new_T - T), abs(new_S - S), abs(new_G - G))
        L0, T, S, G = new_L0, new_T, new_S, new_G
        if verbose:
            print(f"iter {it:03d}: L0={L0:.5f} T={T:.5f} S={S:.5f} G={G:.5f} diff={diff:.6f}")
        if diff < tol:
            break
    return {"L0": L0, "T": T, "S": S, "G": G}