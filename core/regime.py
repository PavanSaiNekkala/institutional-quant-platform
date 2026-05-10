import pandas as pd
import numpy as np

# =========================================================
# TREND REGIME
# =========================================================

def trend_regime(

    close,

    short_window=50,

    long_window=200
):

    short_ma = (

        close

        .rolling(short_window)

        .mean()
    )

    long_ma = (

        close

        .rolling(long_window)

        .mean()
    )

    regime = np.where(

        short_ma > long_ma,

        "BULL",

        "BEAR"
    )

    return pd.Series(

        regime,

        index=close.index
    )

# =========================================================
# VOLATILITY REGIME
# =========================================================

def volatility_regime(

    returns,

    window=20
):

    volatility = (

        returns

        .rolling(window)

        .std()

        * np.sqrt(252)
    )

    regime = []

    for vol in volatility:

        if np.isnan(vol):

            regime.append(np.nan)

        elif vol < 0.15:

            regime.append("LOW_VOL")

        elif vol < 0.30:

            regime.append("NORMAL_VOL")

        else:

            regime.append("HIGH_VOL")

    return pd.Series(

        regime,

        index=returns.index
    )

# =========================================================
# MARKET REGIME COMBINATION
# =========================================================

def combined_regime(

    close,

    returns
):

    trend = trend_regime(

        close
    )

    vol = volatility_regime(

        returns
    )

    combined = trend.astype(str) + "_" + vol.astype(str)

    return combined

# =========================================================
# REGIME ALLOCATION
# =========================================================

def regime_allocation(

    regime
):

    allocation_map = {

        "BULL_LOW_VOL": 1.50,

        "BULL_NORMAL_VOL": 1.20,

        "BULL_HIGH_VOL": 0.80,

        "BEAR_LOW_VOL": 0.70,

        "BEAR_NORMAL_VOL": 0.50,

        "BEAR_HIGH_VOL": 0.20
    }

    return allocation_map.get(

        regime,

        1.00
    )