import pandas as pd
import numpy as np

# =========================================================
# MARKET CRASH
# =========================================================

def market_crash(

    portfolio,

    shock=-0.30
):

    stressed = portfolio.copy()

    stressed["Stressed Value"] = (

        stressed["Value"]

        * (1 + shock)
    )

    return stressed

# =========================================================
# VOLATILITY SHOCK
# =========================================================

def volatility_shock(

    returns,

    multiplier=2
):

    stressed_returns = (

        returns * multiplier
    )

    return stressed_returns

# =========================================================
# LIQUIDITY STRESS
# =========================================================

def liquidity_stress(

    portfolio,

    haircut=0.10
):

    stressed = portfolio.copy()

    stressed["Liquidity Adjusted"] = (

        stressed["Value"]

        * (1 - haircut)
    )

    return stressed

# =========================================================
# CORRELATION SHOCK
# =========================================================

def correlation_shock(

    corr_matrix,

    increase=0.20
):

    stressed_corr = (

        corr_matrix + increase
    )

    stressed_corr = stressed_corr.clip(

        upper=1
    )

    return stressed_corr

# =========================================================
# FULL STRESS REPORT
# =========================================================

def stress_report(

    portfolio,

    returns,

    corr_matrix
):

    crash = market_crash(

        portfolio
    )

    vol = volatility_shock(

        returns
    )

    liquidity = liquidity_stress(

        portfolio
    )

    corr = correlation_shock(

        corr_matrix
    )

    report = {

        "Crash Portfolio Value":

            round(

                crash["Stressed Value"]

                .sum(),

                2
            ),

        "Volatility Shock Std":

            round(

                vol.std(),

                4
            ),

        "Liquidity Adjusted Value":

            round(

                liquidity["Liquidity Adjusted"]

                .sum(),

                2
            ),

        "Average Correlation":

            round(

                corr.mean().mean(),

                4
            )
    }

    return report