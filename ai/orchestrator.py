import numpy as np
import pandas as pd

from ai.ensemble_ai import (
    train_ensemble
)

from ai.regime_ai import (
    train_regime_ai
)

from ai.deep_forecaster import (
    train_lstm
)

from ai.transformer_forecaster import (
    train_transformer
)

# =========================================================
# SIGNAL NORMALIZATION
# =========================================================

def normalize_signal(

    value
):

    return np.tanh(

        value * 100
    )

# =========================================================
# ORCHESTRATION ENGINE
# =========================================================

def orchestrate_ai(

    prices
):

    # =====================================================
    # ENSEMBLE AI
    # =====================================================

    ensemble = train_ensemble(

        prices
    )

    ensemble_signal = normalize_signal(

        ensemble["EnsembleForecast"]
    )

    # =====================================================
    # REGIME AI
    # =====================================================

    regime = train_regime_ai(

        prices
    )

    regime_signal = normalize_signal(

        regime["Prediction"]
    )

    # =====================================================
    # DEEP LEARNING
    # =====================================================

    lstm = train_lstm(

        prices
    )

    latest_price = prices.iloc[-1]

    lstm_signal = normalize_signal(

        (

            lstm["Prediction"]

            - latest_price
        )

        / latest_price
    )

    # =====================================================
    # TRANSFORMER
    # =====================================================

    transformer = train_transformer(

        prices
    )

    transformer_signal = normalize_signal(

        (

            transformer["Prediction"]

            - latest_price
        )

        / latest_price
    )

    # =====================================================
    # AGGREGATE SIGNAL
    # =====================================================

    final_signal = (

        0.30 * ensemble_signal

        + 0.25 * regime_signal

        + 0.25 * lstm_signal

        + 0.20 * transformer_signal
    )

    # =====================================================
    # DECISION
    # =====================================================

    if final_signal > 0.20:

        decision = "STRONG BUY"

    elif final_signal > 0.05:

        decision = "BUY"

    elif final_signal < -0.20:

        decision = "STRONG SELL"

    elif final_signal < -0.05:

        decision = "SELL"

    else:

        decision = "HOLD"

    return {

        "Ensemble Signal":

            round(ensemble_signal, 4),

        "Regime Signal":

            round(regime_signal, 4),

        "LSTM Signal":

            round(lstm_signal, 4),

        "Transformer Signal":

            round(transformer_signal, 4),

        "Final Signal":

            round(final_signal, 4),

        "Decision":

            decision
    }