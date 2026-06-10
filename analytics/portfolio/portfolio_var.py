from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = ROOT / "data" / "portfolio" / "optimised_portfolio.csv"

PRICE_CACHE = ROOT / "data" / "cache" / "stock_prices.parquet"

OUTPUT_FILE = ROOT / "data" / "portfolio" / "portfolio_var.csv"

print("\n📥 Loading Portfolio")

portfolio = pd.read_csv(PORTFOLIO_FILE)

prices = pd.read_parquet(PRICE_CACHE)

if isinstance(prices.columns, pd.MultiIndex):
    prices = prices.xs("Close", axis=1, level=-1)

symbols = portfolio["Symbol"].astype(str).tolist()

yf_symbols = [f"{s}.NS" if not s.endswith(".NS") else s for s in symbols]

weights = portfolio["OPT_WEIGHT"].values

prices = prices[[c for c in yf_symbols if c in prices.columns]]

returns = prices.pct_change(fill_method=None).dropna()

portfolio_returns = returns.dot(weights[: len(returns.columns)])

var95 = np.percentile(portfolio_returns, 5)
var99 = np.percentile(portfolio_returns, 1)

cvar95 = portfolio_returns[portfolio_returns <= var95].mean()
cvar99 = portfolio_returns[portfolio_returns <= var99].mean()

output = pd.DataFrame(
    {
        "Metric": [
            "VaR_95",
            "VaR_99",
            "CVaR_95",
            "CVaR_99",
        ],
        "Value": [
            var95,
            var99,
            cvar95,
            cvar99,
        ],
    }
)

output.to_csv(OUTPUT_FILE, index=False)

print(output)
