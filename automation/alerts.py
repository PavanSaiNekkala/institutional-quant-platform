import pandas as pd
import numpy as np

# =========================================================
# PRICE BREAKOUT
# =========================================================

def breakout_alert(

    close,

    window=20
):

    resistance = (

        close

        .rolling(window)

        .max()
    )

    latest_close = close.iloc[-1]

    latest_resistance = resistance.iloc[-2]

    if latest_close > latest_resistance:

        return True

    return False

# =========================================================
# VOLUME SPIKE
# =========================================================

def volume_spike_alert(

    volume,

    threshold=2.0,

    window=20
):

    mean_volume = (

        volume

        .rolling(window)

        .mean()
    )

    std_volume = (

        volume

        .rolling(window)

        .std()
    )

    zscore = (

        volume.iloc[-1]

        - mean_volume.iloc[-1]

    ) / (std_volume.iloc[-1] + 1e-9)

    return zscore > threshold

# =========================================================
# VOLATILITY ALERT
# =========================================================

def volatility_alert(

    returns,

    threshold=0.04,

    window=20
):

    realized_vol = (

        returns

        .rolling(window)

        .std()
    )

    latest_vol = realized_vol.iloc[-1]

    return latest_vol > threshold

# =========================================================
# DRAWDOWN ALERT
# =========================================================

def drawdown_alert(

    equity_curve,

    threshold=-0.10
):

    rolling_max = (

        equity_curve.cummax()
    )

    drawdown = (

        equity_curve - rolling_max

    ) / rolling_max

    latest_dd = drawdown.iloc[-1]

    return latest_dd < threshold

# =========================================================
# INSTITUTIONAL ALERT SUMMARY
# =========================================================

def institutional_alerts(

    close,

    volume,

    returns,

    equity_curve
):

    alerts = {

        "Breakout":

            breakout_alert(close),

        "Volume Spike":

            volume_spike_alert(volume),

        "Volatility Risk":

            volatility_alert(returns),

        "Drawdown Risk":

            drawdown_alert(equity_curve)
    }

    return alerts