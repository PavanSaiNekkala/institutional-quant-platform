import pandas as pd
import numpy as np
import time

# =========================================================
# TWAP EXECUTION
# =========================================================

def twap_execution(

    broker,

    symbol,

    total_quantity,

    intervals=5,

    delay=1
):

    slice_qty = int(

        total_quantity / intervals
    )

    executions = []

    for i in range(intervals):

        result = broker.place_order(

            symbol,

            slice_qty,

            "BUY"
        )

        result["slice"] = i + 1

        result["strategy"] = "TWAP"

        executions.append(result)

        time.sleep(delay)

    return pd.DataFrame(

        executions
    )

# =========================================================
# VWAP EXECUTION
# =========================================================

def vwap_execution(

    broker,

    symbol,

    total_quantity,

    volume_profile
):

    executions = []

    volume_profile = (

        np.array(volume_profile)

        / np.sum(volume_profile)
    )

    quantities = (

        volume_profile

        * total_quantity
    ).astype(int)

    for i, qty in enumerate(quantities):

        result = broker.place_order(

            symbol,

            int(qty),

            "BUY"
        )

        result["slice"] = i + 1

        result["strategy"] = "VWAP"

        executions.append(result)

    return pd.DataFrame(

        executions
    )

# =========================================================
# ADAPTIVE EXECUTION
# =========================================================

def adaptive_execution(

    broker,

    symbol,

    quantity,

    volatility
):

    if volatility > 0.03:

        return twap_execution(

            broker,

            symbol,

            quantity,

            intervals=10,

            delay=0.5
        )

    else:

        profile = [

            0.10,
            0.15,
            0.20,
            0.25,
            0.20,
            0.10
        ]

        return vwap_execution(

            broker,

            symbol,

            quantity,

            profile
        )