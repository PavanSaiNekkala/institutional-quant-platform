import numpy as np
import pandas as pd
import yfinance as yf

from core.task_queue import TaskQueue

# =========================================================
# SINGLE RISK SIMULATION
# =========================================================


def monte_carlo_risk(symbol, simulations=1000, horizon=30):

    try:
        data = yf.download(symbol, period="6mo", progress=False, auto_adjust=True)

        if data.empty:
            return None

        close = data["Close"]

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        returns = close.pct_change().dropna()

        if len(returns) < 30:
            return None

        mean_return = returns.mean()

        volatility = returns.std()

        simulated_returns = []

        for _ in range(simulations):
            daily_returns = np.random.normal(mean_return, volatility, horizon)

            cumulative_return = np.prod(1 + daily_returns) - 1

            simulated_returns.append(cumulative_return)

        simulated_returns = np.array(simulated_returns)

        var_95 = np.percentile(simulated_returns, 5)

        expected_shortfall = simulated_returns[simulated_returns <= var_95].mean()

        return {
            "Symbol": symbol,
            "VaR 95": round(var_95, 4),
            "Expected Shortfall": round(expected_shortfall, 4),
            "Mean Simulated Return": round(simulated_returns.mean(), 4),
            "Simulation Volatility": round(simulated_returns.std(), 4),
        }

    except Exception:
        return None


# =========================================================
# DISTRIBUTED RISK ENGINE
# =========================================================


class DistributedRiskEngine:
    def __init__(self):

        self.queue = TaskQueue()

    # =====================================================
    # RUN RISK ANALYSIS
    # =====================================================

    def run_risk_analysis(self, symbols, workers=8):

        self.queue.start_workers(num_workers=workers)

        for symbol in symbols:
            self.queue.add_task(monte_carlo_risk, symbol)

        self.queue.wait_completion()

        self.queue.stop_workers()

        results = [r for r in self.queue.results if r is not None]

        return pd.DataFrame(results)
