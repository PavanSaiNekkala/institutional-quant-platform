import pandas as pd
import numpy as np

# =========================================================
# FACTOR ENGINEERING
# =========================================================

def build_factor(

    prices
):

    returns = prices.pct_change()

    factor = (

        prices

        / prices.shift(20)
    )

    future_return = (

        returns.shift(-1)
    )

    df = pd.DataFrame({

        "factor":

            factor,

        "future_return":

            future_return
    })

    return df.dropna()

# =========================================================
# ROLLING IC
# =========================================================

def rolling_information_coefficient(

    df,

    window=50
):

    ic_values = []

    for i in range(

        window,

        len(df)
    ):

        subset = df.iloc[

            i-window:i
        ]

        ic = subset["factor"].corr(

            subset["future_return"]
        )

        ic_values.append(ic)

    return pd.Series(

        ic_values
    )

# =========================================================
# DECAY ANALYSIS
# =========================================================

def alpha_decay_analysis(

    prices
):

    df = build_factor(

        prices
    )

    ic_series = rolling_information_coefficient(

        df
    )

    report = {

        "Average IC":

            round(

                ic_series.mean(),

                4
            ),

        "IC Volatility":

            round(

                ic_series.std(),

                4
            ),

        "Best IC":

            round(

                ic_series.max(),

                4
            ),

        "Worst IC":

            round(

                ic_series.min(),

                4
            ),

        "Recent IC":

            round(

                ic_series.iloc[-1],

                4
            )
    }

    return report, ic_series