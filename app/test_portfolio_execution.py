import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import pandas as pd

from execution.paper_broker import (
    PaperBroker
)

from execution.portfolio_executor import (
    generate_orders,
    execute_portfolio
)

# =====================================================
# SAMPLE PORTFOLIO
# =====================================================

portfolio = pd.DataFrame({

    "Symbol": [

        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS"
    ],

    "Weight": [

        0.30,
        0.25,
        0.25,
        0.20
    ],

    "Price": [

        2900,
        3800,
        1450,
        1600
    ]
})

# =====================================================
# GENERATE ORDERS
# =====================================================

orders = generate_orders(

    portfolio,

    capital=1_000_000
)

print("\nGENERATED ORDERS")

print(orders)

# =====================================================
# PAPER BROKER
# =====================================================

broker = PaperBroker()

# =====================================================
# EXECUTION
# =====================================================

executions = execute_portfolio(

    broker,

    orders
)

print("\nEXECUTION RESULTS")

print(executions)

# =====================================================
# FINAL PORTFOLIO
# =====================================================

print("\nBROKER POSITIONS")

print(

    broker.positions()
)

# =====================================================
# FINAL CASH
# =====================================================

print("\nREMAINING CASH")

print(

    broker.get_balance()
)