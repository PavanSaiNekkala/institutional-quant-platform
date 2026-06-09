from core.database import Database


class StockRepository:

    @staticmethod
    def get_all():
        conn = Database.connection()

        return conn.execute("""
            SELECT *
            FROM stock_metadata
        """).df()

    @staticmethod
    def get_by_symbol(symbol: str):
        conn = Database.connection()

        return conn.execute("""
            SELECT *
            FROM stock_metadata
            WHERE symbol = ?
        """, [symbol]).df()
