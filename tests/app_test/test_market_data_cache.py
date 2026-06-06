import sys
import time

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.market_data_cache import (
    MarketDataCache
)

# =====================================================
# ENGINE
# =====================================================

engine = MarketDataCache()

# =====================================================
# FIRST LOAD
# =====================================================

start = time.time()

data1 = engine.get_data(

    "RELIANCE.NS"
)

end = time.time()

print(

    f"\nFIRST LOAD TIME: "

    f"{round(end-start, 2)} sec"
)

# =====================================================
# SECOND LOAD
# =====================================================

start = time.time()

data2 = engine.get_data(

    "RELIANCE.NS"
)

end = time.time()

print(

    f"\nSECOND LOAD TIME: "

    f"{round(end-start, 2)} sec"
)

print(

    "\nCACHE OPERATIONAL\n"
)

print(data2.tail())
