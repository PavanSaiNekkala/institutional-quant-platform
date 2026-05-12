import pandas as pd
import numpy as np
import yfinance as yf

# =========================================================
# FAST BATCH UNIVERSE RANKER
# =========================================================

class ParallelUniverseRanker:

    def __init__(

        self,

        batch_size=100
    ):

        self.batch_size = batch_size

    # =====================================================
    # PROCESS BATCH
    # =====================================================

    def process_batch(

        self,

        batch_symbols
    ):

        try:

            data = yf.download(

                batch_symbols,

                period="3mo",

                auto_adjust=True,

                progress=False,

                group_by="ticker",

                threads=True
            )

            results = []

            for symbol in batch_symbols:

                try:

                    if symbol not in data:

                        continue

                    stock = data[symbol]

                    close = stock["Close"].dropna()

                    volume = stock["Volume"].dropna()

                    if len(close) < 40:

                        continue

                    returns = close.pct_change().dropna()

                    if returns.empty:

                        continue

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

                    avg_volume = (

                        volume.tail(20).mean()
                    )

                    # =====================================
                    # FAST MARKET CAP
                    # =====================================

                    try:

                        fast_info = yf.Ticker(

                            symbol
                        ).fast_info

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

                    # =====================================
                    # INSTITUTIONAL SCORE
                    # =====================================

                    score = (

                        momentum * 0.30

                        + sharpe * 0.30

                        + total_return * 0.20

                        - volatility * 0.10

                        + np.log1p(avg_volume) * 0.10

                        + np.log1p(
                            max(market_cap, 1)
                        ) * 0.05
                    )

                    results.append({

                        "Symbol":

                            symbol,

                        "Sector":

                            "OTHER",

                        "Current Price":

                            round(
                                float(current_price),
                                2
                            ),

                        "Market Cap":

                            round(
                                float(market_cap),
                                0
                            ),

                        "Momentum":

                            round(
                                float(momentum),
                                4
                            ),

                        "Volatility":

                            round(
                                float(volatility),
                                4
                            ),

                        "Sharpe":

                            round(
                                float(sharpe),
                                4
                            ),

                        "Total Return":

                            round(
                                float(total_return),
                                4
                            ),

                        "Avg Volume":

                            round(
                                float(avg_volume),
                                0
                            ),

                        "Institutional Score":

                            round(
                                float(score),
                                4
                            )
                    })

                except:

                    continue

            return results

        except:

            return []

    # =====================================================
    # RANK UNIVERSE
    # =====================================================

    def rank(

        self,

        symbols
    ):

        print(

            f"\nPROCESSING "

            f"{len(symbols)} STOCKS\n"
        )

        all_results = []

        # =================================================
        # BATCH LOOP
        # =================================================

        for i in range(

            0,

            len(symbols),

            self.batch_size
        ):

            batch = symbols[
                i:i + self.batch_size
            ]

            print(

                f"PROCESSING BATCH "

                f"{i // self.batch_size + 1}"
            )

            batch_results = self.process_batch(

                batch
            )

            all_results.extend(

                batch_results
            )

        # =================================================
        # DATAFRAME
        # =================================================

        df = pd.DataFrame(

            all_results
        )

        if df.empty:

            return df

        # =================================================
        # CLEAN NUMERICS
        # =================================================

        numeric_cols = [

            "Current Price",

            "Market Cap",

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

        df = df.dropna(

            subset=[

                "Institutional Score"
            ]
        )

        # =================================================
        # SORT
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
