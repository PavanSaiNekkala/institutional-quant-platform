# =========================================================
# VOLATILITY INDEX REGIME
# =========================================================


def volatility_environment(vix_value):

    if vix_value < 12:
        return "LOW_RISK"

    elif vix_value < 20:
        return "NORMAL_RISK"

    elif vix_value < 30:
        return "HIGH_RISK"

    return "PANIC"


# =========================================================
# INTEREST RATE REGIME
# =========================================================


def interest_rate_regime(rate_change):

    if rate_change > 1:
        return "AGGRESSIVE_HIKING"

    elif rate_change > 0:
        return "TIGHTENING"

    elif rate_change < -1:
        return "AGGRESSIVE_EASING"

    return "EASING"


# =========================================================
# LIQUIDITY REGIME
# =========================================================


def liquidity_regime(market_return, breadth_score):

    if market_return > 0.15 and breadth_score > 1:
        return "STRONG_LIQUIDITY"

    elif market_return > 0:
        return "NORMAL_LIQUIDITY"

    return "WEAK_LIQUIDITY"


# =========================================================
# MACRO COMPOSITE
# =========================================================


def macro_composite(vol_regime, rate_regime, liquidity_regime_value):

    return f"{vol_regime}_{rate_regime}_{liquidity_regime_value}"


# =========================================================
# MACRO ALLOCATION
# =========================================================


def macro_allocation(macro_regime):

    if "PANIC" in macro_regime:
        return 0.30

    if "HIGH_RISK" in macro_regime:
        return 0.60

    if "LOW_RISK" in macro_regime:
        return 1.30

    return 1.00
