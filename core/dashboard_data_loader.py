import pandas as pd

from pathlib import Path

# =========================================================
# EXPORT DIRECTORY
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

EXPORT_DIR = (

    ROOT_DIR

    / "cache"

    / "dashboard_exports"
)

# =========================================================
# LOAD PARQUET
# =========================================================

def load_parquet(

    filename
):

    filepath = (

        EXPORT_DIR

        / filename
    )

    if not filepath.exists():

        return pd.DataFrame()

    try:

        return pd.read_parquet(

            filepath
        )

    except Exception as e:

        print(

            f"LOAD ERROR: {e}"
        )

        return pd.DataFrame()

# =========================================================
# RANKED UNIVERSE
# =========================================================

def load_ranked_universe():

    return load_parquet(

        "ranked_universe.parquet"
    )

# =========================================================
# SIGNALS
# =========================================================

def load_signals():

    return load_parquet(

        "signals.parquet"
    )

# =========================================================
# PORTFOLIO ANALYTICS
# =========================================================

def load_portfolio_analytics():

    return load_parquet(

        "portfolio_analytics.parquet"
    )

# =========================================================
# EXPOSURE ANALYTICS
# =========================================================

def load_exposure_analytics():

    return load_parquet(

        "exposure_analytics.parquet"
    )

# =========================================================
# PNL ANALYTICS
# =========================================================

def load_pnl_analytics():

    return load_parquet(

        "pnl_analytics.parquet"
    )
