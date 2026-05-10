import pandas as pd
import numpy as np

# =========================================================
# ROLLING VOLATILITY
# =========================================================

def rolling_volatility(

    returns,

    window=60
):

    volatility = (

        returns

        .rolling(window)

        .std()

        * np.sqrt(252)
    )

    return volatility

# =========================================================
# ROLLING SHARPE RATIO
# =========================================================

def rolling_sharpe(

    returns,

    window=60,

    risk_free_rate=0
):

    rolling_return = (

        returns

        .rolling(window)

        .mean()

        * 252
    )

    rolling_vol = (

        returns

        .rolling(window)

        .std()

        * np.sqrt(252)
    )

    sharpe = (

        rolling_return - risk_free_rate

    ) / (rolling_vol + 1e-9)

    return sharpe

# =========================================================
# ROLLING CAGR
# =========================================================

def rolling_cagr(

    equity_curve,

    window=252
):

    cagr_list = []

    for i in range(window, len(equity_curve)):

        start = equity_curve.iloc[

            i - window
        ]

        end = equity_curve.iloc[i]

        cagr = (

            (end / start)

            ** (252 / window)

        ) - 1

        cagr_list.append(cagr)

    return pd.Series(

        cagr_list,

        index=equity_curve.index[window:]
    )

# =========================================================
# ROLLING RETURNS
# =========================================================

def rolling_returns(

    returns,

    window=21
):

    rr = (

        (1 + returns)

        .rolling(window)

        .apply(np.prod, raw=True)

    ) - 1

    return rr