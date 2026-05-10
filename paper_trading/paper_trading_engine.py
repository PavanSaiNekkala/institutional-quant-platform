import pandas as pd
import yfinance as yf

from paper_trading.portfolio_storage import (

    initialize_database,
    save_cash,
    load_cash,
    save_position,
    load_positions,
    save_trade,
    load_trades
)

# =========================================================
# PAPER TRADING ENGINE
# =========================================================

class PaperTradingEngine:

    def __init__(

        self,

        initial_cash=100000
    ):

        # =================================================
        # INITIALIZE DATABASE
        # =================================================

        initialize_database()

        # =================================================
        # LOAD PERSISTENT STATE
        # =================================================

        self.cash = load_cash()

        if self.cash is None:

            self.cash = initial_cash

            save_cash(self.cash)

        self.positions = load_positions()

        self.trade_history = (

            load_trades()

            .to_dict(

                orient="records"
            )
        )

    # =====================================================
    # GET MARKET PRICE
    # =====================================================

    def get_price(

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

            close = close.dropna()

            if len(close) == 0:

                return None

            return float(close.iloc[-1])

        except:

            return None

    # =====================================================
    # BUY
    # =====================================================

    def buy(

        self,

        symbol,

        quantity
    ):

        price = self.get_price(

            symbol
        )

        if price is None:

            return "PRICE ERROR"

        cost = price * quantity

        if cost > self.cash:

            return "INSUFFICIENT CASH"

        # =================================================
        # UPDATE CASH
        # =================================================

        self.cash -= cost

        save_cash(

            self.cash
        )

        # =================================================
        # UPDATE POSITIONS
        # =================================================

        self.positions[symbol] = (

            self.positions.get(

                symbol,

                0
            )

            + quantity
        )

        save_position(

            symbol,

            self.positions[symbol]
        )

        # =================================================
        # SAVE TRADE
        # =================================================

        trade = {

            "Action": "BUY",

            "Symbol": symbol,

            "Quantity": quantity,

            "Price": round(price, 2),

            "Cost": round(cost, 2)
        }

        self.trade_history.append(

            trade
        )

        save_trade(

            "BUY",

            symbol,

            quantity,

            round(price, 2),

            round(cost, 2)
        )

        return "BUY EXECUTED"

    # =====================================================
    # SELL
    # =====================================================

    def sell(

        self,

        symbol,

        quantity
    ):

        if (

            symbol not in self.positions

            or self.positions[symbol] < quantity
        ):

            return "INSUFFICIENT POSITION"

        price = self.get_price(

            symbol
        )

        if price is None:

            return "PRICE ERROR"

        proceeds = price * quantity

        # =================================================
        # UPDATE CASH
        # =================================================

        self.cash += proceeds

        save_cash(

            self.cash
        )

        # =================================================
        # UPDATE POSITION
        # =================================================

        self.positions[symbol] -= quantity

        if self.positions[symbol] <= 0:

            self.positions[symbol] = 0

        save_position(

            symbol,

            self.positions[symbol]
        )

        # =================================================
        # SAVE TRADE
        # =================================================

        trade = {

            "Action": "SELL",

            "Symbol": symbol,

            "Quantity": quantity,

            "Price": round(price, 2),

            "Proceeds": round(proceeds, 2)
        }

        self.trade_history.append(

            trade
        )

        save_trade(

            "SELL",

            symbol,

            quantity,

            round(price, 2),

            round(proceeds, 2)
        )

        return "SELL EXECUTED"

    # =====================================================
    # PORTFOLIO VALUE
    # =====================================================

    def portfolio_value(self):

        total_value = self.cash

        for symbol, quantity in self.positions.items():

            if quantity <= 0:

                continue

            price = self.get_price(

                symbol
            )

            if price:

                total_value += (

                    price * quantity
                )

        return round(total_value, 2)

    # =====================================================
    # PORTFOLIO REPORT
    # =====================================================

    def report(self):

        active_positions = {

            k: v

            for k, v in self.positions.items()

            if v > 0
        }

        return {

            "Cash":

                round(self.cash, 2),

            "Positions":

                active_positions,

            "Portfolio Value":

                self.portfolio_value(),

            "Trades":

                self.trade_history
        }