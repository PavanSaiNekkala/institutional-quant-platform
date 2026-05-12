import pandas as pd

from pathlib import Path

# =========================================================
# ROOT DIRECTORY
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

# =========================================================
# EXPORT DIRECTORY
# =========================================================

EXPORT_DIR = (

    ROOT_DIR

    / "cache"

    / "dashboard_exports"
)

# =========================================================
# EXCEL FILES
# =========================================================

RANKED_EXCEL = (

    ROOT_DIR

    / "ranked_universe.xlsx"
)

FAILED_EXCEL = (

    ROOT_DIR

    / "failed_stocks.xlsx"
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

        print(

            f"PARQUET FILE "
            f"NOT FOUND: {filepath}"
        )

        return pd.DataFrame()

    try:

        df = pd.read_parquet(

            filepath
        )

        print(

            f"LOADED PARQUET: "
            f"{filename} | "
            f"ROWS: {len(df)}"
        )

        return df

    except Exception as e:

        print(

            f"PARQUET LOAD ERROR: {e}"
        )

        return pd.DataFrame()

# =========================================================
# LOAD EXCEL
# =========================================================

def load_excel(

    filepath
):

    if not filepath.exists():

        print(

            f"EXCEL FILE "
            f"NOT FOUND: {filepath}"
        )

        return pd.DataFrame()

    try:

        df = pd.read_excel(

            filepath
        )

        print(

            f"LOADED EXCEL: "
            f"{filepath.name} | "
            f"ROWS: {len(df)}"
        )

        return df

    except Exception as e:

        print(

            f"EXCEL LOAD ERROR: {e}"
        )

        return pd.DataFrame()

# =========================================================
# RANKED UNIVERSE
# =========================================================

def load_ranked_universe():

    # =============================================
    # PRIORITY 1 → PARQUET
    # =============================================

    parquet_df = load_parquet(

        "ranked_universe.parquet"
    )

    if not parquet_df.empty:

        return parquet_df

    # =============================================
    # PRIORITY 2 → EXCEL FALLBACK
    # =============================================

    return load_excel(

        RANKED_EXCEL
    )

# =========================================================
# FAILED STOCKS
# =========================================================

def load_failed_stocks():

    return load_excel(

        FAILED_EXCEL
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
