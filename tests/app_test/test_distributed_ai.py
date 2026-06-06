import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from distributed.ai_pipeline import (
    distributed_ai_pipeline
)

# =====================================================
# SAMPLE SYMBOLS
# =====================================================

symbols = [

    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ITC.NS",
    "LT.NS",
    "SBIN.NS",
    "AXISBANK.NS"
]

# =====================================================
# RUN PIPELINE
# =====================================================

if __name__ == "__main__":

    result = distributed_ai_pipeline(

        symbols,

        workers=4
    )

    print("\nDISTRIBUTED AI PIPELINE\n")

    print(result)
