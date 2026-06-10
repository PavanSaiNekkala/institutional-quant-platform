from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]

MASTER_SOURCE = (
    ROOT_DIR
    / "data"
    / "master"
    / "security_master_source.csv"
)

METADATA_FILE = (
    ROOT_DIR
    / "data"
    / "raw"
    / "stock_metadata.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "raw"
    / "security_master.csv"
)

print("\n🏗 Building Security Master...")

master = pd.read_csv(MASTER_SOURCE)

metadata = pd.read_csv(METADATA_FILE)

master["Symbol"] = (
    master["Symbol"]
    .astype(str)
    .str.upper()
    .str.strip()
)

metadata["Symbol"] = (
    metadata["Symbol"]
    .astype(str)
    .str.upper()
    .str.replace(".NS", "", regex=False)
    .str.strip()
)

security_master = master.merge(
    metadata[["Symbol", "Market_Cap"]],
    on="Symbol",
    how="left"
)

security_master["Market_Cap"] = (
    pd.to_numeric(
        security_master["Market_Cap"],
        errors="coerce"
    )
    .fillna(0)
)

security_master.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n✅ Security Master Created")

print("Rows:", len(security_master))
print(security_master.head())
