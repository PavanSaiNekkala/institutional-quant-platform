from pathlib import Path

import pandas as pd

# =========================================================
# FEATURE DIRECTORY
# =========================================================

FEATURE_DIR = Path("feature_store")

FEATURE_DIR.mkdir(exist_ok=True)

# =========================================================
# FEATURE ENGINEERING
# =========================================================


def generate_features(prices):

    df = pd.DataFrame()

    # =====================================================
    # RETURNS
    # =====================================================

    df["returns"] = prices.pct_change()

    # =====================================================
    # VOLATILITY
    # =====================================================

    df["volatility_20"] = df["returns"].rolling(20).std()

    # =====================================================
    # MOMENTUM
    # =====================================================

    df["momentum_20"] = prices / prices.shift(20)

    # =====================================================
    # MOVING AVERAGES
    # =====================================================

    df["ma_20"] = prices.rolling(20).mean()

    df["ma_50"] = prices.rolling(50).mean()

    # =====================================================
    # RSI
    # =====================================================

    delta = prices.diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()

    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    df["rsi_14"] = 100 - (100 / (1 + rs))

    df = df.dropna()

    return df


# =========================================================
# SAVE FEATURES
# =========================================================


def save_features(symbol, features):

    path = FEATURE_DIR / f"{symbol}.parquet"

    features.to_parquet(path)

    return path


# =========================================================
# LOAD FEATURES
# =========================================================


def load_features(symbol):

    path = FEATURE_DIR / f"{symbol}.parquet"

    return pd.read_parquet(path)


# =========================================================
# FEATURE SUMMARY
# =========================================================


def feature_summary(features):

    return {
        "Rows": len(features),
        "Columns": list(features.columns),
        "Missing Values": int(features.isna().sum().sum()),
    }
