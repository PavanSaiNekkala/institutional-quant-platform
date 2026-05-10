import sqlite3
import pandas as pd
import json

from pathlib import Path

# =========================================================
# CACHE DATABASE
# =========================================================

CACHE_DB = Path(

    "cache/research_cache.db"
)

# =========================================================
# CONNECTION
# =========================================================

def get_connection():

    CACHE_DB.parent.mkdir(

        exist_ok=True
    )

    return sqlite3.connect(CACHE_DB)

# =========================================================
# INITIALIZE CACHE
# =========================================================

def initialize_cache():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """

        CREATE TABLE IF NOT EXISTS research_cache (

            cache_key TEXT PRIMARY KEY,

            cache_value TEXT
        )

        """
    )

    conn.commit()

    conn.close()

# =========================================================
# SAVE CACHE
# =========================================================

def save_cache(

    key,

    value
):

    conn = get_connection()

    cursor = conn.cursor()

    serialized = json.dumps(

        value
    )

    cursor.execute(

        """

        INSERT OR REPLACE INTO research_cache

        (cache_key, cache_value)

        VALUES (?, ?)

        """,

        (

            key,

            serialized
        )
    )

    conn.commit()

    conn.close()

# =========================================================
# LOAD CACHE
# =========================================================

def load_cache(

    key
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT cache_value

        FROM research_cache

        WHERE cache_key = ?

        """,

        (key,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:

        return json.loads(

            result[0]
        )

    return None