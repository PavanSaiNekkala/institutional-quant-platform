import numpy as np
import pandas as pd

# =========================================================
# PERFORMANCE ATTRIBUTION ENGINE
# =========================================================


class PerformanceAttribution:
    def __init__(self):

        pass

    # =====================================================
    # ATTRIBUTION ANALYSIS
    # =====================================================

    def analyze(self, symbols, portfolio_returns, benchmark_returns, weights):

        portfolio_returns = np.array(portfolio_returns)

        benchmark_returns = np.array(benchmark_returns)

        weights = np.array(weights)

        excess_returns = portfolio_returns - benchmark_returns

        allocation_contribution = weights * excess_returns

        total_alpha = excess_returns.sum()

        results = []

        for i in range(len(symbols)):
            results.append(
                {
                    "Symbol": symbols[i],
                    "Portfolio Return": round(portfolio_returns[i], 4),
                    "Benchmark Return": round(benchmark_returns[i], 4),
                    "Excess Return": round(excess_returns[i], 4),
                    "Weight": round(weights[i], 4),
                    "Allocation Contribution": round(allocation_contribution[i], 4),
                }
            )

        df = pd.DataFrame(results)

        summary = {
            "Portfolio Alpha": round(total_alpha, 4),
            "Average Excess Return": round(excess_returns.mean(), 4),
            "Total Allocation Contribution": round(allocation_contribution.sum(), 4),
        }

        return df, summary
