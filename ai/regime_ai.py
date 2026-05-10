import pandas as pd
import numpy as np

from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor
)

from sklearn.linear_model import (
    LinearRegression
)

# =========================================================
# REGIME DETECTION
# =========================================================

def detect_regime(

    returns,

    volatility_threshold=0.02
):

    volatility = returns.std()

    trend = returns.mean()

    if volatility > volatility_threshold:

        return "HIGH_VOL"

    elif trend > 0:

        return "BULL"

    else:

        return "BEAR"

# =========================================================
# FEATURE ENGINEERING
# =========================================================

def build_features(

    prices
):

    df = pd.DataFrame()

    df["returns"] = (

        prices.pct_change()
    )

    df["volatility"] = (

        df["returns"]

        .rolling(20)

        .std()
    )

    df["momentum"] = (

        prices

        / prices.shift(20)
    )

    df["moving_avg"] = (

        prices

        .rolling(20)

        .mean()
    )

    df["target"] = (

        df["returns"]

        .shift(-1)
    )

    df = df.dropna()

    return df

# =========================================================
# REGIME MODEL SELECTION
# =========================================================

def regime_model(

    regime
):

    if regime == "HIGH_VOL":

        return GradientBoostingRegressor(

            random_state=42
        )

    elif regime == "BULL":

        return RandomForestRegressor(

            n_estimators=100,

            random_state=42
        )

    else:

        return LinearRegression()

# =========================================================
# TRAIN REGIME AI
# =========================================================

def train_regime_ai(

    prices
):

    df = build_features(

        prices
    )

    regime = detect_regime(

        df["returns"]
    )

    X = df[[

        "volatility",
        "momentum",
        "moving_avg"
    ]]

    y = df["target"]

    model = regime_model(

        regime
    )

    model.fit(

        X,

        y
    )

    prediction = model.predict(

        X.tail(1)
    )[0]

    return {

        "Regime":

            regime,

        "Prediction":

            prediction,

        "Model":

            model.__class__.__name__
    }