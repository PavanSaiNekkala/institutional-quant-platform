import pandas as pd

from pathlib import Path
from datetime import datetime, timedelta

# =========================================================
# REFRESH ENGINE
# =========================================================

class IncrementalRefreshEngine:

    def __init__(

        self,

        cache_dir="cache/market_data",

        refresh_hours=24
    ):

        self.cache_dir = Path(

            cache_dir
        )

        self.refresh_hours = refresh_hours

    # =====================================================
    # CACHE FILE
    # =====================================================

    def cache_file(

        self,

        symbol
    ):

        safe_symbol = (

            symbol

            .replace("^", "")

            .replace("/", "_")
        )

        return (

            self.cache_dir

            / f"{safe_symbol}.parquet"
        )

    # =====================================================
    # NEEDS REFRESH
    # =====================================================

    def needs_refresh(

        self,

        symbol
    ):

        filepath = self.cache_file(

            symbol
        )

        # =================================================
        # FILE MISSING
        # =================================================

        if not filepath.exists():

            return True

        # =================================================
        # CHECK AGE
        # =================================================

        modified_time = datetime.fromtimestamp(

            filepath.stat().st_mtime
        )

        age = datetime.now() - modified_time

        return age > timedelta(

            hours=self.refresh_hours
        )

    # =====================================================
    # REFRESH LIST
    # =====================================================

    def stale_symbols(

        self,

        symbols
    ):

        stale = []

        for symbol in symbols:

            if self.needs_refresh(

                symbol
            ):

                stale.append(symbol)

        return stale

    # =====================================================
    # SUMMARY
    # =====================================================

    def refresh_summary(

        self,

        symbols
    ):

        stale = self.stale_symbols(

            symbols
        )

        return {

            "Total Symbols":

                len(symbols),

            "Needs Refresh":

                len(stale),

            "Already Cached":

                len(symbols) - len(stale)
        }
