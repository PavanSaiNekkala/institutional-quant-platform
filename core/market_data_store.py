import sqlite3
from pathlib import Path

import pandas as pd
import yfinance as yf

# =========================================================
# DATABASE PATH
# =========================================================

DB_PATH = Path("data/market_data.db")

# =========================================================
# DATABASE CONNECTION
# =========================================================


def get_connection():

    DB_PATH.parent.mkdir(exist_ok=True)

    return sqlite3.connect(DB_PATH)


# =========================================================
# SAVE MARKET DATA
# =========================================================


def save_market_data(symbol, period="6mo"):

    conn = get_connection()

    try:
        data = yf.download(symbol, period=period, progress=False, auto_adjust=True, threads=False)

        if data.empty:
            return False

        data.reset_index(inplace=True)

        data["Symbol"] = symbol

        table_name = symbol.replace(".", "_")

        data.to_sql(table_name, conn, if_exists="replace", index=False)

        return True

    except Exception as e:
        print(f"SAVE ERROR: {e}")

        return False

    finally:
        conn.close()


# =========================================================
# LOAD MARKET DATA
# =========================================================


def load_market_data(symbol):

    conn = get_connection()

    try:
        table_name = symbol.replace(".", "_")

        query = f"""

        SELECT *

        FROM {table_name}
        """

        data = pd.read_sql(query, conn)

        return data

    except Exception as e:
        print(f"LOAD ERROR: {e}")

        return pd.DataFrame()

    finally:
        conn.close()
