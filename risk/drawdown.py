import pandas as pd

# =========================================================
# DRAWDOWN SERIES
# =========================================================

def calculate_drawdown(

    equity_curve
):

    rolling_max = (

        equity_curve.cummax()
    )

    drawdown = (

        equity_curve - rolling_max

    ) / rolling_max

    return drawdown

# =========================================================
# MAXIMUM DRAWDOWN
# =========================================================

def maximum_drawdown(

    equity_curve
):

    dd = calculate_drawdown(

        equity_curve
    )

    return dd.min()
# =========================================================
# ROLLING MAX DRAWDOWN
# =========================================================

def rolling_max_drawdown(

    equity_curve,

    window=252
):

    rolling_dd = []

    for i in range(window, len(equity_curve)):

        subset = equity_curve.iloc[

            i - window:i
        ]

        dd = maximum_drawdown(

            subset
        )

        rolling_dd.append(dd)

    return pd.Series(

        rolling_dd,

        index=equity_curve.index[window:]
    )

# =========================================================
# UNDERWATER CURVE
# =========================================================

def underwater_curve(

    equity_curve
):

    rolling_max = (

        equity_curve.cummax()
    )

    underwater = (

        equity_curve - rolling_max

    ) / rolling_max

    return underwater

# =========================================================
# RECOVERY TIME
# =========================================================

def recovery_time(

    equity_curve
):

    rolling_max = (

        equity_curve.cummax()
    )

    underwater = (

        equity_curve < rolling_max
    )

    recovery_periods = underwater.astype(int)

    return recovery_periods.sum()