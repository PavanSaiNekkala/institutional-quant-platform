import numpy as np
import pandas as pd

# =========================================================
# REGIME DETECTION
# =========================================================


def detect_regime(returns):

    vol = returns.std()

    trend = returns.mean()

    if vol > 0.03:
        return "HIGH_VOL"

    elif trend > 0:
        return "BULL"

    else:
        return "BEAR"


# =========================================================
# AI ALLOCATION ENGINE
# =========================================================


def adaptive_weights(assets, returns):

    regime = detect_regime(returns)

    n = len(assets)

    # =====================================================
    # BULL REGIME
    # =====================================================

    if regime == "BULL":
        weights = np.random.dirichlet(np.ones(n) * 2)

    # =====================================================
    # HIGH VOL
    # =====================================================

    elif regime == "HIGH_VOL":
        weights = np.random.dirichlet(np.ones(n) * 0.5)

    # =====================================================
    # BEAR
    # =====================================================

    else:
        weights = np.random.dirichlet(np.ones(n))

    return pd.DataFrame({"Asset": assets, "Weight": weights}), regime


# =========================================================
# PORTFOLIO SUMMARY
# =========================================================


def portfolio_summary(allocation):

    allocation["Weight"] = allocation["Weight"] / allocation["Weight"].sum()

    allocation["Allocation %"] = (allocation["Weight"] * 100).round(2)

    return allocation
