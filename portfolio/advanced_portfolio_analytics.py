import pandas as pd
import yfinance as yf

# =========================================================
# ADVANCED PORTFOLIO ANALYTICS
# =========================================================

class AdvancedPortfolioAnalytics:

    def __init__(

        self,

        positions,

        trades,

        cash
    ):

        self.positions = positions

        self.trades = trades

        self.cash = cash

    # =====================================================
    # CURRENT MARKET VALUE
    # =====================================================

    def market_value(self):

        total = 0

        values = []

        for symbol, quantity in self.positions.items():

            if quantity <= 0:

                continue

            try:

                data = yf.download(

                    symbol,

                    period="5d",

                    progress=False,

                    auto_adjust=True
                )

                if data.empty:

                    continue

                close = data["Close"]

                if isinstance(close, pd.DataFrame):

                    close = close.iloc[:, 0]

                close = close.dropna()

                if len(close) == 0:

                    continue

                price = float(

                    close.iloc[-1]
                )

                value = (

                    price * quantity
                )

                total += value

                values.append({

                    "Symbol":

                        symbol,

                    "Quantity":

                        quantity,

                    "Price":

                        round(price, 2),

                    "Market Value":

                        round(value, 2)
                })

            except Exception:

                continue

        return total, pd.DataFrame(values)

    # =====================================================
    # TRADE ANALYTICS
    # =====================================================

    def trade_statistics(self):

        if len(self.trades) == 0:

            return {

                "Total Trades": 0,

                "Buy Trades": 0,

                "Sell Trades": 0
            }

        trades_df = pd.DataFrame(

            self.trades
        )

        if trades_df.empty:

            return {

                "Total Trades": 0,

                "Buy Trades": 0,

                "Sell Trades": 0
            }

        # =================================================
        # NORMALIZE COLUMN NAMES
        # =================================================

        trades_df.columns = [

            str(col).strip().lower()

            for col in trades_df.columns
        ]

        if "action" not in trades_df.columns:

            return {

                "Total Trades": 0,

                "Buy Trades": 0,

                "Sell Trades": 0
            }

        # =================================================
        # NORMALIZE ACTION VALUES
        # =================================================

        trades_df["action"] = (

            trades_df["action"]

            .astype(str)

            .str.upper()

            .str.strip()
        )

        total_trades = len(trades_df)

        buy_trades = len(

            trades_df[

                trades_df["action"]

                == "BUY"
            ]
        )

        sell_trades = len(

            trades_df[

                trades_df["action"]

                == "SELL"
            ]
        )

        return {

            "Total Trades":

                total_trades,

            "Buy Trades":

                buy_trades,

            "Sell Trades":

                sell_trades
        }

    # =====================================================
    # EXPOSURE ANALYSIS
    # =====================================================

    def exposure_analysis(

        self,

        market_value
    ):

        total_equity = (

            market_value

            + self.cash
        )

        if total_equity <= 0:

            return {

                "Equity Exposure": 0,

                "Cash Exposure": 0
            }

        equity_exposure = (

            market_value

            / total_equity
        )

        cash_exposure = (

            self.cash

            / total_equity
        )

        return {

            "Equity Exposure":

                round(equity_exposure, 4),

            "Cash Exposure":

                round(cash_exposure, 4)
        }

    # =====================================================
    # FULL ANALYTICS
    # =====================================================

    def full_report(self):

        market_value, holdings_df = (

            self.market_value()
        )

        stats = self.trade_statistics()

        exposure = self.exposure_analysis(

            market_value
        )

        portfolio_value = (

            market_value

            + self.cash
        )

        report = {

            "Cash":

                round(self.cash, 2),

            "Market Value":

                round(market_value, 2),

            "Portfolio Value":

                round(portfolio_value, 2)
        }

        report.update(stats)

        report.update(exposure)

        return report, holdings_df