import numpy as np

from ai.adaptive_allocator import adaptive_weights
from ai.ensemble_ai import train_ensemble
from ai.regime_ai import train_regime_ai

# =========================================================
# FORECAST AGENT
# =========================================================


def forecast_agent(prices):

    result = train_ensemble(prices)

    signal = result["EnsembleForecast"]

    return {"Agent": "ForecastAgent", "Signal": signal}


# =========================================================
# REGIME AGENT
# =========================================================


def regime_agent(prices):

    result = train_regime_ai(prices)

    signal = result["Prediction"]

    return {"Agent": "RegimeAgent", "Signal": signal, "Regime": result["Regime"]}


# =========================================================
# RISK AGENT
# =========================================================


def risk_agent(returns):

    volatility = returns.std()

    signal = -volatility

    return {"Agent": "RiskAgent", "Signal": signal}


# =========================================================
# ALLOCATION AGENT
# =========================================================


def allocation_agent(assets, returns):

    allocation, regime = adaptive_weights(assets, returns)

    signal = allocation["Weight"].mean()

    return {"Agent": "AllocationAgent", "Signal": signal, "Regime": regime}


# =========================================================
# COORDINATION ENGINE
# =========================================================


def coordinate_agents(prices, assets):

    returns = prices.pct_change().dropna()

    agents = []

    # =====================================================
    # AGENTS
    # =====================================================

    agents.append(forecast_agent(prices))

    agents.append(regime_agent(prices))

    agents.append(risk_agent(returns))

    agents.append(allocation_agent(assets, returns))

    # =====================================================
    # AGGREGATE SIGNAL
    # =====================================================

    signals = [a["Signal"] for a in agents]

    final_signal = np.mean(signals)

    # =====================================================
    # DECISION
    # =====================================================

    if final_signal > 0.05:
        decision = "BUY"

    elif final_signal < -0.05:
        decision = "SELL"

    else:
        decision = "HOLD"

    return {"Agents": agents, "Final Signal": round(final_signal, 4), "Decision": decision}
