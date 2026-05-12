import pandas as pd

# =========================================
# INPUT / OUTPUT
# =========================================
INPUT_FILE = "valid_stocks.xlsx"
OUTPUT_FILE = "pure_equity_stocks.xlsx"

# =========================================
# READ FILE
# =========================================
df = pd.read_excel(INPUT_FILE)

# =========================================
# DETECT STOCK COLUMN
# =========================================
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

if stock_col is None:
    stock_col = df.columns[0]

# =========================================
# CLEAN SYMBOLS
# =========================================
stocks = (
    df[stock_col]
    .dropna()
    .astype(str)
    .str.strip()
)

# =========================================
# REMOVE NON-EQUITY KEYWORDS
# =========================================
remove_keywords = [

    # ETFs / Index
    "ETF",
    "IETF",
    "BEES",
    "INDEX",
    "NIFTY",
    "SENSEX",
    "MIDCAP",
    "SMALLCAP",
    "BANKNIFTY",
    "NEXT50",
    "MOMENTUM",
    "LOWVOL",
    "QUALITY",
    "VALUE",
    "ALPHA",
    "EQUAL",
    "PSUBANK",
    "PVTBANK",

    # Gold / Silver / Commodity
    "GOLD",
    "SILVER",
    "COMMO",
    "GSEC",

    # Liquid / Debt
    "LIQUID",
    "BOND",
    "GILT",

    # Fund / Mutual Fund
    "FUND",
    "MF",

    # Add-ons
    "ADD",
    "CASE",
    "BETA",

    # ETFs commonly ending
    "ETF",

]

# =========================================
# FILTER
# =========================================
pure_stocks = []

for stock in stocks:

    upper_stock = stock.upper()

    remove = False

    for keyword in remove_keywords:

        if keyword in upper_stock:

            remove = True
            break

    if not remove:
        pure_stocks.append(stock)

# =========================================
# REMOVE DUPLICATES
# =========================================
pure_stocks = sorted(list(set(pure_stocks)))

# =========================================
# CREATE OUTPUT
# =========================================
output_df = pd.DataFrame({
    "Stock": pure_stocks
})

# =========================================
# EXPORT
# =========================================
output_df.to_excel(
    OUTPUT_FILE,
    index=False
)

# =========================================
# SUMMARY
# =========================================
print("\n================================")
print(f"Original Symbols : {len(stocks)}")
print(f"Pure Equity Stocks : {len(output_df)}")
print(f"Removed Non-Stocks : {len(stocks) - len(output_df)}")
print("================================")

print(f"\nSaved File: {OUTPUT_FILE}")
