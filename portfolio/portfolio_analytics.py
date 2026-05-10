import pandas as pd
import numpy as np

# =========================================================
# SHARPE RATIO
# =========================================================

def sharpe_ratio(

    returns,

    risk_free_rate=0.0
):

    excess = (

        returns - risk_free_rate
    )

    return (

        excess.mean()

        / excess.std()
    ) * np.sqrt(252)

# =========================================================
# MAX DRAWDOWN
# =========================================================

def max_drawdown(

    returns
):

    cumulative = (

        (1 + returns)

        .cumprod()
    )

    peak = cumulative.cummax()

    drawdown = (

        cumulative - peak
    ) / peak

    return drawdown.min()

# =========================================================
# VOLATILITY
# =========================================================

def annualized_volatility(

    returns
):

    return (

        returns.std()

        * np.sqrt(252)
    )

# =========================================================
# WIN RATE
# =========================================================

def win_rate(

    returns
):

    wins = (

        returns > 0
    ).sum()

    return wins / len(returns)

# =========================================================
# PORTFOLIO REPORT
# =========================================================

def portfolio_report(

    returns
):

    report = {

        "Sharpe Ratio":

            round(

                sharpe_ratio(returns),

                4
            ),

        "Max Drawdown":

            round(

                max_drawdown(returns),

                4
            ),

        "Annualized Volatility":

            round(

                annualized_volatility(
                    returns
                ),

                4
            ),

        "Win Rate":

            round(

                win_rate(returns),

                4
            ),

        "Total Return":

            round(

                (

                    (1 + returns)

                    .prod()

                    - 1
                ),

                4
            )
    }

    return pd.DataFrame({

        "Metric":

            report.keys(),

        "Value":

            report.values()
    })