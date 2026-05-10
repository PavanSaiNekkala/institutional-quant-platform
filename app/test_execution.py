import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from execution.paper_broker import (
    PaperBroker
)

# =====================================================
# BROKER
# =====================================================

broker = PaperBroker()

connected = broker.connect()

print("\nBROKER CONNECTED")

print(connected)

# =====================================================
# BALANCE
# =====================================================

print("\nINITIAL CASH")

print(

    broker.get_balance()
)

# =====================================================
# BUY ORDER
# =====================================================

buy = broker.place_order(

    "RELIANCE.NS",

    quantity=10,

    side="BUY"
)

print("\nBUY ORDER")

print(buy)

# =====================================================
# SELL ORDER
# =====================================================

sell = broker.place_order(

    "TCS.NS",

    quantity=5,

    side="SELL"
)

print("\nSELL ORDER")

print(sell)

# =====================================================
# POSITIONS
# =====================================================

print("\nPORTFOLIO")

print(

    broker.positions()
)

# =====================================================
# FINAL CASH
# =====================================================

print("\nFINAL CASH")

print(

    broker.get_balance()
)