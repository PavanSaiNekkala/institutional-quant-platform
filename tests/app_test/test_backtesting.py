import pandas as pd
import yfinance as yf
import vectorbt as vbt
import quantstats as qs

from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns

print("====================================")
print("INSTITUTIONAL BACKTEST STACK ACTIVE")
print("====================================")

# =====================================================
# DOWNLOAD SAMPLE DATA
# =====================================================

data = yf.download(

    "RELIANCE.NS",

    period="1y",

    progress=False
)

close = data["Close"]

print("\nDATA DOWNLOAD SUCCESS")

# =====================================================
# VECTORBT TEST
# =====================================================

fast_ma = close.rolling(20).mean()

slow_ma = close.rolling(50).mean()

entries = fast_ma > slow_ma

exits = fast_ma < slow_ma

portfolio = vbt.Portfolio.from_signals(

    close,

    entries,

    exits,

    init_cash=100000,

    freq="1D"
)

print("\nVECTORBT TEST SUCCESS")

print(portfolio.stats())

# =====================================================
# QUANTSTATS TEST
# =====================================================

returns = close.pct_change().dropna()

sharpe = qs.stats.sharpe(returns)

print("\nQUANTSTATS TEST SUCCESS")

print("Sharpe Ratio:", sharpe)

# =====================================================
# PYPORTFOLIOOPT TEST
# =====================================================

multi = yf.download(

    ["RELIANCE.NS", "TCS.NS", "INFY.NS"],

    period="1y",

    progress=False
)["Close"]

mu = expected_returns.mean_historical_return(multi)

S = risk_models.sample_cov(multi)

ef = EfficientFrontier(mu, S)

weights = ef.max_sharpe()

print("\nPYPORTFOLIOOPT TEST SUCCESS")

print(weights)

print("\nALL INSTITUTIONAL MODULES VERIFIED")
