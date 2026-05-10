import yfinance as yf
import pandas as pd

from pathlib import Path

# =========================================================
# CACHE DIRECTORY
# =========================================================

CACHE_DIR = Path(

    "cache/market_data"
)

CACHE_DIR.mkdir(

    parents=True,

    exist_ok=True
)

# =========================================================
# MARKET DATA CACHE
# =========================================================

class MarketDataCache:

    def __init__(self):

        pass

    # =====================================================
    # CACHE PATH
    # =====================================================

    def cache_path(

        self,

        symbol
    ):

        safe_symbol = (

            symbol

            .replace("^", "")

            .replace("/", "_")
        )

        return CACHE_DIR / f"{safe_symbol}.parquet"

    # =====================================================
    # LOAD CACHE
    # =====================================================

    def load_cache(

        self,

        symbol
    ):

        path = self.cache_path(

            symbol
        )

        if path.exists():

            try:

                return pd.read_parquet(path)

            except:

                return None

        return None

    # =====================================================
    # SAVE CACHE
    # =====================================================

    def save_cache(

        self,

        symbol,

        data
    ):

        path = self.cache_path(

            symbol
        )

        try:

            data.to_parquet(path)

        except:

            pass

    # =====================================================
    # GET MARKET DATA
    # =====================================================

    def get_data(

        self,

        symbol,

        period="1y",

        refresh=False
    ):

        # =================================================
        # LOAD EXISTING CACHE
        # =================================================

        if not refresh:

            cached = self.load_cache(

                symbol
            )

            if cached is not None:

                return cached

        # =================================================
        # DOWNLOAD NEW DATA
        # =================================================

        try:

            data = yf.download(

                symbol,

                period=period,

                progress=False,

                auto_adjust=True
            )

            if data.empty:

                return pd.DataFrame()

            self.save_cache(

                symbol,

                data
            )

            return data

        except:

            return pd.DataFrame()