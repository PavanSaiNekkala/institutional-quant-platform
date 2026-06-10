from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = ROOT_DIR / "data/raw/symbol_metadata.csv"

OUTPUT_FILE = (
    ROOT_DIR
    / "data/master/security_master_source.csv"
)

print("\nBuilding Security Master Source...")

df = pd.read_csv(INPUT_FILE)

df.columns = df.columns.str.strip()

required_cols = [
    "symbol",
    "company_name",
    "sector",
    "industry",
]

missing = [
    c for c in required_cols
    if c not in df.columns
]

if missing:
    raise Exception(
        f"Missing columns: {missing}"
    )

master = df[required_cols].copy()

master["Symbol"] = (
    master["symbol"]
    .astype(str)
    .str.upper()
    .str.replace(".NS", "", regex=False)
    .str.strip()
)

master = (
    master
    .drop_duplicates("Symbol")
    .sort_values("Symbol")
)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

master.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n✅ Security Master Source Created")

print(f"Rows: {len(master):,}")

print(f"\nSaved:\n{OUTPUT_FILE}")
