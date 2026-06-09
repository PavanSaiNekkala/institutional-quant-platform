from pathlib import Path

import duckdb

DB_DIR = Path("data/duckdb")
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "institutional_quant.db"


class Database:
    @staticmethod
    def connection():
        return duckdb.connect(str(DB_PATH))
