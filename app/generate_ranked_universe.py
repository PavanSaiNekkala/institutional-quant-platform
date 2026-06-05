import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import pandas as pd
import numpy as np
import yfinance as yf

# =========================================================
# LOAD STOCK UNIVERSE
# =========================================================

universe = pd.read_excel(

    "updated_stocks.xlsx"
)

symbols = (

    universe.iloc[:, 0]

    .dropna()

    .astype(str)

    .unique()

    .tolist()
)

# =========================================================
# RANKING ENGINE
# =========================================================

ranking_data = []

print(

    "\nGENERATING INSTITUTIONAL RANKINGS\n"
)

total = len(symbols)

for idx, symbol in enumerate(symbols):

    try:

        print(

            f"[{idx+1}/{total}] {symbol}"
        )

        data = yf.download(

            symbol,

            period="3mo",

            progress=False,

            auto_adjust=True,

            threads=True
        )

        if data.empty:

            continue

        # =====================================================
        # CLOSE
        # =====================================================

        close = data["Close"]

        if isinstance(close, pd.DataFrame):

            close = close.iloc[:, 0]

        close = pd.to_numeric(

            close,

            errors="coerce"
        ).dropna()

        if len(close) < 40:

            continue

        # =====================================================
        # RETURNS
        # =====================================================

        returns = close.pct_change().dropna()

        if returns.empty:

            continue

        # =====================================================
        # FACTORS
        # =====================================================

        momentum = (

            close.iloc[-1]

            / close.iloc[-20]

        ) - 1

        volatility = (

            returns.std()

            * np.sqrt(252)
        )

        sharpe = (

            returns.mean()

            / returns.std()

        ) * np.sqrt(252)

        total_return = (

            close.iloc[-1]

            / close.iloc[0]

        ) - 1

        # =====================================================
        # VOLUME
        # =====================================================

        volume = data["Volume"]

        if isinstance(volume, pd.DataFrame):

            volume = volume.iloc[:, 0]

        volume = pd.to_numeric(

            volume,

            errors="coerce"
        ).dropna()

        avg_volume = volume.tail(20).mean()

        # =====================================================
        # FORCE SCALARS
        # =====================================================

        momentum = float(momentum)

        volatility = float(volatility)

        sharpe = float(sharpe)

        total_return = float(total_return)

        avg_volume = float(avg_volume)

        # =====================================================
        # SCORE
        # =====================================================

        score = (

            momentum * 0.30

            + sharpe * 0.30

            + total_return * 0.20

            - volatility * 0.10

            + np.log1p(avg_volume) * 0.10
        )

        score = float(score)

        # =====================================================
        # STORE
        # =====================================================

        ranking_data.append({

            "Symbol":

                symbol,

            "Momentum":

                round(momentum, 4),

            "Volatility":

                round(volatility, 4),

            "Sharpe":

                round(sharpe, 4),

            "Total Return":

                round(total_return, 4),

            "Avg Volume":

                round(avg_volume, 0),

            "Institutional Score":

                round(score, 4)
        })

    except Exception as e:

        print(

            f"ERROR: {symbol} -> {e}"
        )

# =========================================================
# FINAL DATAFRAME
# =========================================================

ranking_df = pd.DataFrame(

    ranking_data
)

if ranking_df.empty:

    print(

        "\nNO VALID STOCKS RANKED\n"
    )

    sys.exit()

# =========================================================
# SAFE NUMERIC CONVERSION
# =========================================================

ranking_df["Institutional Score"] = pd.to_numeric(

    ranking_df["Institutional Score"],

    errors="coerce"
)

ranking_df = ranking_df.dropna(

    subset=["Institutional Score"]
)

# =========================================================
# SORT
# =========================================================

ranking_df = ranking_df.sort_values(

    by="Institutional Score",

    ascending=False
)

ranking_df.reset_index(

    drop=True,

    inplace=True
)

# =========================================================
# SAVE FILE
# =========================================================

ranking_df.to_excel(

    "ranked_universe.xlsx",

    index=False
)

# =========================================================
# OUTPUT
# =========================================================

print(

    "\nRANKED UNIVERSE GENERATED\n"
)

print(

    f"TOTAL RANKED STOCKS: {len(ranking_df)}"
)

print(

    "\nTOP STOCKS\n"
)

print(

    ranking_df.head()
)
