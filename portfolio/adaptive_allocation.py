import numpy as np
import pandas as pd

# =========================================================
# ADAPTIVE ALLOCATION ENGINE
# =========================================================


class AdaptiveAllocation:
    def __init__(self, target_volatility=0.15):

        self.target_volatility = target_volatility

    # =====================================================
    # VOLATILITY TARGETING
    # =====================================================

    def volatility_target_weights(self, volatilities):

        inverse_vol = 1 / np.array(volatilities)

        weights = inverse_vol / inverse_vol.sum()

        return weights

    # =====================================================
    # ADAPTIVE ALLOCATION
    # =====================================================

    def allocate(self, symbols, expected_returns, volatilities):

        expected_returns = np.array(expected_returns)

        volatilities = np.array(volatilities)

        base_weights = self.volatility_target_weights(volatilities)

        alpha_adjustment = expected_returns / np.abs(expected_returns).sum()

        adaptive_weights = base_weights * 0.7 + alpha_adjustment * 0.3

        adaptive_weights = np.clip(adaptive_weights, 0, None)

        adaptive_weights /= adaptive_weights.sum()

        portfolio_volatility = np.dot(adaptive_weights, volatilities)

        scaling_factor = self.target_volatility / portfolio_volatility

        scaled_weights = adaptive_weights * scaling_factor

        scaled_weights /= scaled_weights.sum()

        results = []

        for i in range(len(symbols)):
            results.append(
                {
                    "Symbol": symbols[i],
                    "Expected Return": round(expected_returns[i], 4),
                    "Volatility": round(volatilities[i], 4),
                    "Adaptive Weight": round(scaled_weights[i], 4),
                }
            )

        df = pd.DataFrame(results)

        summary = {
            "Portfolio Volatility": round(portfolio_volatility, 4),
            "Target Volatility": round(self.target_volatility, 4),
            "Scaling Factor": round(scaling_factor, 4),
        }

        return df, summary
