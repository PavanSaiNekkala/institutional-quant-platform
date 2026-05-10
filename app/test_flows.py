import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import yfinance as yf
import pandas as pd

from core.flows import (
    volume_zscore,
    accumulation_distribution,
    on_balance_volume,
    flow_momentum,
    smart_money_score,
    classify_flow
)

# =====================================================
# DOWNLOAD DATA
# =====================================================

data = yf.download(

    "RELIANCE.NS",

    period="2y",

    progress=False
)

# =====================================================
# STANDARDIZE COLUMNS
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
# FLOW ANALYTICS
# =====================================================

vz = volume_zscore(

    data["volume"]
)

ad = accumulation_distribution(

    data["high"],

    data["low"],

    data["close"],

    data["volume"]
)

obv = on_balance_volume(

    data["close"],

    data["volume"]
)

ad_mom = flow_momentum(

    ad
)

obv_mom = flow_momentum(

    obv
)

# =====================================================
# SCORE
# =====================================================

score = smart_money_score(

    vz.iloc[-1],

    ad_mom.iloc[-1],

    obv_mom.iloc[-1]
)

classification = classify_flow(

    score
)

# =====================================================
# RESULTS
# =====================================================

print("\nSMART MONEY ANALYSIS")

print("Volume Z-Score:", vz.iloc[-1])

print("AD Momentum:", ad_mom.iloc[-1])

print("OBV Momentum:", obv_mom.iloc[-1])

print("\nSMART MONEY SCORE")

print(score)

print("\nFLOW CLASSIFICATION")

print(classification)