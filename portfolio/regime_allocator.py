import pandas as pd
import numpy as np

# =========================================================
# DETECT REGIME
# =========================================================

def detect_regime(

    returns,

    volatility_threshold=0.02
):

    rolling_vol = (

        returns

        .rolling(20)

        .std()
    )

    latest_vol = rolling_vol.iloc[-1]

    mean_return = (

        returns

        .rolling(20)

        .mean()

        .iloc[-1]
    )

    # =====================================================
    # REGIME LOGIC
    # =====================================================

    if (

        latest_vol

        > volatility_threshold

        and mean_return < 0
    ):

        regime = "CRISIS"

    elif mean_return > 0:

        regime = "BULL"

    else:

        regime = "BEAR"

    return regime

# =========================================================
# ADAPTIVE ALLOCATION
# =========================================================

def adaptive_allocation(

    regime
):

    allocations = {

        "BULL": {

            "Equities": 0.70,

            "Cash": 0.10,

            "Defensive": 0.20
        },

        "BEAR": {

            "Equities": 0.30,

            "Cash": 0.40,

            "Defensive": 0.30
        },

        "CRISIS": {

            "Equities": 0.10,

            "Cash": 0.70,

            "Defensive": 0.20
        }
    }

    return allocations[regime]

# =========================================================
# REGIME REPORT
# =========================================================

def regime_report(

    returns
):

    regime = detect_regime(

        returns
    )

    allocation = adaptive_allocation(

        regime
    )

    report = pd.DataFrame({

        "Asset":

            allocation.keys(),

        "Weight":

            allocation.values()
    })

    return regime, report