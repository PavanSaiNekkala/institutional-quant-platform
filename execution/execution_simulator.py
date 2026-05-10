import numpy as np
import pandas as pd
import yfinance as yf

# =========================================================
# EXECUTION SIMULATOR
# =========================================================

class ExecutionSimulator:

    def __init__(

        self,

        slippage_bps=5,

        transaction_cost_bps=2
    ):

        self.slippage_bps = slippage_bps

        self.transaction_cost_bps = transaction_cost_bps

    # =====================================================
    # SIMULATE EXECUTION
    # =====================================================

    def simulate_trade(

        self,

        symbol,

        quantity=100
    ):

        try:

            data = yf.download(

                symbol,

                period="5d",

                progress=False,

                auto_adjust=True
            )

            if data.empty:

                return None

            close = data["Close"]

            volume = data["Volume"]

            if isinstance(close, pd.DataFrame):

                close = close.iloc[:, 0]

            if isinstance(volume, pd.DataFrame):

                volume = volume.iloc[:, 0]

            market_price = float(

                close.iloc[-1]
            )

            avg_volume = float(

                volume.tail(5).mean()
            )

            # =================================================
            # SLIPPAGE
            # =================================================

            slippage = (

                market_price

                * self.slippage_bps

                / 10000
            )

            # =================================================
            # MARKET IMPACT
            # =================================================

            participation_rate = min(

                quantity / avg_volume,

                0.05
            )

            impact_cost = (

                market_price

                * participation_rate

                * 0.01
            )

            # =================================================
            # TRANSACTION COST
            # =================================================

            transaction_cost = (

                market_price

                * self.transaction_cost_bps

                / 10000
            )

            # =================================================
            # EXECUTION PRICE
            # =================================================

            execution_price = (

                market_price

                + slippage

                + impact_cost

                + transaction_cost
            )

            total_cost = (

                execution_price

                * quantity
            )

            return {

                "Symbol":

                    symbol,

                "Market Price":

                    round(market_price, 2),

                "Execution Price":

                    round(execution_price, 2),

                "Slippage":

                    round(slippage, 4),

                "Impact Cost":

                    round(impact_cost, 4),

                "Transaction Cost":

                    round(transaction_cost, 4),

                "Total Trade Cost":

                    round(total_cost, 2),

                "Participation Rate":

                    round(participation_rate, 6)
            }

        except:

            return None

    # =====================================================
    # BATCH EXECUTION
    # =====================================================

    def simulate_portfolio_execution(

        self,

        symbols,

        quantity=100
    ):

        results = []

        for symbol in symbols:

            result = self.simulate_trade(

                symbol,

                quantity
            )

            if result:

                results.append(result)

        return pd.DataFrame(results)