import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import yfinance as yf
import pandas as pd

from automation.alerts import (
    institutional_alerts
)

# =====================================================
# DOWNLOAD DATA
# =====================================================

data = yf.download(

    "RELIANCE.NS",

    period="6mo",

    progress=False
)

# =====================================================
# STANDARDIZE
# =====================================================

if isinstance(

    data.columns,

    pd.MultiIndex
):

    data.columns = (

        data.columns

        .get_level_values(0)
    )

data.columns = [

    str(c).lower()

    for c in data.columns
]

# =====================================================
# SERIES
# =====================================================

close = data["close"]

volume = data["volume"]

returns = close.pct_change().dropna()

equity_curve = (

    100000 *

    (1 + returns)

    .cumprod()
)

# =====================================================
# ALERTS
# =====================================================

alerts = institutional_alerts(

    close,

    volume,

    returns,

    equity_curve
)

# =====================================================
# RESULTS
# =====================================================

print("\nINSTITUTIONAL ALERT ENGINE")

for k, v in alerts.items():

    print(f"{k}: {v}")