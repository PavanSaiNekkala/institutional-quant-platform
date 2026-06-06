import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from analytics.distributed_scan import (
    distributed_scan,
    institutional_distributed_pipeline
)

# =====================================================
# SAMPLE UNIVERSE
# =====================================================

stocks = [

    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "LT.NS",
    "ITC.NS",
    "SUNPHARMA.NS",
    "BHARTIARTL.NS",
    "MARUTI.NS",
    "SBIN.NS",
    "AXISBANK.NS",
    "BAJFINANCE.NS",
    "ASIANPAINT.NS",
    "ULTRACEMCO.NS"
]

# =====================================================
# DISTRIBUTED SCAN
# =====================================================

scan_results = distributed_scan(

    stocks,

    workers=4
)

print("\nDISTRIBUTED SCAN RESULTS")

print(scan_results)

# =====================================================
# FULL PIPELINE
# =====================================================

pipeline_results = (

    institutional_distributed_pipeline(

        stocks
    )
)

print("\nINSTITUTIONAL DISTRIBUTED PIPELINE")

print(pipeline_results)
