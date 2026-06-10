from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = ROOT / "data" / "portfolio" / "optimised_portfolio.csv"

PRICE_CACHE = ROOT / "data" / "cache" / "stock_prices.parquet"

OUTPUT_FILE = ROOT / "data" / "portfolio" / "beta_metrics.csv"

portfolio = pd.read_csv(PORTFOLIO_FILE)

prices = pd.read_parquet(PRICE_CACHE)

if isinstance(prices.columns, pd.MultiIndex):
    prices = prices.xs("Close", axis=1, level=-1)

weights = portfolio["OPT_WEIGHT"].values

symbols = [
    f"{x}.NS" if not x.endswith(".NS") else x
    for x in portfolio["Symbol"]
]

prices = prices[[x for x in symbols if x in prices.columns]]

returns = prices.pct_change(fill_method=None).dropna()

portfolio_returns = returns.dot(weights[: len(returns.columns)])

benchmark = returns.mean(axis=1)

cov = np.cov(portfolio_returns, benchmark)[0][1]

beta = cov / np.var(benchmark)

pd.DataFrame(
    {
        "Metric": ["Portfolio_Beta"],
        "Value": [beta],
    }
).to_csv(OUTPUT_FILE, index=False)

print(f"\nPortfolio Beta: {beta:.2f}")
