import numpy as np

# =========================================================
# HISTORICAL VAR
# =========================================================


def historical_var(returns, confidence=0.95):

    percentile = (1 - confidence) * 100

    var = np.percentile(returns, percentile)

    return var


# =========================================================
# CONDITIONAL VAR
# =========================================================


def conditional_var(returns, confidence=0.95):

    var = historical_var(returns, confidence)

    cvar = returns[returns <= var].mean()

    return cvar
