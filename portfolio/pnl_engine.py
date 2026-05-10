import pandas as pd
import yfinance as yf

# =========================================================
# PNL ENGINE
# =========================================================

class PNLEngine:

    def __init__(

        self,

        trades
    ):

        self.trades = pd.DataFrame(

            trades
        )

        if not self.trades.empty:

            self.trades.columns = [

                str(col).strip().lower()

                for col in self.trades.columns
            ]

    # =====================================================
    # CURRENT PRICE
    # =====================================================

    def current_price(

        self,

        symbol
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

            if isinstance(close, pd.DataFrame):

                close = close.iloc[:, 0]

            return float(

                close.iloc[-1]
            )

        except:

            return None

    # =====================================================
    # POSITION ANALYSIS
    # =====================================================

    def position_analysis(self):

        if self.trades.empty:

            return pd.DataFrame()

        symbols = self.trades[

            "symbol"

        ].unique()

        results = []

        for symbol in symbols:

            df = self.trades[

                self.trades["symbol"]

                == symbol
            ]

            buys = df[

                df["action"]

                == "BUY"
            ]

            sells = df[

                df["action"]

                == "SELL"
            ]

            buy_qty = buys[

                "quantity"

            ].sum()

            sell_qty = sells[

                "quantity"

            ].sum()

            net_qty = (

                buy_qty

                - sell_qty
            )

            buy_value = buys[

                "value"

            ].sum()

            sell_value = sells[

                "value"

            ].sum()

            avg_buy_price = (

                buy_value / buy_qty

                if buy_qty > 0

                else 0
            )

            realized_pnl = (

                sell_value

                - (

                    avg_buy_price

                    * sell_qty
                )
            )

            current_price = self.current_price(

                symbol
            )

            unrealized_pnl = 0

            market_value = 0

            if (

                current_price is not None

                and net_qty > 0
            ):

                market_value = (

                    current_price

                    * net_qty
                )

                unrealized_pnl = (

                    market_value

                    - (

                        avg_buy_price

                        * net_qty
                    )
                )

            results.append({

                "Symbol":

                    symbol,

                "Net Quantity":

                    round(net_qty, 2),

                "Average Buy Price":

                    round(avg_buy_price, 2),

                "Current Price":

                    round(current_price, 2)

                    if current_price

                    else None,

                "Market Value":

                    round(market_value, 2),

                "Realized PnL":

                    round(realized_pnl, 2),

                "Unrealized PnL":

                    round(unrealized_pnl, 2)
            })

        return pd.DataFrame(results)

    # =====================================================
    # TOTAL PNL
    # =====================================================

    def total_pnl(self):

        df = self.position_analysis()

        if df.empty:

            return {}

        realized = df[

            "Realized PnL"

        ].sum()

        unrealized = df[

            "Unrealized PnL"

        ].sum()

        total = (

            realized

            + unrealized
        )

        return {

            "Total Realized PnL":

                round(realized, 2),

            "Total Unrealized PnL":

                round(unrealized, 2),

            "Total Portfolio PnL":

                round(total, 2)
        }