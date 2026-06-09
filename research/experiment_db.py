import sqlite3
from datetime import datetime

import pandas as pd

# =========================================================
# DATABASE PATH
# =========================================================

DB_PATH = "research_lab.db"

# =========================================================
# INITIALIZE DATABASE
# =========================================================


def initialize_db():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS experiments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            experiment_name TEXT,

            model TEXT,

            metric REAL,

            status TEXT,

            timestamp TEXT
        )

    """)

    conn.commit()

    conn.close()


# =========================================================
# INSERT EXPERIMENT
# =========================================================


def insert_experiment(experiment_name, model, metric, status="ACTIVE"):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """

        INSERT INTO experiments (

            experiment_name,

            model,

            metric,

            status,

            timestamp

        )

        VALUES (?, ?, ?, ?, ?)

    """,
        (experiment_name, model, metric, status, timestamp),
    )

    conn.commit()

    conn.close()


# =========================================================
# LOAD EXPERIMENTS
# =========================================================


def load_experiments():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("SELECT * FROM experiments", conn)

    conn.close()

    return df


# =========================================================
# UPDATE STATUS
# =========================================================


def update_status(experiment_id, status):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """

        UPDATE experiments

        SET status = ?

        WHERE id = ?

    """,
        (status, experiment_id),
    )

    conn.commit()

    conn.close()
