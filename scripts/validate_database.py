from core.database import Database

conn = Database.connection()

print("\nRow Count")
print(
    conn.execute(
        "SELECT COUNT(*) FROM stock_metadata"
    ).fetchall()
)

print("\nTop 10 Stocks")
print(
    conn.execute(
        """
        SELECT *
        FROM stock_metadata
        LIMIT 10
        """
    ).df()
)

print("\nLargest Market Caps")
print(
    conn.execute(
        """
        SELECT symbol, market_cap
        FROM stock_metadata
        ORDER BY market_cap DESC
        LIMIT 10
        """
    ).df()
)
