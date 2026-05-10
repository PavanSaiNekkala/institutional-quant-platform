import pandas as pd

# =========================================================
# TRADE PERFORMANCE ANALYTICS
# =========================================================

class TradePerformanceAnalytics:

    def __init__(

        self,

        pnl_dataframe
    ):

        self.df = pnl_dataframe.copy()

    # =====================================================
    # CLEAN DATA
    # =====================================================

    def clean(self):

        if self.df.empty:

            return

        numeric_cols = [

            "Realized PnL",
            "Unrealized PnL"
        ]

        for col in numeric_cols:

            if col in self.df.columns:

                self.df[col] = pd.to_numeric(

                    self.df[col],

                    errors="coerce"
                )

    # =====================================================
    # WIN RATE
    # =====================================================

    def win_rate(self):

        if self.df.empty:

            return 0

        wins = len(

            self.df[

                self.df["Realized PnL"]

                > 0
            ]
        )

        total = len(self.df)

        if total == 0:

            return 0

        return round(

            (wins / total) * 100,

            2
        )

    # =====================================================
    # AVERAGE GAIN
    # =====================================================

    def average_gain(self):

        gains = self.df[

            self.df["Realized PnL"]

            > 0
        ]

        if gains.empty:

            return 0

        return round(

            gains["Realized PnL"]

            .mean(),

            2
        )

    # =====================================================
    # AVERAGE LOSS
    # =====================================================

    def average_loss(self):

        losses = self.df[

            self.df["Realized PnL"]

            < 0
        ]

        if losses.empty:

            return 0

        return round(

            losses["Realized PnL"]

            .mean(),

            2
        )

    # =====================================================
    # PROFIT FACTOR
    # =====================================================

    def profit_factor(self):

        gross_profit = self.df[

            self.df["Realized PnL"]

            > 0
        ]["Realized PnL"].sum()

        gross_loss = abs(

            self.df[

                self.df["Realized PnL"]

                < 0
            ]["Realized PnL"].sum()
        )

        if gross_loss == 0:

            return None

        return round(

            gross_profit / gross_loss,

            2
        )

    # =====================================================
    # EXPECTANCY
    # =====================================================

    def expectancy(self):

        win_rate = self.win_rate() / 100

        loss_rate = 1 - win_rate

        avg_gain = self.average_gain()

        avg_loss = abs(

            self.average_loss()
        )

        expectancy = (

            (win_rate * avg_gain)

            -

            (loss_rate * avg_loss)
        )

        return round(

            expectancy,

            2
        )

    # =====================================================
    # FULL REPORT
    # =====================================================

    def full_report(self):

        self.clean()

        return {

            "Win Rate %":

                self.win_rate(),

            "Average Gain":

                self.average_gain(),

            "Average Loss":

                self.average_loss(),

            "Profit Factor":

                self.profit_factor(),

            "Expectancy":

                self.expectancy()
        }