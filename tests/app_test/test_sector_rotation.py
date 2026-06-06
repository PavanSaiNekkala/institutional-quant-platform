import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import pandas as pd
import yfinance as yf

from core.sector_rotation import (
    SECTOR_ETFS,
    sector_momentum,
    relative_sector_strength,
    sector_ranking,
    classify_sector
)

# =====================================================
# BENCHMARK
# =====================================================

benchmark = yf.download(

    "^NSEI",

    period="2y",

    progress=False
)

benchmark_close = benchmark["Close"].squeeze()

benchmark_returns = (

    benchmark_close

    .pct_change()

    .dropna()
)

# =====================================================
# SECTOR ANALYSIS
# =====================================================

results = []

for sector, ticker in SECTOR_ETFS.items():

    try:

        data = yf.download(

            ticker,

            period="2y",

            progress=False
        )

        close = data["Close"].squeeze()

        returns = close.pct_change().dropna()

        rm = sector_momentum(

            close
        )

        rs = relative_sector_strength(

            returns,

            benchmark_returns
        )

        latest_rm = rm.iloc[-1]

        latest_rs = rs.iloc[-1]

        score = (

            0.5 * latest_rm +

            0.5 * latest_rs
        )

        results.append({

            "Sector": sector,

            "Momentum": latest_rm,

            "Relative Strength": latest_rs,

            "Score": score
        })

    except:
        continue

# =====================================================
# RANKING
# =====================================================

results_df = pd.DataFrame(results)

results_df["Percentile"] = (

    results_df["Score"]

    .rank(

        ascending=False,

        pct=True
    )
)

results_df["Classification"] = (

    results_df["Percentile"]

    .apply(classify_sector)
)

results_df = results_df.sort_values(

    "Score",

    ascending=False
)

print("\nSECTOR ROTATION ANALYSIS")

print(results_df)
