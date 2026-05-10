import sqlite3
import pandas as pd

from pathlib import Path

# =========================================================
# DATABASE
# =========================================================

DB_PATH = Path(

    "paper_trading/paper_portfolio.db"
)

# =========================================================
# CONNECTION
# =========================================================

def get_connection():

    DB_PATH.parent.mkdir(

        exist_ok=True
    )

    return sqlite3.connect(DB_PATH)

# =========================================================
# INITIALIZE DATABASE
# =========================================================

def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()

    # =====================================================
    # POSITIONS
    # =====================================================

    cursor.execute(

        """

        CREATE TABLE IF NOT EXISTS positions (

            symbol TEXT PRIMARY KEY,

            quantity REAL

        )

        """
    )

    # =====================================================
    # TRADES
    # =====================================================

    cursor.execute(

        """

        CREATE TABLE IF NOT EXISTS trades (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            action TEXT,

            symbol TEXT,

            quantity REAL,

            price REAL,

            value REAL

        )

        """
    )

    # =====================================================
    # CASH
    # =====================================================

    cursor.execute(

        """

        CREATE TABLE IF NOT EXISTS cash (

            id INTEGER PRIMARY KEY,

            balance REAL

        )

        """
    )

    conn.commit()

    conn.close()

# =========================================================
# SAVE CASH
# =========================================================

def save_cash(balance):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """

        INSERT OR REPLACE INTO cash

        (id, balance)

        VALUES (1, ?)

        """,

        (balance,)
    )

    conn.commit()

    conn.close()

# =========================================================
# LOAD CASH
# =========================================================

def load_cash():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        "SELECT balance FROM cash WHERE id = 1"
    )

    result = cursor.fetchone()

    conn.close()

    if result:

        return result[0]

    return 100000

# =========================================================
# SAVE POSITION
# =========================================================

def save_position(

    symbol,

    quantity
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """

        INSERT OR REPLACE INTO positions

        (symbol, quantity)

        VALUES (?, ?)

        """,

        (

            symbol,

            quantity
        )
    )

    conn.commit()

    conn.close()

# =========================================================
# LOAD POSITIONS
# =========================================================

def load_positions():

    conn = get_connection()

    df = pd.read_sql(

        "SELECT * FROM positions",

        conn
    )

    conn.close()

    if df.empty:

        return {}

    return dict(

        zip(

            df["symbol"],

            df["quantity"]
        )
    )

# =========================================================
# SAVE TRADE
# =========================================================

def save_trade(

    action,

    symbol,

    quantity,

    price,

    value
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """

        INSERT INTO trades

        (

            action,

            symbol,

            quantity,

            price,

            value

        )

        VALUES (?, ?, ?, ?, ?)

        """,

        (

            action,

            symbol,

            quantity,

            price,

            value
        )
    )

    conn.commit()

    conn.close()

# =========================================================
# LOAD TRADES
# =========================================================

def load_trades():

    conn = get_connection()

    df = pd.read_sql(

        "SELECT * FROM trades",

        conn
    )

    conn.close()

    return df