import pandas as pd
import numpy as np

# =========================================================
# COMMISSION COST
# =========================================================

def commission_cost(

    turnover,

    commission_rate=0.001
):

    return turnover * commission_rate

# =========================================================
# SLIPPAGE MODEL
# =========================================================

def slippage_cost(

    volatility,

    slippage_factor=0.05
):

    return volatility * slippage_factor

# =========================================================
# MARKET IMPACT
# =========================================================

def market_impact(

    position_size,

    avg_daily_volume
):

    impact = (

        position_size

        / avg_daily_volume
    )

    return impact * 0.10

# =========================================================
# TOTAL EXECUTION COST
# =========================================================

def total_execution_cost(

    turnover,

    volatility,

    position_size,

    avg_daily_volume
):

    commission = commission_cost(

        turnover
    )

    slippage = slippage_cost(

        volatility
    )

    impact = market_impact(

        position_size,

        avg_daily_volume
    )

    total_cost = (

        commission

        + slippage

        + impact
    )

    return {

        "Commission":

            round(commission, 6),

        "Slippage":

            round(slippage, 6),

        "Market Impact":

            round(impact, 6),

        "Total Cost":

            round(total_cost, 6)
    }

# =========================================================
# NET STRATEGY RETURNS
# =========================================================

def net_strategy_returns(

    gross_returns,

    execution_cost
):

    return (

        gross_returns

        - execution_cost
    )