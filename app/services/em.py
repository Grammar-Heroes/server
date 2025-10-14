# bkt_em.py
import math

EPS = 1e-9

def clamp(x, lo=1e-6, hi=1 - 1e-6):
    return max(lo, min(hi, x))


def forward_backward(seq, L0, T, S, G):
    """
    Standard forward-backward for BKT.
    seq: list of 0/1 (1 = correct)
    returns gamma (posterior per time), xi_0_to_1 (expected transitions)
    """
    n = len(seq)
    e_known = 1 - S
    e_unknown = G

    # Forward pass
    alpha = [None] * n
    pK, pU = L0, 1 - L0
    o = seq[0]
    alpha_known = pK * (e_known if o == 1 else (1 - e_known))
    alpha_unknown = pU * (e_unknown if o == 1 else (1 - e_unknown))
    norm = alpha_known + alpha_unknown + EPS
    alpha[0] = (alpha_unknown / norm, alpha_known / norm)

    for t in range(1, n):
        o = seq[t]
        prev_u, prev_k = alpha[t - 1]
        # transition model
        pred_u = prev_u * (1 - T)
        pred_k = prev_u * T + prev_k
        # emission
        emit_u = e_unknown if o == 1 else (1 - e_unknown)
        emit_k = e_known if o == 1 else (1 - e_known)
        a_u = pred_u * emit_u
        a_k = pred_k * emit_k
        s = a_u + a_k + EPS
        alpha[t] = (a_u / s, a_k / s)

    # Backward pass
    beta = [(1.0, 1.0)] * n
    for t in range(n - 2, -1, -1):
        o_next = seq[t + 1]
        b_next_u, b_next_k = beta[t + 1]
        emit_u = e_unknown if o_next == 1 else (1 - e_unknown)
        emit_k = e_known if o_next == 1 else (1 - e_known)
        val_u = (1 - T) * emit_u * b_next_u + T * emit_k * b_next_k
        val_k = emit_k * b_next_k
        s = val_u + val_k + EPS
        beta[t] = (val_u / s, val_k / s)

    # Smoothed marginals
    gamma = []
    for t in range(n):
        a_u, a_k = alpha[t]
        b_u, b_k = beta[t]
        g_u = a_u * b_u
        g_k = a_k * b_k
        s = g_u + g_k + EPS
        gamma.append((g_u / s, g_k / s))

    # Expected unknown→known transitions
    xi_0_to_1 = []
    for t in range(n - 1):
        a_u, a_k = alpha[t]
        b_next_u, b_next_k = beta[t + 1]
        o_next = seq[t + 1]
        emit_next_k = e_known if o_next == 1 else (1 - e_known)
        emit_next_u = e_unknown if o_next == 1 else (1 - e_unknown)
        num = a_u * T * emit_next_k * b_next_k
        val_00 = a_u * (1 - T) * emit_next_u * b_next_u
        val_01 = a_u * T * emit_next_k * b_next_k
        val_11 = a_k * emit_next_k * b_next_k
        denom = val_00 + val_01 + val_11 + EPS
        xi_0_to_1.append(num / denom)
    return gamma, xi_0_to_1


def em_fit_bkt(sequences, max_iters=100, tol=1e-5, verbose=False, init_params=None):
    """
    Fit BKT parameters (L0, T, S, G) using Expectation-Maximization.
    sequences: list of lists of 0/1 (1=correct)
    """
    if init_params is None:
        L0, T, S, G = 0.2, 0.1, 0.15, 0.25
    else:
        L0, T, S, G = init_params

    for it in range(max_iters):
        sum_gamma0 = sum_gamma = sum_gamma_incorrect = 0.0
        sum_one_minus_gamma = sum_one_minus_gamma_correct = 0.0
        sum_xi_0_to_1 = sum_expected_zero = 0.0
        nseq = 0

        for seq in sequences:
            if len(seq) == 0:
                continue
            nseq += 1
            gamma, xi = forward_backward(seq, L0, T, S, G)
            sum_gamma0 += gamma[0][1]
            for t, obs in enumerate(seq):
                g_u, g_k = gamma[t]
                sum_gamma += g_k
                if obs == 0:
                    sum_gamma_incorrect += g_k
                sum_one_minus_gamma += g_u
                if obs == 1:
                    sum_one_minus_gamma_correct += g_u
            sum_xi_0_to_1 += sum(xi)
            for t in range(len(seq) - 1):
                sum_expected_zero += (1 - gamma[t][1])

        if nseq == 0:
            raise ValueError("No valid sequences")

        new_L0 = sum_gamma0 / nseq
        new_T = sum_xi_0_to_1 / (sum_expected_zero + EPS)
        new_S = sum_gamma_incorrect / (sum_gamma + EPS)
        new_G = sum_one_minus_gamma_correct / (sum_one_minus_gamma + EPS)

        new_L0, new_T, new_S, new_G = map(clamp, (new_L0, new_T, new_S, new_G))
        diff = max(abs(new_L0 - L0), abs(new_T - T), abs(new_S - S), abs(new_G - G))

        L0, T, S, G = new_L0, new_T, new_S, new_G
        if verbose:
            print(f"[EM] iter {it:03d} L0={L0:.4f} T={T:.4f} S={S:.4f} G={G:.4f} Δ={diff:.6f}")
        if diff < tol:
            break

    return {"L0": L0, "T": T, "S": S, "G": G}