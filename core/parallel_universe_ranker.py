import pandas as pd
import numpy as np
import yfinance as yf

# =========================================================
# ULTRA FAST INSTITUTIONAL UNIVERSE RANKER
# =========================================================

class ParallelUniverseRanker:

    def __init__(

        self,

        batch_size=25
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

            # =============================================
            # FAST BATCH DOWNLOAD
            # =============================================

            data = yf.download(

                batch_symbols,

                period="3mo",

                auto_adjust=True,

                progress=False,

                group_by="ticker",

                threads=True
            )

            results = []

            # =============================================
            # PROCESS EACH STOCK
            # =============================================

            for symbol in batch_symbols:

                try:

                    if symbol not in data:

                        continue

                    stock = data[symbol]

                    close = stock["Close"].dropna()

                    volume = stock["Volume"].dropna()

                    # =====================================
                    # MINIMUM HISTORY CHECK
                    # =====================================

                    if len(close) < 40:

                        continue

                    # =====================================
                    # RETURNS
                    # =====================================

                    returns = close.pct_change().dropna()

                    if returns.empty:

                        continue

                    # =====================================
                    # QUANT METRICS
                    # =====================================

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

                    current_price = float(

                        close.iloc[-1]
                    )

                    # =====================================
                    # INSTITUTIONAL SCORE
                    # =====================================

                    score = (

                        momentum * 0.35

                        + sharpe * 0.30

                        + total_return * 0.20

                        - volatility * 0.10

                        + np.log1p(avg_volume) * 0.05
                    )

                    # =====================================
                    # OUTPUT
                    # =====================================

                    results.append({

                        "Symbol":

                            symbol,

                        "Sector":

                            "OTHER",

                        "Current Price":

                            round(
                                current_price,
                                2
                            ),

                        "Market Cap":

                            0,

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

        except Exception as e:

            print(

                f"BATCH FAILED -> {e}"
            )

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

        total_batches = (

            len(symbols)

            // self.batch_size
        ) + 1

        # =================================================
        # BATCH LOOP
        # =================================================

        for i in range(

            0,

            len(symbols),

            self.batch_size
        ):

            batch_number = (

                i // self.batch_size
            ) + 1

            batch = symbols[
                i:i + self.batch_size
            ]

            print(

                f"PROCESSING BATCH "

                f"{batch_number}/"

                f"{total_batches}"
            )

            batch_results = self.process_batch(

                batch
            )

            all_results.extend(

                batch_results
            )

        # =================================================
        # CREATE DATAFRAME
        # =================================================

        df = pd.DataFrame(

            all_results
        )

        if df.empty:

            return df

        # =================================================
        # CLEAN NUMERIC COLUMNS
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
