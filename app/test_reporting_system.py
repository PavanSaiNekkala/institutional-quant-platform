import sys
import pandas as pd

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from reporting.institutional_reporting import (
    InstitutionalReportGenerator
)

# =====================================================
# SAMPLE DATA
# =====================================================

regime_data = {

    "Trend": "BULL",

    "Volatility": "LOW VOL"
}

strategy_data = {

    "Strategy": "AGGRESSIVE MOMENTUM"
}

allocation_df = pd.DataFrame({

    "Symbol": [

        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS"
    ],

    "Weight": [

        0.40,
        0.35,
        0.25
    ]
})

metrics_df = pd.DataFrame({

    "Metric": [

        "Sharpe Ratio",
        "Max Drawdown"
    ],

    "Value": [

        1.82,
        -0.12
    ]
})

backtest_metrics = {

    "Sharpe Ratio": 1.82,

    "Max Drawdown": -0.12
}

# =====================================================
# ENGINE
# =====================================================

engine = InstitutionalReportGenerator()

report = engine.generate_report(

    regime_data,

    strategy_data,

    allocation_df,

    backtest_metrics
)

filename = engine.export_excel(

    allocation_df,

    metrics_df
)

# =====================================================
# OUTPUT
# =====================================================

print(

    "\nINSTITUTIONAL REPORT\n"
)

print(report)

print(

    f"\nEXCEL REPORT GENERATED: {filename}"
)