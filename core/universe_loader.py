import pandas as pd

# =========================================================
# LOAD RANKED UNIVERSE
# =========================================================


def load_ranked_universe(top_n=100):

    try:
        ranking_df = pd.read_excel("ranked_universe.xlsx")

        symbols = ranking_df["Symbol"].dropna().astype(str).head(top_n).tolist()

        return symbols

    except Exception as e:
        print(f"UNIVERSE LOAD ERROR: {e}")

        return []
