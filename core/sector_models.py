# =========================================================
# FILE: core/sector_models.py
# FINAL FIXED VERSION
# =========================================================

import numpy as np

# =========================================================
# DEFAULT SECTOR WEIGHTS
# =========================================================

SECTOR_WEIGHTS = {

    "Technology": {

        "revenue_growth": 0.25,
        "profit_margin": 0.15,
        "roe": 0.15,
        "momentum": 0.20,
        "sharpe": 0.15,
        "trend_strength": 0.10
    },

    "Financial Services": {

        "roe": 0.30,
        "profit_margin": 0.20,
        "operating_margin": 0.15,
        "momentum": 0.15,
        "sharpe": 0.10,
        "dividend_yield": 0.10
    },

    "Healthcare": {

        "revenue_growth": 0.20,
        "profit_margin": 0.20,
        "roe": 0.20,
        "momentum": 0.15,
        "sharpe": 0.15,
        "trend_strength": 0.10
    },

    "Industrials": {

        "revenue_growth": 0.20,
        "operating_margin": 0.20,
        "roe": 0.20,
        "momentum": 0.15,
        "trend_strength": 0.15,
        "sharpe": 0.10
    },

    "Energy": {

        "profit_margin": 0.25,
        "dividend_yield": 0.20,
        "momentum": 0.15,
        "roe": 0.15,
        "operating_margin": 0.15,
        "sharpe": 0.10
    },

    "Consumer Defensive": {

        "profit_margin": 0.20,
        "dividend_yield": 0.20,
        "roe": 0.20,
        "momentum": 0.15,
        "sharpe": 0.15,
        "trend_strength": 0.10
    }
}

# =========================================================
# DEFAULT MODEL
# =========================================================

DEFAULT_WEIGHTS = {

    "revenue_growth": 0.15,
    "profit_margin": 0.15,
    "roe": 0.15,
    "operating_margin": 0.10,
    "momentum": 0.15,
    "sharpe": 0.10,
    "trend_strength": 0.10,
    "dividend_yield": 0.05,
    "debt_to_equity": -0.05
}

# =========================================================
# SAFE VALUE
# =========================================================

def safe_value(x):

    try:

        if x is None:
            return 0

        if np.isnan(x):
            return 0

        if np.isinf(x):
            return 0

        return float(x)

    except Exception:

        return 0

# =========================================================
# MAIN SCORING ENGINE
# =========================================================

def calculate_sector_score(
    sector,
    metrics
):

    try:

        weights = SECTOR_WEIGHTS.get(
            sector,
            DEFAULT_WEIGHTS
        )

        score = 0

        for factor, weight in weights.items():

            value = safe_value(
                metrics.get(factor, 0)
            )

            score += value * weight

        # =============================================
        # PENALIZE HIGH DEBT
        # =============================================

        debt = safe_value(
            metrics.get(
                "debt_to_equity",
                0
            )
        )

        if debt > 2:

            score *= 0.85

        # =============================================
        # BONUS FOR STRONG MOMENTUM
        # =============================================

        momentum = safe_value(
            metrics.get(
                "momentum",
                0
            )
        )

        if momentum > 0.20:

            score *= 1.10

        return round(score, 4)

    except Exception:

        return 0

# =========================================================
# BACKWARD COMPATIBILITY
# =========================================================

sector_score = calculate_sector_score
