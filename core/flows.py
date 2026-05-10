import pandas as pd
import numpy as np

# =========================================================
# VOLUME Z-SCORE
# =========================================================

def volume_zscore(

    volume,

    window=20
):

    mean = (

        volume

        .rolling(window)

        .mean()
    )

    std = (

        volume

        .rolling(window)

        .std()
    )

    zscore = (

        volume - mean

    ) / (std + 1e-9)

    return zscore

# =========================================================
# ACCUMULATION DISTRIBUTION
# =========================================================

def accumulation_distribution(

    high,

    low,

    close,

    volume
):

    money_flow_multiplier = (

        ((close - low) - (high - close))

        /

        ((high - low) + 1e-9)
    )

    money_flow_volume = (

        money_flow_multiplier * volume
    )

    ad_line = money_flow_volume.cumsum()

    return ad_line

# =========================================================
# ON BALANCE VOLUME
# =========================================================

def on_balance_volume(

    close,

    volume
):

    direction = np.sign(

        close.diff()
    )

    obv = (

        direction * volume
    ).fillna(0).cumsum()

    return obv

# =========================================================
# FLOW MOMENTUM
# =========================================================

def flow_momentum(

    flow_series,

    window=20
):

    momentum = (

        flow_series.pct_change(window)
    )

    return momentum

# =========================================================
# SMART MONEY SCORE
# =========================================================

def smart_money_score(

    volume_z,

    ad_momentum,

    obv_momentum
):

    score = (

        0.4 * volume_z +

        0.3 * ad_momentum +

        0.3 * obv_momentum
    )

    return score

# =========================================================
# FLOW CLASSIFICATION
# =========================================================

def classify_flow(

    score
):

    if score > 2:

        return "HEAVY_ACCUMULATION"

    elif score > 1:

        return "ACCUMULATION"

    elif score > 0:

        return "NEUTRAL"

    return "DISTRIBUTION"