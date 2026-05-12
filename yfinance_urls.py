import pandas as pd
import yfinance as yf
import time
from pathlib import Path

# =====================================================
# WINDOWS DOWNLOADS PATH
# =====================================================
downloads_path = Path.home() / "Downloads"

# =====================================================
# INPUT / OUTPUT FILES
# =====================================================
INPUT_FILE = downloads_path / "valid_stocks.xlsx"
OUTPUT_FILE = downloads_path / "yfinance_stock_urls.xlsx"

# =====================================================
# CHECK FILE EXISTS
# =====================================================
if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"\nFile not found:\n{INPUT_FILE}"
    )

# =====================================================
# READ INPUT FILE
# =====================================================
df = pd.read_excel(INPUT_FILE)

# =====================================================
# DETECT STOCK COLUMN
# =====================================================
possible_cols = [
    "stock",
    "symbol",
    "ticker",
    "stocks",
    "yfinance_symbol"
]

stock_col = None

for col in df.columns:

    if str(col).strip().lower() in possible_cols:
        stock_col = col
        break

# Fallback to first column
if stock_col is None:
    stock_col = df.columns[0]

print(f"\nUsing Stock Column: {stock_col}")

# =====================================================
# STOCK LIST
# =====================================================
stocks = (
    df[stock_col]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
    .tolist()
)

print(f"\nTotal Stocks Found: {len(stocks)}")

# =====================================================
# GENERATE URLS
# =====================================================
def generate_urls(stock):

    return {

        "YahooFinancePage":
            f"https://finance.yahoo.com/quote/{stock}",

        "QuoteAPI":
            f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={stock}",

        "ChartAPI":
            f"https://query1.finance.yahoo.com/v8/finance/chart/{stock}",

        "FinancialsAPI":
            (
                "https://query2.finance.yahoo.com/"
                f"v10/finance/quoteSummary/{stock}"
                "?modules=financialData"
            ),

        "BalanceSheetAPI":
            (
                "https://query2.finance.yahoo.com/"
                f"v10/finance/quoteSummary/{stock}"
                "?modules=balanceSheetHistory"
            ),

        "CashflowAPI":
            (
                "https://query2.finance.yahoo.com/"
                f"v10/finance/quoteSummary/{stock}"
                "?modules=cashflowStatementHistory"
            ),

        "EarningsAPI":
            (
                "https://query2.finance.yahoo.com/"
                f"v10/finance/quoteSummary/{stock}"
                "?modules=earnings"
            ),

        "RecommendationsAPI":
            (
                "https://query2.finance.yahoo.com/"
                f"v10/finance/quoteSummary/{stock}"
                "?modules=recommendationTrend"
            ),

        "InstitutionalHoldersAPI":
            (
                "https://query2.finance.yahoo.com/"
                f"v10/finance/quoteSummary/{stock}"
                "?modules=institutionOwnership"
            ),

        "NewsURL":
            f"https://finance.yahoo.com/quote/{stock}/news"
    }

# =====================================================
# VALIDATE STOCK
# =====================================================
def validate_stock(stock):

    try:

        ticker = yf.Ticker(stock)

        # Fast validation
        hist = ticker.history(period="5d")

        if hist.empty:
            return False, "Delisted / Not Found"

        return True, "Found"

    except Exception as e:

        return False, str(e)

# =====================================================
# PROCESS STOCKS
# =====================================================
results = []

for i, stock in enumerate(stocks):

    print(f"\n[{i+1}/{len(stocks)}] Checking {stock}")

    try:

        found, status = validate_stock(stock)

        if found:

            urls = generate_urls(stock)

            row = {
                "Stock": stock,
                "Status": "Found"
            }

            row.update(urls)

        else:

            row = {
                "Stock": stock,
                "Status": f"Not Found / Delisted ({status})",
                "YahooFinancePage": None,
                "QuoteAPI": None,
                "ChartAPI": None,
                "FinancialsAPI": None,
                "BalanceSheetAPI": None,
                "CashflowAPI": None,
                "EarningsAPI": None,
                "RecommendationsAPI": None,
                "InstitutionalHoldersAPI": None,
                "NewsURL": None
            }

        results.append(row)

        print(row["Status"])

        # Avoid Yahoo rate limit
        time.sleep(0.3)

    except Exception as e:

        print(f"Error: {e}")

        results.append({
            "Stock": stock,
            "Status": f"Error: {e}"
        })

# =====================================================
# CREATE OUTPUT DATAFRAME
# =====================================================
output_df = pd.DataFrame(results)

# =====================================================
# EXPORT TO EXCEL
# =====================================================
output_df.to_excel(
    OUTPUT_FILE,
    index=False
)

print("\n====================================")
print(f"Saved Successfully:")
print(OUTPUT_FILE)
print("====================================")
