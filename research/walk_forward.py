import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# =========================================================
# FEATURE ENGINEERING
# =========================================================


def build_features(prices):

    df = pd.DataFrame()

    df["returns"] = prices.pct_change()

    df["momentum"] = prices / prices.shift(20)

    df["volatility"] = df["returns"].rolling(20).std()

    df["target"] = df["returns"].shift(-1)

    return df.dropna()


# =========================================================
# WALK-FORWARD VALIDATION
# =========================================================


def walk_forward_validation(prices, train_window=200, test_window=50):

    df = build_features(prices)

    X = df[["momentum", "volatility"]]

    y = df["target"]

    results = []

    start = 0

    while start + train_window + test_window <= len(df):
        # =================================================
        # SPLIT
        # =================================================

        X_train = X.iloc[start : start + train_window]

        y_train = y.iloc[start : start + train_window]

        X_test = X.iloc[start + train_window : start + train_window + test_window]

        y_test = y.iloc[start + train_window : start + train_window + test_window]

        # =================================================
        # TRAIN
        # =================================================

        model = LinearRegression()

        model.fit(X_train, y_train)

        preds = model.predict(X_test)

        mse = mean_squared_error(y_test, preds)

        results.append(
            {
                "Train Start": start,
                "Train End": start + train_window,
                "Test End": start + train_window + test_window,
                "MSE": mse,
            }
        )

        start += test_window

    return pd.DataFrame(results)


# =========================================================
# VALIDATION SUMMARY
# =========================================================


def validation_summary(results):

    return {
        "Average MSE": round(results["MSE"].mean(), 6),
        "Best MSE": round(results["MSE"].min(), 6),
        "Worst MSE": round(results["MSE"].max(), 6),
        "Validation Runs": len(results),
    }
