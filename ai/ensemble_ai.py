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
# ENSEMBLE TRAINING
# =========================================================

def train_ensemble(

    prices
):

    df = build_features(

        prices
    )

    X = df[[

        "volatility",
        "momentum",
        "moving_avg"
    ]]

    y = df["target"]

    # =====================================================
    # MODELS
    # =====================================================

    rf = RandomForestRegressor(

        n_estimators=100,

        random_state=42
    )

    gb = GradientBoostingRegressor(

        random_state=42
    )

    lr = LinearRegression()

    # =====================================================
    # TRAIN
    # =====================================================

    rf.fit(X, y)

    gb.fit(X, y)

    lr.fit(X, y)

    latest = X.tail(1)

    rf_pred = rf.predict(latest)[0]

    gb_pred = gb.predict(latest)[0]

    lr_pred = lr.predict(latest)[0]

    # =====================================================
    # WEIGHTED ENSEMBLE
    # =====================================================

    ensemble_prediction = (

        0.4 * rf_pred

        + 0.4 * gb_pred

        + 0.2 * lr_pred
    )

    return {

        "RandomForest":

            rf_pred,

        "GradientBoosting":

            gb_pred,

        "LinearRegression":

            lr_pred,

        "EnsembleForecast":

            ensemble_prediction
    }