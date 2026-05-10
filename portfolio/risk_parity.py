import numpy as np

from pypfopt import (
    EfficientFrontier,
    risk_models,
    expected_returns
)

# =========================================================
# MAX SHARPE OPTIMIZATION
# =========================================================

def max_sharpe_allocation(price_data):

    # =====================================================
    # EXPECTED RETURNS
    # =====================================================

    mu = expected_returns.mean_historical_return(

        price_data
    )

    # =====================================================
    # COVARIANCE MATRIX
    # =====================================================

    S = risk_models.sample_cov(

        price_data
    )

    # =====================================================
    # OPTIMIZATION
    # =====================================================

    ef = EfficientFrontier(

        mu,

        S
    )

    weights = ef.max_sharpe()

    cleaned = ef.clean_weights()

    performance = ef.portfolio_performance()

    return (

        cleaned,

        performance
    )

# =========================================================
# MINIMUM VOLATILITY
# =========================================================

def min_volatility_allocation(price_data):

    mu = expected_returns.mean_historical_return(

        price_data
    )

    S = risk_models.sample_cov(

        price_data
    )

    ef = EfficientFrontier(

        mu,

        S
    )

    weights = ef.min_volatility()

    cleaned = ef.clean_weights()

    performance = ef.portfolio_performance()

    return (

        cleaned,

        performance
    )