import multiprocessing as mp
import pandas as pd
import numpy as np

from ai.orchestrator import (
    orchestrate_ai
)

# =========================================================
# PROCESS SINGLE ASSET
# =========================================================

def process_asset(

    symbol
):

    np.random.seed(

        abs(hash(symbol)) % 100000
    )

    prices = pd.Series(

        100

        + np.cumsum(

            np.random.normal(

                0,

                1,

                400
            )
        )
    )

    result = orchestrate_ai(

        prices
    )

    return {

        "Symbol":

            symbol,

        "Decision":

            result["Decision"],

        "Final Signal":

            result["Final Signal"]
    }

# =========================================================
# DISTRIBUTED PIPELINE
# =========================================================

def distributed_ai_pipeline(

    symbols,

    workers=4
):

    with mp.Pool(workers) as pool:

        results = pool.map(

            process_asset,

            symbols
        )

    return pd.DataFrame(

        results
    )