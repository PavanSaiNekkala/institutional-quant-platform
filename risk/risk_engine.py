import pandas as pd
import numpy as np

# =========================================================
# POSITION LIMIT CHECK
# =========================================================

def check_position_limits(

    weights,

    max_position=0.25
):

    breaches = weights[

        weights > max_position
    ]

    return breaches

# =========================================================
# VOLATILITY TARGETING
# =========================================================

def volatility_targeting(

    returns,

    target_vol=0.15
):

    realized_vol = (

        returns.std()

        * np.sqrt(252)
    )

    scaling_factor = (

        target_vol

        / realized_vol
    )

    return scaling_factor

# =========================================================
# DRAWDOWN CONTROL
# =========================================================

def drawdown_control(

    returns,

    threshold=-0.20
):

    cumulative = (

        (1 + returns)

        .cumprod()
    )

    peak = cumulative.cummax()

    drawdown = (

        cumulative - peak
    ) / peak

    breached = (

        drawdown.min()

        < threshold
    )

    return {

        "Max Drawdown":

            round(

                drawdown.min(),

                4
            ),

        "Threshold Breached":

            breached
    }

# =========================================================
# CORRELATION RISK
# =========================================================

def correlation_risk(

    returns_df
):

    corr = returns_df.corr()

    avg_corr = (

        corr.values.mean()
    )

    return {

        "Average Correlation":

            round(avg_corr, 4)
    }

# =========================================================
# FULL RISK REPORT
# =========================================================

def risk_report(

    weights,

    returns,

    returns_df
):

    position_breaches = (

        check_position_limits(
            weights
        )
    )

    vol_scaler = (

        volatility_targeting(
            returns
        )
    )

    dd = drawdown_control(

        returns
    )

    corr = correlation_risk(

        returns_df
    )

    report = {

        "Position Breaches":

            len(position_breaches),

        "Volatility Scaling":

            round(vol_scaler, 4),

        "Max Drawdown":

            dd["Max Drawdown"],

        "Drawdown Breach":

            dd["Threshold Breached"],

        "Average Correlation":

            corr["Average Correlation"]
    }

    return pd.DataFrame({

        "Metric":

            report.keys(),

        "Value":

            report.values()
    })