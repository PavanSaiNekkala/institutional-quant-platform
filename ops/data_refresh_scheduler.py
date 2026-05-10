import pandas as pd

from core.market_data_store import (
    save_market_data
)

# =========================================================
# LOAD SYMBOLS
# =========================================================

def load_symbols():

    try:

        universe = pd.read_excel(

            "valid_stocks.xlsx"
        )

        symbols = (

            universe.iloc[:, 0]

            .dropna()

            .astype(str)

            .unique()

            .tolist()
        )

        return symbols

    except:

        return []

# =========================================================
# REFRESH DATABASE
# =========================================================

def refresh_market_database(

    limit=100
):

    symbols = load_symbols()

    symbols = symbols[:limit]

    results = {

        "success": 0,

        "failed": 0
    }

    for symbol in symbols:

        success = save_market_data(

            symbol,

            period="6mo"
        )

        if success:

            results["success"] += 1

            print(

                f"UPDATED: {symbol}"
            )

        else:

            results["failed"] += 1

            print(

                f"FAILED: {symbol}"
            )

    return results