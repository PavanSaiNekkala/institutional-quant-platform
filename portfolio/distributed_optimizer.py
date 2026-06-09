import numpy as np
import pandas as pd
import yfinance as yf

from core.task_queue import TaskQueue

# =========================================================
# SINGLE PORTFOLIO SIMULATION
# =========================================================


def simulate_portfolio(symbols, period="6mo"):

    try:
        prices = pd.DataFrame()

        for symbol in symbols:
            data = yf.download(symbol, period=period, progress=False, auto_adjust=True)

            if data.empty:
                continue

            close = data["Close"]

            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]

            prices[symbol] = close

        prices = prices.dropna()

        if prices.empty:
            return None

        returns = prices.pct_change().dropna()

        mean_returns = returns.mean() * 252

        cov_matrix = returns.cov() * 252

        num_assets = len(prices.columns)

        weights = np.random.random(num_assets)

        weights /= np.sum(weights)

        portfolio_return = np.dot(weights, mean_returns)

        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

        sharpe_ratio = portfolio_return / portfolio_volatility

        return {
            "Symbols": list(prices.columns),
            "Weights": np.round(weights, 4).tolist(),
            "Return": round(portfolio_return, 4),
            "Volatility": round(portfolio_volatility, 4),
            "Sharpe": round(sharpe_ratio, 4),
        }

    except Exception:
        return None


# =========================================================
# DISTRIBUTED OPTIMIZATION
# =========================================================


class DistributedOptimizer:
    def __init__(self):

        self.queue = TaskQueue()

    # =====================================================
    # RUN OPTIMIZATION
    # =====================================================

    def optimize(self, symbols, simulations=100, workers=8):

        self.queue.start_workers(num_workers=workers)

        for _ in range(simulations):
            self.queue.add_task(simulate_portfolio, symbols)

        self.queue.wait_completion()

        self.queue.stop_workers()

        results = [r for r in self.queue.results if r is not None]

        df = pd.DataFrame(results)

        if df.empty:
            return df

        return df.sort_values(by="Sharpe", ascending=False)
