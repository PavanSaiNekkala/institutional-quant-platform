import pandas as pd
import yfinance as yf

# =========================================================
# CONFIG
# =========================================================

INPUT_FILE = "valid_stocks.xlsx"

DOWNLOAD_PERIOD = "2y"

# =========================================================
# STANDARDIZE OHLCV
# =========================================================

def standardize_ohlcv(df):

    if df is None or df.empty:
        return pd.DataFrame()

    if isinstance(df.columns, pd.MultiIndex):

        df.columns = (
            df.columns.get_level_values(0)
        )

    df.columns = [

        str(c).lower().strip()

        for c in df.columns
    ]

    rename_map = {

        "adj close": "close"
    }

    df = df.rename(columns=rename_map)

    required = [

        "open",
        "high",
        "low",
        "close",
        "volume"
    ]

    if not all(
        col in df.columns
        for col in required
    ):
        return pd.DataFrame()

    return df[required].dropna()

# =========================================================
# LOAD SYMBOLS
# =========================================================

def load_symbols():

    try:

        df = pd.read_excel(INPUT_FILE)

        df.columns = (

            df.columns

            .str.upper()

            .str.strip()
        )

        stock_col = None

        for col in [

            "SYMBOL",
            "STOCK",
            "TICKER"
        ]:

            if col in df.columns:

                stock_col = col

                break

        if stock_col is None:

            raise Exception(
                "Stock column missing"
            )

        symbols = (

            df[stock_col]

            .dropna()

            .astype(str)

            .str.upper()

            .str.strip()

            .unique()

            .tolist()
        )

        cleaned = []

        for s in symbols:

            if not s.endswith(".NS"):
                s += ".NS"

            cleaned.append(s)

        return cleaned

    except Exception as e:

        print(f"LOAD ERROR: {e}")

        return [

            "RELIANCE.NS",
            "TCS.NS",
            "INFY.NS"
        ]

# =========================================================
# ETF / INVALID FILTER
# =========================================================

def prefilter_symbols(symbols):

    filtered = []

    blacklist = [

        "ETF",
        "BEES",
        "GOLD",
        "SILVER",
        "LIQUID",
        "INDEX",
        "SETF",
        "JUNIORBEES"
    ]

    for s in symbols:

        if any(
            x in s.upper()
            for x in blacklist
        ):
            continue

        filtered.append(s)

    return filtered

# =========================================================
# BULK DOWNLOAD
# =========================================================

def batch_download(symbols):

    out = {}

    try:

        raw = yf.download(

            tickers=symbols,

            period=DOWNLOAD_PERIOD,

            interval="1d",

            auto_adjust=True,

            progress=False,

            group_by="ticker",

            threads=False
        )

        if isinstance(
            raw.columns,
            pd.MultiIndex
        ):

            for s in symbols:

                try:

                    temp = raw[s]

                    temp = (
                        standardize_ohlcv(temp)
                    )

                    if not temp.empty:

                        out[s] = temp

                except:
                    pass

    except Exception as e:

        print(f"DOWNLOAD ERROR: {e}")

    return out