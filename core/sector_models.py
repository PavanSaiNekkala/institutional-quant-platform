# =========================================================
# FILE: core/sector_models.py
# FINAL INSTITUTIONAL SECTOR ADAPTIVE ENGINE
# =========================================================

import numpy as np


# =========================================================
# SAFE VALUE HANDLER
# =========================================================

def safe(value, default=0):

    try:

        if value is None:
            return default

        if np.isnan(value):
            return default

        if np.isinf(value):
            return default

        return value

    except Exception:

        return default


# =========================================================
# NORMALIZATION
# =========================================================

def normalize(value, min_val=-1, max_val=1):

    value = safe(value)

    try:

        value = max(min(value, max_val), min_val)

        return value

    except Exception:

        return 0


# =========================================================
# BANKING MODEL
# =========================================================

def banking_model(m):

    score = (

        normalize(m["roe"]) * 0.25 +

        normalize(m["profit_margin"]) * 0.20 +

        normalize(m["revenue_growth"]) * 0.15 +

        normalize(m["sharpe"]) * 0.15 +

        normalize(m["momentum"]) * 0.10 +

        normalize(m["trend_strength"]) * 0.05 -

        normalize(m["debt_to_equity"]) * 0.05 -

        normalize(m["volatility"]) * 0.05
    )

    return score


# =========================================================
# INFORMATION TECHNOLOGY MODEL
# =========================================================

def it_model(m):

    score = (

        normalize(m["revenue_growth"]) * 0.30 +

        normalize(m["operating_margin"]) * 0.25 +

        normalize(m["roe"]) * 0.15 +

        normalize(m["momentum"]) * 0.10 +

        normalize(m["sharpe"]) * 0.10 +

        normalize(m["total_return"]) * 0.10
    )

    return score


# =========================================================
# PHARMA MODEL
# =========================================================

def pharma_model(m):

    score = (

        normalize(m["revenue_growth"]) * 0.20 +

        normalize(m["profit_margin"]) * 0.20 +

        normalize(m["roe"]) * 0.15 +

        normalize(m["sharpe"]) * 0.15 +

        normalize(m["momentum"]) * 0.10 +

        normalize(m["dividend_yield"]) * 0.10 -

        normalize(m["volatility"]) * 0.10
    )

    return score


# =========================================================
# FMCG MODEL
# =========================================================

def fmcg_model(m):

    score = (

        normalize(m["profit_margin"]) * 0.25 +

        normalize(m["dividend_yield"]) * 0.20 +

        normalize(m["roe"]) * 0.20 +

        normalize(m["sharpe"]) * 0.15 +

        normalize(m["momentum"]) * 0.10 +

        normalize(m["trend_strength"]) * 0.05 -

        normalize(m["volatility"]) * 0.05
    )

    return score


# =========================================================
# AUTOMOBILE MODEL
# =========================================================

def auto_model(m):

    score = (

        normalize(m["revenue_growth"]) * 0.25 +

        normalize(m["momentum"]) * 0.20 +

        normalize(m["total_return"]) * 0.15 +

        normalize(m["operating_margin"]) * 0.15 +

        normalize(m["sharpe"]) * 0.15 +

        normalize(m["trend_strength"]) * 0.10
    )

    return score


# =========================================================
# METALS & MINING MODEL
# =========================================================

def metals_model(m):

    score = (

        normalize(m["momentum"]) * 0.30 +

        normalize(m["total_return"]) * 0.20 +

        normalize(m["sharpe"]) * 0.20 +

        normalize(m["revenue_growth"]) * 0.10 +

        normalize(m["trend_strength"]) * 0.10 -

        normalize(m["volatility"]) * 0.10
    )

    return score


# =========================================================
# ENERGY MODEL
# =========================================================

def energy_model(m):

    score = (

        normalize(m["dividend_yield"]) * 0.20 +

        normalize(m["profit_margin"]) * 0.20 +

        normalize(m["roe"]) * 0.15 +

        normalize(m["momentum"]) * 0.15 +

        normalize(m["sharpe"]) * 0.15 +

        normalize(m["total_return"]) * 0.15
    )

    return score


# =========================================================
# REAL ESTATE MODEL
# =========================================================

