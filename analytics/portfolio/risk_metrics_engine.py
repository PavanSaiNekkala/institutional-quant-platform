from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_DIR = ROOT / "data" / "portfolio"

VAR_FILE = PORTFOLIO_DIR / "portfolio_var.csv"

BETA_FILE = PORTFOLIO_DIR / "beta_metrics.csv"

CONCENTRATION_FILE = PORTFOLIO_DIR / "concentration_risk.csv"

OUTPUT_FILE = PORTFOLIO_DIR / "risk_metrics.csv"

print("\n📥 Loading Risk Files")

frames = []

for file in [
    VAR_FILE,
    BETA_FILE,
    CONCENTRATION_FILE,
]:
    if not file.exists():
        print(f"⚠ Missing: {file.name}")
        continue

    df = pd.read_csv(file)

    frames.append(df)

if len(frames) == 0:
    raise ValueError("No risk files found.")

risk_df = pd.concat(frames, ignore_index=True)

risk_df.to_csv(OUTPUT_FILE, index=False)

print("\n✅ Risk Metrics Generated")

print(f"\nSaved: {OUTPUT_FILE}")

print("\nRisk Summary:\n")

print(risk_df)
