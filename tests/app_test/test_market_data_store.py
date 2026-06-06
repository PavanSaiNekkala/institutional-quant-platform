import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from core.market_data_store import (

    save_market_data,
    load_market_data
)

# =====================================================
# SYMBOL
# =====================================================

symbol = "RELIANCE.NS"

# =====================================================
# SAVE
# =====================================================

saved = save_market_data(

    symbol
)

print(

    "\nDATA SAVED:",

    saved
)

# =====================================================
# LOAD
# =====================================================

df = load_market_data(

    symbol
)

print(

    "\nLOADED ROWS:",

    len(df)
)

print(

    df.head()
)
