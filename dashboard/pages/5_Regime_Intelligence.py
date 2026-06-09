import sys
from pathlib import Path

import pandas as pd
import streamlit as st

from risk.regime_detection import RegimeDetector

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

sys.path.append(str(ROOT_DIR))

# =========================================================
# TITLE
# =========================================================

st.title("Regime Intelligence")

engine = RegimeDetector()

result = engine.detect(symbol="^NSEI")

if result:
    df = pd.DataFrame(result.items(), columns=["Metric", "Value"])

    st.dataframe(df, use_container_width=True)
