import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

# =========================================================
# PREPARE FEATURES
# =========================================================


def prepare_features(factor_df, target):

    X = factor_df.copy()

    y = target.copy()

    return X, y


# =========================================================
# TRAIN MODEL
# =========================================================


def train_alpha_model(X, y, n_estimators=200, random_state=42):

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state
    )

    model = RandomForestRegressor(
        n_estimators=n_estimators, max_depth=6, min_samples_leaf=5, random_state=random_state
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mse = mean_squared_error(y_test, predictions)

    return (model, mse, predictions)


# =========================================================
# FEATURE IMPORTANCE
# =========================================================


def feature_importance(model, feature_names):

    importance = pd.Series(model.feature_importances_, index=feature_names)

    importance = importance.sort_values(ascending=False)

    return importance


# =========================================================
# AI SCORE
# =========================================================


def ai_alpha_score(model, latest_features):

    prediction = model.predict(latest_features)

    return prediction


# =========================================================
# CONFIDENCE ESTIMATION
# =========================================================


def prediction_confidence(predictions):

    confidence = 1 / (np.std(predictions) + 1e-9)

    return confidence
