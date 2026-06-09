from skopt import gp_minimize
from skopt.space import Real

# =========================================================
# STRATEGY OBJECTIVE
# =========================================================


def strategy_objective(params, returns):

    momentum_weight = params[0]

    volatility_weight = params[1]

    momentum = returns.rolling(20).mean()

    volatility = returns.rolling(20).std()

    signal = momentum_weight * momentum - volatility_weight * volatility

    strategy_returns = signal.shift(1) * returns

    sharpe = strategy_returns.mean() / strategy_returns.std()

    # =====================================================
    # NEGATIVE FOR MINIMIZATION
    # =====================================================

    return -sharpe


# =========================================================
# BAYESIAN OPTIMIZATION
# =========================================================


def optimize_strategy(returns):

    search_space = [Real(0.0, 2.0), Real(0.0, 2.0)]

    result = gp_minimize(
        func=lambda params: strategy_objective(params, returns),
        dimensions=search_space,
        n_calls=20,
        random_state=42,
    )

    best_params = {
        "Momentum Weight": round(result.x[0], 4),
        "Volatility Weight": round(result.x[1], 4),
        "Best Score": round(-result.fun, 4),
    }

    return best_params
