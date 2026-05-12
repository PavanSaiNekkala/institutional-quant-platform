import pandas as pd
import numpy as np
import yfinance as yf

from joblib import Parallel, delayed

# =========================================================
# FAILED STOCK TRACKER
# =========================================================

FAILED_STOCKS = []

# =========================================================
# SAFE ROUND
# =========================================================

def safe_round(value, digits=2):

    try:

        if value is None:

            return 0

        if pd.isna(value):

            return 0

        if np.isinf(value):

            return 0

        return round(float(value), digits)

    except Exception:

        return 0

# =========================================================
# PROCESS SINGLE STOCK
# =========================================================

def process_symbol(symbol):

    try:

        ticker = yf.Ticker(symbol)

        # =================================================
        # FETCH HISTORICAL DATA
        # =================================================

        data = ticker.history(

            period="3mo",

            auto_adjust=True
        )

        # =================================================
        # EMPTY DATA
        # =================================================

        if data.empty:

            FAILED_STOCKS.append({

                "Symbol": symbol,

                "Failure Reason":

                    "No historical data returned"
            })

            return None

        # =================================================
        # CLOSE PRICE
        # =================================================

        close = data["Close"]

        if isinstance(close, pd.DataFrame):

            close = close.iloc[:, 0]

        close = pd.to_numeric(

            close,

            errors="coerce"
        ).dropna()

        # =================================================
        # INSUFFICIENT DATA
        # =================================================

        if len(close) < 40:

            FAILED_STOCKS.append({

                "Symbol": symbol,

                "Failure Reason":

                    "Insufficient price candles"
            })

            return None

        # =================================================
        # RETURNS
        # =================================================

        returns = close.pct_change().dropna()

        if returns.empty:

            FAILED_STOCKS.append({

                "Symbol": symbol,

                "Failure Reason":

                    "Returns calculation failed"
            })

            return None

        # =================================================
        # FACTORS
        # =================================================

        momentum = (

            close.iloc[-1]

            / close.iloc[-20]

        ) - 1

        volatility = (

            returns.std()

            * np.sqrt(252)
        )

        sharpe = 0

        if returns.std() != 0:

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
        # MARKET CAP
        # =================================================

        market_cap = 0

        try:

            info = ticker.info

            market_cap = info.get(

                "marketCap",

                0
            )

            if market_cap is None:

                market_cap = 0

        except Exception:

            market_cap = 0

        # =================================================
        # INSTITUTIONAL SCORE
        # =================================================

        score = (
            momentum * 0.30
            + sharpe * 0.30
            + total_return * 0.20
            - volatility * 0.10
            + np.log1p(avg_volume) * 0.10
        )

        # =================================================
        # OUTPUT
        # =================================================

        return {

            "Symbol":

                symbol,

            "Momentum":

                safe_round(momentum, 4),

            "Volatility":

                safe_round(volatility, 4),

            "Sharpe":

                safe_round(sharpe, 4),

            "Total Return":

                safe_round(total_return, 4),

            "Avg Volume":

                safe_round(avg_volume, 0),

            "Market Cap (Cr)":

                safe_round(
                    market_cap / 10000000,
                    2
                ),

            "Institutional Score":

                safe_round(score, 4)
        }

    # =====================================================
    # EXCEPTION HANDLER
    # =====================================================

    except Exception as e:

        FAILED_STOCKS.append({

            "Symbol": symbol,

            "Failure Reason":

                str(e)
        })

        return None

# =========================================================
# PARALLEL RANKER
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

        global FAILED_STOCKS

        FAILED_STOCKS = []

        print(

            f"\nPROCESSING "

            f"{len(symbols)} STOCKS "

            f"USING {self.n_jobs} WORKERS\n"
        )

        results = Parallel(

            n_jobs=self.n_jobs,

            backend="threading",

            batch_size=50

        )(

            delayed(process_symbol)(symbol)

            for symbol in symbols
        )

        # =================================================
        # CLEAN RESULTS
        # =================================================

        results = [

            r for r in results

            if r is not None
        ]

        df = pd.DataFrame(results)

        if df.empty:

            return df

        # =================================================
        # CLEAN SCORE
        # =================================================

        df["Institutional Score"] = pd.to_numeric(

            df["Institutional Score"],

            errors="coerce"
        )

        df = df.dropna(

            subset=["Institutional Score"]
        )

        # =================================================
        # SORT
        # =================================================

        df = df.sort_values(

            by="Institutional Score",

            ascending=False
        )

        # =================================================
        # SAVE FAILED STOCKS
        # =================================================

        failed_df = pd.DataFrame(

            FAILED_STOCKS
        )

        if not failed_df.empty:

            failed_df.to_excel(

                "failed_stocks.xlsx",

                index=False
            )

            print(

                "\nFAILED STOCKS SAVED "
                "TO failed_stocks.xlsx\n"
            )

        return df.reset_index(drop=True)
