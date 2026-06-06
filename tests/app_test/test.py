import pandas as pd
import numpy as np
import yfinance as yf
import vectorbt as vbt
import xgboost as xgb

print("=================================")
print("INSTITUTIONAL QUANT SETUP ACTIVE")
print("=================================")

print("Pandas:", pd.__version__)
print("NumPy:", np.__version__)
print("VectorBT:", vbt.__version__)
print("XGBoost:", xgb.__version__)

ticker = yf.download(
    "RELIANCE.NS",
    period="5d",
    progress=False
)

print("\nDATA DOWNLOAD SUCCESSFUL")
print(ticker.tail())
