import random
from datetime import datetime

from execution.broker_interface import (
    BrokerInterface
)

# =========================================================
# PAPER BROKER
# =========================================================

class PaperBroker(

    BrokerInterface
):

    def __init__(self):

        self.cash = 1_000_000

        self.portfolio = {}

    # =====================================================
    # CONNECT
    # =====================================================

    def connect(self):

        return True

    # =====================================================
    # BALANCE
    # =====================================================

    def get_balance(self):

        return self.cash

    # =====================================================
    # POSITIONS
    # =====================================================

    def positions(self):

        return self.portfolio

    # =====================================================
    # ORDER
    # =====================================================

    def place_order(

        self,

        symbol,

        quantity,

        side
    ):

        price = random.uniform(

            100,

            3000
        )

        value = price * quantity

        timestamp = datetime.now()

        if side == "BUY":

            self.cash -= value

            self.portfolio[symbol] = (

                self.portfolio.get(

                    symbol,

                    0
                )

                + quantity
            )

        elif side == "SELL":

            self.cash += value

            self.portfolio[symbol] = (

                self.portfolio.get(

                    symbol,

                    0
                )

                - quantity
            )

        return {

            "timestamp":

                timestamp,

            "symbol":

                symbol,

            "side":

                side,

            "quantity":

                quantity,

            "price":

                round(price, 2),

            "value":

                round(value, 2),

            "cash_remaining":

                round(self.cash, 2)
        }