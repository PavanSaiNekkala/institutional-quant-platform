from core.database import Database

conn = Database.connection()

conn.execute("""
CREATE TABLE IF NOT EXISTS stock_metadata (
    symbol VARCHAR,
    sector VARCHAR,
    industry VARCHAR,
    market_cap BIGINT
)
""")

print("Database initialized successfully")
