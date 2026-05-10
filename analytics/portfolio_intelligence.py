import numpy as np
import pandas as pd

# =========================================================
# MONTE CARLO SIMULATION
# =========================================================

def monte_carlo_simulation(

    returns,

    simulations=1000,

    horizon=252
):

    mean_return = returns.mean()

    volatility = returns.std()

    simulations_data = np.zeros(

        (horizon, simulations)
    )

    for sim in range(simulations):

        prices = [100]

        for _ in range(horizon):

            shock = np.random.normal(

                mean_return,

                volatility
            )

            prices.append(

                prices[-1]

                * (1 + shock)
            )

        simulations_data[:, sim] = prices[1:]

    return pd.DataFrame(

        simulations_data
    )

# =========================================================
# VALUE AT RISK
# =========================================================

def value_at_risk(

    returns,

    confidence=0.95
):

    percentile = (

        1 - confidence
    ) * 100

    return np.percentile(

        returns,

        percentile
    )

# =========================================================
# MAX DRAWDOWN
# =========================================================

def max_drawdown(

    equity_curve
):

    cumulative_max = (

        equity_curve.cummax()
    )

    drawdown = (

        equity_curve

        - cumulative_max
    ) / cumulative_max

    return drawdown.min()

# =========================================================
# STRESS TEST
# =========================================================

def stress_test(

    portfolio_value,

    shock=-0.20
):

    stressed_value = (

        portfolio_value

        * (1 + shock)
    )

    return stressed_value

# =========================================================
# PORTFOLIO REPORT
# =========================================================

def portfolio_report(

    returns
):

    mc = monte_carlo_simulation(

        returns
    )

    var = value_at_risk(

        returns
    )

    equity_curve = (

        (1 + returns)

        .cumprod()
    )

    dd = max_drawdown(

        equity_curve
    )

    stressed = stress_test(

        1_000_000
    )

    report = {

        "Value at Risk":

            round(var, 4),

        "Max Drawdown":

            round(dd, 4),

        "Stress Test Value":

            round(stressed, 2),

        "Monte Carlo Mean":

            round(

                mc.iloc[-1].mean(),

                2
            )
    }

    return report