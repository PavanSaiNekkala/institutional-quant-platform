from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = ROOT_DIR / "data" / "processed" / "factor_model_rankings.csv"

OUTPUT_FILE = ROOT_DIR / "data" / "models" / "ml_alpha_predictions.csv"

MODEL_METRICS_FILE = ROOT_DIR / "data" / "models" / "ml_model_metrics.csv"

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Factor Data...")

df = pd.read_csv(INPUT_FILE)

print("✅ Data Loaded")

# =========================================================
# CLEAN COLUMNS
# =========================================================

df.columns = df.columns.str.strip()

# =========================================================
# REQUIRED FEATURES
# =========================================================

required_cols = ["Momentum", "Sharpe", "ALPHA_SCORE", "MULTI_FACTOR_SCORE"]

for col in required_cols:
    if col not in df.columns:
        raise Exception(f"\n❌ Missing Required Column: {col}")

# =========================================================
# OPTIONAL FEATURES
# =========================================================

optional_cols = ["RS_30D", "RS_60D", "RS_ACCELERATION", "VOL_ADJ_RS", "SECTOR_SCORE"]

features = required_cols.copy()

for col in optional_cols:
    if col in df.columns:
        features.append(col)

# =========================================================
# CLEAN DATA
# =========================================================

df = df.replace([np.inf, -np.inf], np.nan)

df = df.dropna(subset=features)

# =========================================================
# SYNTHETIC TARGET
# =========================================================

print("\n🧠 Building Alpha Prediction Target...")

df["FUTURE_ALPHA"] = (
    (df["Momentum"] * 0.35) + (df["Sharpe"] * 0.25) + (df["MULTI_FACTOR_SCORE"] * 0.40)
)

# =========================================================
# FEATURE MATRIX
# =========================================================

X = df[features]

y = df["FUTURE_ALPHA"]

# =========================================================
# TRAIN TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

# =========================================================
# RANDOM FOREST MODEL
# =========================================================

print("\n🤖 Training Institutional ML Model...")

model = RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1)

model.fit(X_train, y_train)

# =========================================================
# PREDICTIONS
# =========================================================

predictions = model.predict(X)

df["ML_PREDICTED_ALPHA"] = predictions

# =========================================================
# FEATURE IMPORTANCE
# =========================================================

importance_df = pd.DataFrame({"Feature": features, "Importance": model.feature_importances_})

importance_df = importance_df.sort_values(by="Importance", ascending=False)

# =========================================================
# MODEL EVALUATION
# =========================================================

test_predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, test_predictions)

# =========================================================
# FINAL RANKING
# =========================================================

df = df.sort_values(by="ML_PREDICTED_ALPHA", ascending=False)

df["ML_RANK"] = range(1, len(df) + 1)

# =========================================================
# ROUNDING
# =========================================================

df["ML_PREDICTED_ALPHA"] = df["ML_PREDICTED_ALPHA"].round(4)

importance_df["Importance"] = importance_df["Importance"].round(4)

# =========================================================
# SAVE OUTPUTS
# =========================================================

df.to_csv(OUTPUT_FILE, index=False)

metrics_df = pd.DataFrame(
    {
        "Metric": ["Mean Absolute Error", "Training Samples", "Testing Samples", "Feature Count"],
        "Value": [round(mae, 4), len(X_train), len(X_test), len(features)],
    }
)

metrics_df.to_csv(MODEL_METRICS_FILE, index=False)

# =========================================================
# OUTPUT
# =========================================================

print("\n✅ Institutional ML Alpha Engine Complete")

print(f"\n📁 Predictions Saved To:\n{OUTPUT_FILE}")

print(f"\n📁 Metrics Saved To:\n{MODEL_METRICS_FILE}")

print("\n📊 MODEL METRICS:\n")

print(f"Mean Absolute Error: {mae:.4f}")

print(f"Training Samples: {len(X_train)}")

print(f"Testing Samples: {len(X_test)}")

print("\n🏆 FEATURE IMPORTANCE:\n")

print(importance_df)

print("\n🏆 TOP ML ALPHA STOCKS:\n")

print(df[["ML_RANK", "Symbol", "Sector", "ML_PREDICTED_ALPHA"]].head(20))