def real_estate_model(m):

    score = (

        normalize(m["revenue_growth"]) * 0.20 +

        normalize(m["roe"]) * 0.20 +

        normalize(m["profit_margin"]) * 0.15 +

        normalize(m["momentum"]) * 0.15 +

        normalize(m["trend_strength"]) * 0.10 +

        normalize(m["total_return"]) * 0.10 -

        normalize(m["debt_to_equity"]) * 0.10
    )

    return score


# =========================================================
# TELECOM MODEL
# =========================================================

def telecom_model(m):

    score = (

        normalize(m["revenue_growth"]) * 0.25 +

        normalize(m["operating_margin"]) * 0.20 +

        normalize(m["roe"]) * 0.15 +

        normalize(m["momentum"]) * 0.15 +

        normalize(m["sharpe"]) * 0.10 +

        normalize(m["trend_strength"]) * 0.10 -

        normalize(m["volatility"]) * 0.05
    )

    return score


# =========================================================
# INFRASTRUCTURE MODEL
# =========================================================

def infra_model(m):

    score = (

        normalize(m["revenue_growth"]) * 0.20 +

        normalize(m["operating_margin"]) * 0.20 +

        normalize(m["momentum"]) * 0.20 +

        normalize(m["total_return"]) * 0.15 +

        normalize(m["trend_strength"]) * 0.15 +

        normalize(m["sharpe"]) * 0.10
    )

    return score


# =========================================================
# DEFAULT MODEL
# =========================================================

def default_model(m):

    score = (

        normalize(m["revenue_growth"]) * 0.15 +

        normalize(m["profit_margin"]) * 0.15 +

        normalize(m["roe"]) * 0.15 +

        normalize(m["momentum"]) * 0.15 +

        normalize(m["sharpe"]) * 0.10 +

        normalize(m["trend_strength"]) * 0.10 +

        normalize(m["total_return"]) * 0.10 +

        normalize(m["dividend_yield"]) * 0.05 -

        normalize(m["volatility"]) * 0.05
    )

    return score


# =========================================================
# SECTOR ROUTER
# =========================================================

def sector_score(sector, metrics):

    sector = str(sector).lower()

    # =====================================================
    # BANKING & FINANCIALS
    # =====================================================

    if (

        "bank" in sector or

        "financial" in sector or

        "insurance" in sector
    ):

        return banking_model(metrics)

    # =====================================================
    # INFORMATION TECHNOLOGY
    # =====================================================

    elif (

        "technology" in sector or

        "software" in sector or

        "it" in sector
    ):

        return it_model(metrics)

    # =====================================================
    # PHARMA & HEALTHCARE
    # =====================================================

    elif (

        "health" in sector or

        "pharma" in sector or

        "biotech" in sector
    ):

        return pharma_model(metrics)

    # =====================================================
    # FMCG & CONSUMER
    # =====================================================

    elif (

        "consumer" in sector or

        "fmcg" in sector or

        "staples" in sector
    ):

        return fmcg_model(metrics)

    # =====================================================
    # AUTOMOBILE
    # =====================================================

    elif (

        "auto" in sector or

        "vehicle" in sector
    ):

        return auto_model(metrics)

    # =====================================================
    # METALS & MINING
    # =====================================================

    elif (

        "metal" in sector or

        "mining" in sector or

        "steel" in sector
    ):

        return metals_model(metrics)

    # =====================================================
    # ENERGY
    # =====================================================

    elif (

        "energy" in sector or

        "oil" in sector or

        "gas" in sector
    ):

        return energy_model(metrics)

    # =====================================================
    # REAL ESTATE
    # =====================================================

    elif (

        "real estate" in sector or

        "realty" in sector or

        "property" in sector
    ):

        return real_estate_model(metrics)

    # =====================================================
    # TELECOM
    # =====================================================

    elif (

        "telecom" in sector or

        "communication" in sector
    ):

        return telecom_model(metrics)

    # =====================================================
    # INFRASTRUCTURE
    # =====================================================

    elif (

        "infra" in sector or

        "construction" in sector or

        "engineering" in sector
    ):

        return infra_model(metrics)

    # =====================================================
    # DEFAULT
    # =====================================================

    else:

        return default_model(metrics)