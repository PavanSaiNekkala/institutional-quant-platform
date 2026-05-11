import sys
import pandas as pd

from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

# =========================================================
# IMPORTS
# =========================================================

from core.parallel_universe_ranker import (
    ParallelUniverseRanker
)

from core.incremental_refresh_engine import (
    IncrementalRefreshEngine
)

# =========================================================
# LOAD UNIVERSE
# =========================================================

def load_symbols():

    universe = pd.read_excel(

        ROOT_DIR / "valid_stocks.xlsx"
    )

    symbols = (

        universe.iloc[:, 0]

        .dropna()

        .astype(str)

        .unique()

        .tolist()
    )

    return symbols

# =========================================================
# MAIN BATCH PROCESS
# =========================================================

def run_overnight_batch():

    print(

        "\nSTARTING OVERNIGHT "
        
        "INSTITUTIONAL BATCH\n"
    )

    # =====================================================
    # LOAD SYMBOLS
    # =====================================================

    symbols = load_symbols()

    print(

        f"TOTAL SYMBOLS: "
        
        f"{len(symbols)}"
    )

    # =====================================================
    # CHECK STALE SYMBOLS
    # =====================================================

    refresh_engine = IncrementalRefreshEngine(

        refresh_hours=24
    )

    stale_symbols = refresh_engine.stale_symbols(

        symbols
    )

    print(

        f"\nSTALE SYMBOLS: "
        
        f"{len(stale_symbols)}"
    )

    # =====================================================
    # NOTHING TO REFRESH
    # =====================================================

    if len(stale_symbols) == 0:

        print(

            "\nALL DATA CURRENT\n"
        )

        return

    # =====================================================
    # PARALLEL RANKING
    # =====================================================

    ranker = ParallelUniverseRanker(

        n_jobs=8
    )

    ranking_df = ranker.rank(

        stale_symbols
    )

    # =====================================================
    # SAVE OUTPUT
    # =====================================================

    output_path = (

        ROOT_DIR

        / "ranked_universe.xlsx"
    )

    ranking_df.to_excel(

        output_path,

        index=False
    )

    print(

        "\nRANKED UNIVERSE SAVED\n"
    )

    print(

        f"TOTAL RANKED: "
        
        f"{len(ranking_df)}"
    )

    # =====================================================
    # LOG FILE
    # =====================================================

    log_path = (

        ROOT_DIR

        / "automation"

        / "overnight_batch_log.txt"
    )

    with open(

        log_path,

        "a",

        encoding="utf-8"
    ) as f:

        f.write(

            f"\n{datetime.now()} | "
            
            f"Processed {len(stale_symbols)} "
            
            f"symbols | "
            
            f"Ranked {len(ranking_df)}"
        )

    print(

        "\nOVERNIGHT BATCH COMPLETE\n"
    )

# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    run_overnight_batch()
