import pandas as pd

from core.database import Database

df = pd.read_csv("data/raw/stock_metadata.csv")

# Standardize column names
df.columns = [
    "symbol",
    "sector",
    "industry",
    "market_cap"
]

conn = Database.connection()

conn.execute("DROP TABLE IF EXISTS stock_metadata")

conn.register("stock_metadata_df", df)

conn.execute("""
CREATE TABLE stock_metadata AS
SELECT *
FROM stock_metadata_df
""")

count = conn.execute(
    "SELECT COUNT(*) FROM stock_metadata"
).fetchone()[0]

print(f"Loaded {count} rows into stock_metadata")
