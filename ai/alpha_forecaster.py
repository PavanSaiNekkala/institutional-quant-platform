import pandas as pd
import numpy as np

from sklearn.ensemble import (
    RandomForestRegressor
)

from sklearn.model_selection import (
    train_test_split
)

from sklearn.metrics import (
    mean_squared_error
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
# TRAIN MODEL
# =========================================================

def train_alpha_model(

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

    X_train, X_test, y_train, y_test = (

        train_test_split(

            X,

            y,

            test_size=0.2,

            shuffle=False
        )
    )

    model = RandomForestRegressor(

        n_estimators=100,

        random_state=42
    )

    model.fit(

        X_train,

        y_train
    )

    predictions = model.predict(

        X_test
    )

    mse = mean_squared_error(

        y_test,

        predictions
    )

    return {

        "model":

            model,

        "mse":

            mse,

        "features":

            X_test,

        "predictions":

            predictions
    }

# =========================================================
# FORECAST NEXT RETURN
# =========================================================

def forecast_next_return(

    model,

    latest_features
):

    prediction = model.predict(

        latest_features
    )

    return prediction[0]