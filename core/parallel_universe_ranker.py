import pandas as pd
import numpy as np
import yfinance as yf

from joblib import Parallel, delayed

# =========================================================
# PROCESS SINGLE STOCK
# =========================================================

def process_symbol(symbol):

    try:

        # =================================================
        # DOWNLOAD MARKET DATA
        # =================================================

        data = yf.download(

            symbol,

            period="3mo",

            progress=False,

            auto_adjust=True,

            threads=False
        )

        if data.empty:

            return None

        # =================================================
        # CLOSE PRICES
        # =================================================

        close = data["Close"]

        if isinstance(close, pd.DataFrame):

            close = close.iloc[:, 0]

        close = pd.to_numeric(

            close,

            errors="coerce"
        ).dropna()

        if len(close) < 40:

            return None

        # =================================================
        # RETURNS
        # =================================================

        returns = close.pct_change().dropna()

        if returns.empty:

            return None

        # =================================================
        # QUANT METRICS
        # =================================================

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

        # =================================================
        # VOLUME
        # =================================================

        volume = data["Volume"]

        if isinstance(volume, pd.DataFrame):

            volume = volume.iloc[:, 0]

        volume = pd.to_numeric(

            volume,

            errors="coerce"
        ).dropna()

        avg_volume = volume.tail(20).mean()

        # =================================================
        # FAST FUNDAMENTALS
        # =================================================

        ticker = yf.Ticker(symbol)

        try:

            fast_info = ticker.fast_info

        except:

            fast_info = {}

        market_cap = fast_info.get(

            "market_cap",

            0
        )

        current_price = fast_info.get(

            "last_price",

            float(close.iloc[-1])
        )

        # =================================================
        # PLACEHOLDER META
        # =================================================

        sector = "OTHER"

        industry = "OTHER"

        company_name = symbol

        # =================================================
        # INSTITUTIONAL SCORE
        # =================================================

        score = (

            momentum * 0.30

            + sharpe * 0.30

            + total_return * 0.20

            - volatility * 0.10

            + np.log1p(avg_volume) * 0.10

            + np.log1p(max(market_cap, 1)) * 0.05
        )

        # =================================================
        # FINAL OUTPUT
        # =================================================

        return {

            "Symbol":

                symbol,

            "Company":

                company_name,

            "Sector":

                sector,

            "Industry":

                industry,

            "Current Price":

                round(float(current_price), 2),

            "Market Cap":

                round(float(market_cap), 0),

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

    except Exception as e:

        print(

            f"FAILED: {symbol} -> {e}"
        )

        return None

# =========================================================
# PARALLEL UNIVERSE RANKER
# =========================================================

class ParallelUniverseRanker:

    def __init__(

        self,

        n_jobs=32
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

            f"USING {self.n_jobs} WORKERS\n"
        )

        # =================================================
        # PARALLEL EXECUTION
        # =================================================

        results = Parallel(

            n_jobs=self.n_jobs,

            backend="threading"

        )(

            delayed(process_symbol)(symbol)

            for symbol in symbols
        )

        # =================================================
        # FILTER VALID RESULTS
        # =================================================

        results = [

            r for r in results

            if r is not None
        ]

        df = pd.DataFrame(results)

        if df.empty:

            return df

        # =================================================
        # NUMERIC CLEANING
        # =================================================

        numeric_cols = [

            "Market Cap",

            "Current Price",

            "Momentum",

            "Volatility",

            "Sharpe",

            "Total Return",

            "Avg Volume",

            "Institutional Score"
        ]

        for col in numeric_cols:

            df[col] = pd.to_numeric(

                df[col],

                errors="coerce"
            )

        # =================================================
        # REMOVE BAD ROWS
        # =================================================

        df = df.dropna(

            subset=[

                "Institutional Score"
            ]
        )

        # =================================================
        # SORT RANKINGS
        # =================================================

        df = df.sort_values(

            by="Institutional Score",

            ascending=False
        )

        df = df.reset_index(

            drop=True
        )

        print(

            f"\nSUCCESSFULLY RANKED "

            f"{len(df)} STOCKS\n"
        )

        return df
