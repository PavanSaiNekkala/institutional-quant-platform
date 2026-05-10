import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import pandas as pd
import yfinance as yf

from data.downloader import (
    load_symbols,
    prefilter_symbols,
    batch_download
)

from core.relative_strength import (
    relative_strength,
    relative_momentum,
    cross_sectional_rank,
    leadership_score,
    classify_leader
)

# =====================================================
# LOAD STOCKS
# =====================================================

symbols = load_symbols()

symbols = prefilter_symbols(symbols)

symbols = symbols[:10]

print("DOWNLOADING DATA...")

stock_data = batch_download(symbols)

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
# RELATIVE MOMENTUM
# =====================================================

scores = {}

for symbol, df in stock_data.items():

    try:

        close = df["close"]

        returns = close.pct_change().dropna()

        aligned = pd.concat(

            [returns, benchmark_returns],

            axis=1

        ).dropna()

        stock_r = aligned.iloc[:, 0]

        benchmark_r = aligned.iloc[:, 1]

        rm = relative_momentum(

            stock_r,

            benchmark_r
        )

        latest_rm = rm.iloc[-1]

        scores[symbol] = latest_rm

    except:
        continue

# =====================================================
# RANKING
# =====================================================

scores_series = pd.Series(scores)

ranks = cross_sectional_rank(

    scores_series
)

# =====================================================
# LEADERSHIP ANALYSIS
# =====================================================

results = []

for symbol in scores_series.index:

    rm = scores_series[symbol]

    rank = ranks[symbol]

    score = leadership_score(

        rm,

        rank
    )

    label = classify_leader(

        score
    )

    results.append({

        "Symbol": symbol,

        "Relative Momentum": rm,

        "Percentile Rank": rank,

        "Leadership Score": score,

        "Classification": label
    })

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(

    "Leadership Score",

    ascending=False
)

print("\nRELATIVE STRENGTH LEADERS")

print(results_df)