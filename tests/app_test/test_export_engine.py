import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import pandas as pd
import numpy as np

from core.orchestrator import (
    orchestrate_portfolio
)

from core.export_engine import (
    export_rankings,
    export_risk_report,
    export_regime_report,
    export_portfolio
)

# =====================================================
# SAMPLE STOCKS
# =====================================================

stocks = [

    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "LT.NS",
    "ITC.NS",
    "SUNPHARMA.NS"
]

# =====================================================
# RANKINGS
# =====================================================

rankings = orchestrate_portfolio(

    stocks,

    regime="BULL_NORMAL_VOL"
)

# =====================================================
# SAMPLE RISK
# =====================================================

risk_df = pd.DataFrame({

    "Metric": [

        "Volatility",
        "Sharpe",
        "Max Drawdown"
    ],

    "Value": [

        0.18,
        1.45,
        -0.12
    ]
})

# =====================================================
# SAMPLE REGIME
# =====================================================

regime_df = pd.DataFrame({

    "Regime": [

        "BULL_NORMAL_VOL"
    ],

    "Exposure": [

        1.20
    ]
})

# =====================================================
# EXPORTS
# =====================================================

rank_path = export_rankings(

    rankings
)

risk_path = export_risk_report(

    risk_df
)

regime_path = export_regime_report(

    regime_df
)

portfolio_path = export_portfolio(

    rankings.head(5)
)

# =====================================================
# RESULTS
# =====================================================

print("\nEXPORT ENGINE")

print("\nRANKINGS EXPORT")

print(rank_path)

print("\nRISK EXPORT")

print(risk_path)

print("\nREGIME EXPORT")

print(regime_path)

print("\nPORTFOLIO EXPORT")

print(portfolio_path)
