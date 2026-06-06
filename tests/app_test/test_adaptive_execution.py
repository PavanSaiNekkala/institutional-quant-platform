import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from execution.paper_broker import (
    PaperBroker
)

from execution.adaptive_execution import (
    twap_execution,
    vwap_execution,
    adaptive_execution
)

# =====================================================
# BROKER
# =====================================================

broker = PaperBroker()

# =====================================================
# TWAP
# =====================================================

twap = twap_execution(

    broker,

    symbol="RELIANCE.NS",

    total_quantity=100
)

print("\nTWAP EXECUTION")

print(twap)

# =====================================================
# VWAP
# =====================================================

profile = [

    0.10,
    0.20,
    0.30,
    0.20,
    0.20
]

vwap = vwap_execution(

    broker,

    symbol="TCS.NS",

    total_quantity=100,

    volume_profile=profile
)

print("\nVWAP EXECUTION")

print(vwap)

# =====================================================
# ADAPTIVE
# =====================================================

adaptive = adaptive_execution(

    broker,

    symbol="INFY.NS",

    quantity=120,

    volatility=0.05
)

print("\nADAPTIVE EXECUTION")

print(adaptive)

# =====================================================
# PORTFOLIO
# =====================================================

print("\nBROKER POSITIONS")

print(

    broker.positions()
)
