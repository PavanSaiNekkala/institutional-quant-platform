import pandas as pd
import yfinance as yf
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# =====================================================
# INPUT / OUTPUT
# =====================================================

INPUT_FILE = "valid_stocks.xlsx"

OUTPUT_FILE = "updated_stocks.xlsx"

SHEET_NAME = 0

# =====================================================
# LOAD
# =====================================================

print("\nLoading Excel...")

df = pd.read_excel(
    INPUT_FILE,
    sheet_name=SHEET_NAME
)

# =====================================================
# SYMBOL COLUMN
# =====================================================

SYMBOL_COL = "Stock"

if SYMBOL_COL not in df.columns:

    raise ValueError(
        f"{SYMBOL_COL} column not found"
    )

# =====================================================
# CLEAN SYMBOLS
# =====================================================

symbols = (

    df[SYMBOL_COL]

    .dropna()

    .astype(str)

    .str.strip()

    .str.upper()

)

symbols = [

    s

    if s.endswith(".NS")

    else f"{s}.NS"

    for s in symbols

]

print(
    f"\nTotal Stocks: {len(symbols)}"
)

# =====================================================
# VALIDATION FUNCTION
# =====================================================

def validate_stock(symbol):

    try:

        data = yf.download(
            symbol,
            period="1y",
            progress=False,
            auto_adjust=True,
            threads=False
        )

        if data.empty:
            return None

        close_series = data["Close"].dropna()

        volume_series = data["Volume"].dropna()

        if isinstance(close_series, pd.DataFrame):

            close_series = close_series.iloc[:, 0]

        if isinstance(volume_series, pd.DataFrame):

            volume_series = volume_series.iloc[:, 0]

        if len(close_series) == 0:
            return None

        latest_close = round(
            float(close_series.iloc[-1]),
            2
        )

        avg_volume = int(
            volume_series.mean()
        )

        # =====================================
        # ATR / VOLATILITY FILTER
        # =====================================

        high_series = data["High"].dropna()

        low_series = data["Low"].dropna()

        if isinstance(high_series, pd.DataFrame):

            high_series = high_series.iloc[:, 0]

        if isinstance(low_series, pd.DataFrame):

            low_series = low_series.iloc[:, 0]

        atr_pct = (

            (
                high_series - low_series
            )

            / close_series

        ).mean() * 100

        # =====================================
        # FILTER 1 : Penny Stocks
        # =====================================

        if latest_close < 20:
            return None

        # =====================================
        # FILTER 2 : Illiquid Stocks
        # =====================================

        if avg_volume < 50000:
            return None
        
        # =====================================
        # MARKET CAP
        # =====================================

        #ticker = yf.Ticker(symbol)

        #try:

            #market_cap = ticker.fast_info.get(
                #"market_cap",
                #0
            #)

        #except:

            #market_cap = 0
            
        # =====================================
        # FILTER 3 : Market Cap
        # =====================================

        #if market_cap < 2_000_000_000:
            #return None
        
        # =====================================
        # FILTER 4 : Extreme Volatility
        # =====================================

        if atr_pct > 6:
            return None

        # =====================================
        # FILTER 5 : Minimum History
        # =====================================

        if len(data) < 200:
            return None
        
        print(
            f"Valid: {symbol}"
        )

        print(
            f"VALID -> {symbol} | "
            f"Close={latest_close} | "
            f"Vol={avg_volume}"
        )

        return {

            "Symbol": symbol,

            "Close": latest_close,

            "Avg_Volume": avg_volume,

            #"Market_Cap": market_cap,

            "ATR_PCT": round(
                atr_pct,
                2
            ),

            "History_Days": len(data)

        }

    except Exception as e:

        import traceback

        print(
            f"\nERROR SYMBOL: {symbol}"
        )

        traceback.print_exc()

        return None
# =====================================================
# PROCESS
# =====================================================

print(
    "\nChecking Stocks..."
)

updated_stocks = []

with ThreadPoolExecutor(
    max_workers=3
) as executor:

    results = list(

        executor.map(

            validate_stock,

            symbols

        )

    )

for r in results:

    if r is not None:

        updated_stocks.append(r)

# =====================================================
# OUTPUT
# =====================================================

if len(updated_stocks) == 0:

    raise ValueError(
        "No stocks passed validation filters."
    )

updated_df = pd.DataFrame(
    updated_stocks
)

updated_df = updated_df.sort_values(
    [
        #"Market_Cap",
        "Avg_Volume"
    ],
    ascending=False
)

updated_df.to_excel(

    OUTPUT_FILE,

    index=False

)

# =====================================================
# REPORT
# =====================================================

print(
    f"\nupdated Stocks : {len(updated_df)}"
)

print(
    f"Removed Stocks : {len(symbols)-len(updated_df)}"
)

print(
    f"\nSaved:\n{OUTPUT_FILE}"
)