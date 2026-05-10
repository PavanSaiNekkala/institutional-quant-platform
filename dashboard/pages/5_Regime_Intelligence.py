import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd

from risk.regime_detection import (
    RegimeDetector
)

# =========================================================
# TITLE
# =========================================================

st.title(

    "Regime Intelligence"
)

engine = RegimeDetector()

result = engine.detect(

    symbol="^NSEI"
)

if result:

    df = pd.DataFrame(

        result.items(),

        columns=[

            "Metric",

            "Value"
        ]
    )

    st.dataframe(

        df,

        use_container_width=True
    )