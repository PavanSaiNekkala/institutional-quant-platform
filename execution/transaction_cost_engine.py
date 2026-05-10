import numpy as np
import pandas as pd

# =========================================================
# TRANSACTION COST ENGINE
# =========================================================

class TransactionCostEngine:

    def __init__(

        self,

        commission_bps=2,

        slippage_bps=5
    ):

        self.commission_bps = commission_bps

        self.slippage_bps = slippage_bps

    # =====================================================
    # SINGLE TRADE COST
    # =====================================================

    def calculate_trade_cost(

        self,

        trade_value
    ):

        commission = (

            trade_value

            * self.commission_bps

            / 10000
        )

        slippage = (

            trade_value

            * self.slippage_bps

            / 10000
        )

        total_cost = (

            commission

            + slippage
        )

        return {

            "Trade Value":

                round(trade_value, 2),

            "Commission":

                round(commission, 2),

            "Slippage":

                round(slippage, 2),

            "Total Cost":

                round(total_cost, 2)
        }

    # =====================================================
    # PORTFOLIO COST ANALYSIS
    # =====================================================

    def analyze_portfolio_costs(

        self,

        portfolio_values
    ):

        results = []

        for value in portfolio_values:

            result = self.calculate_trade_cost(

                value
            )

            results.append(result)

        df = pd.DataFrame(results)

        total_turnover = df[

            "Trade Value"

        ].sum()

        total_cost = df[

            "Total Cost"

        ].sum()

        cost_ratio = (

            total_cost

            / total_turnover
        )

        summary = {

            "Total Turnover":

                round(total_turnover, 2),

            "Total Transaction Cost":

                round(total_cost, 2),

            "Cost Ratio":

                round(cost_ratio, 6)
        }

        return df, summary