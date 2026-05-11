import pandas as pd
import numpy as np
import yfinance as yf

from joblib import Parallel, delayed

# =========================================================
# PROCESS SINGLE STOCK
# =========================================================

def process_symbol(symbol):

    try:

        data = yf.download(

            symbol,

            period="3mo",

            progress=False,

            auto_adjust=True,
            
            threads=False
        )

        if data.empty:

            return None

        close = data["Close"]

        if isinstance(close, pd.DataFrame):

            close = close.iloc[:, 0]

        close = pd.to_numeric(

            close,

            errors="coerce"
        ).dropna()

        if len(close) < 40:

            return None

        returns = close.pct_change().dropna()

        if returns.empty:

            return None

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

        volume = data["Volume"]

        if isinstance(volume, pd.DataFrame):

            volume = volume.iloc[:, 0]

        volume = pd.to_numeric(

            volume,

            errors="coerce"
        ).dropna()

        avg_volume = volume.tail(20).mean()

        score = (
            momentum * 0.30
            + sharpe * 0.30
            + total_return * 0.20
            - volatility * 0.10
            + np.log1p(avg_volume) * 0.10
        )

        return {

            "Symbol":

                symbol,

            "Momentum":

                round(float(momentum), 4),

            "Volatility":

                round(float(volatility), 4),

            "Sharpe":

                round(float(sharpe), 4),

            "Total Return":

                round(float(total_return), 4),

            "Avg Volume":

                round(float(avg_volume), 0),

            "Institutional Score":

                round(float(score), 4)
        }

    except:

        return None

# =========================================================
# PARALLEL RANKER
# =========================================================

class ParallelUniverseRanker:

    def __init__(

        self,

        n_jobs=8
    ):

        self.n_jobs = n_jobs

    # =====================================================
    # RANK UNIVERSE
    # =====================================================

    def rank(

        self,

        symbols
    ):

        print(

            f"\nPROCESSING "

            f"{len(symbols)} STOCKS "
            
            f"USING {self.n_jobs} CORES\n"
        )

        results = Parallel(

            n_jobs=self.n_jobs,

            backend="threading"

        )(

            delayed(process_symbol)(symbol)

            for symbol in symbols
        )

        results = [

            r for r in results

            if r is not None
        ]

        df = pd.DataFrame(results)

        if df.empty:

            return df

        df["Institutional Score"] = pd.to_numeric(

            df["Institutional Score"],

            errors="coerce"
        )

        df = df.dropna(

            subset=["Institutional Score"]
        )

        return df.sort_values(

            by="Institutional Score",

            ascending=False
        )
