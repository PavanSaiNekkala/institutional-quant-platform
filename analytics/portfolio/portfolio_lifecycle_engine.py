from pathlib import Path

import pandas as pd

# =========================================================
# FILES
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = ROOT / "data" / "optimised_portfolio.csv"

TRADE_HISTORY_FILE = ROOT / "data" / "trade_history.csv"

CURRENT_POSITIONS_FILE = ROOT / "data" / "current_positions.csv"

EXITED_POSITIONS_FILE = ROOT / "data" / "exited_positions.csv"

LIFECYCLE_FILE = ROOT / "data" / "portfolio_lifecycle.csv"
EXIT_HISTORY_FILE = ROOT / "data" / "exit_history.csv"
# =========================================================
# LOAD PORTFOLIO
# =========================================================

print("\n📥 Loading Portfolio...")

portfolio = pd.read_csv(PORTFOLIO_FILE)

portfolio["Symbol"] = portfolio["Symbol"].astype(str).str.upper().str.strip()

# =========================================================
# POSITION REGISTRY
# =========================================================

POSITION_REGISTRY_FILE = ROOT / "data" / "position_registry.csv"

if POSITION_REGISTRY_FILE.exists():
    registry = pd.read_csv(POSITION_REGISTRY_FILE)

    registry["Entry_Date"] = pd.to_datetime(registry["Entry_Date"])

    previous_symbols = set(registry["Symbol"])

else:
    registry = pd.DataFrame(columns=["Symbol", "Entry_Date"])

    previous_symbols = set()

# =========================================================
# CURRENT POSITIONS
# =========================================================

current_symbols = set(portfolio["Symbol"])
exited_symbols = list(previous_symbols - current_symbols)
# =========================================================
# UPDATE REGISTRY
# =========================================================

existing_symbols = set(registry["Symbol"])

today = pd.Timestamp.today().normalize()

for symbol in current_symbols:
    if symbol not in existing_symbols:
        registry.loc[len(registry)] = [symbol, today]

# =========================================================
# EXIT HISTORY
# =========================================================

exit_rows = []

for symbol in exited_symbols:
    row = registry[registry["Symbol"] == symbol]

    if len(row):
        entry_date = row.iloc[0]["Entry_Date"]

        exit_date = pd.Timestamp.today()

        holding_days = (exit_date - entry_date).days

        exit_rows.append(
            {
                "Symbol": symbol,
                "Entry_Date": entry_date,
                "Exit_Date": exit_date,
                "Holding_Days": holding_days,
            }
        )

if len(exit_rows):
    exit_df = pd.DataFrame(exit_rows)

    if Path(EXIT_HISTORY_FILE).exists():
        old_exit = pd.read_csv(EXIT_HISTORY_FILE)

        exit_df = pd.concat([old_exit, exit_df], ignore_index=True)

    exit_df.to_csv(EXIT_HISTORY_FILE, index=False)
registry.to_csv(POSITION_REGISTRY_FILE, index=False)
print("\n📊 Registry Stats")

print(f"Tracked Positions: {len(registry)}")

print(f"New Positions: {len(current_symbols - previous_symbols)}")

print(f"Exited Positions: {len(exited_symbols)}")

entry_dates = dict(
    zip(
        registry["Symbol"],
        registry["Entry_Date"],
        strict=False,
    )
)

registry = registry[registry["Symbol"].isin(current_symbols)]
exited_df = pd.DataFrame({"Symbol": exited_symbols, "Status": "EXITED"})


# =========================================================
# CURRENT POSITIONS TABLE
# =========================================================

current_rows = []

today = pd.Timestamp.today()

for _, row in portfolio.iterrows():
    symbol = row["Symbol"]

    entry_date = entry_dates.get(symbol, pd.NaT)

    if pd.notna(entry_date):
        holding_days = (today - entry_date).days

    else:
        holding_days = None

    current_rows.append(
        {
            "Symbol": symbol,
            "Entry_Date": entry_date,
            "Holding_Days": holding_days,
            "Portfolio_Weight": row.get("OPTIMAL_WEIGHT", row.get("FINAL_WEIGHT", None)),
            "Status": "ACTIVE",
        }
    )

current_df = pd.DataFrame(current_rows)

# =========================================================
# LIFECYCLE TABLE
# =========================================================

lifecycle_rows = []

for _, row in current_df.iterrows():
    lifecycle_rows.append(
        {"Symbol": row["Symbol"], "Lifecycle_Stage": "HELD", "Holding_Days": row["Holding_Days"]}
    )

for _, row in exited_df.iterrows():
    lifecycle_rows.append(
        {"Symbol": row["Symbol"], "Lifecycle_Stage": "EXITED", "Holding_Days": None}
    )

lifecycle_df = pd.DataFrame(lifecycle_rows)

# =========================================================
# SAVE
# =========================================================

current_df.to_csv(CURRENT_POSITIONS_FILE, index=False)

exited_df.to_csv(EXITED_POSITIONS_FILE, index=False)

lifecycle_df.to_csv(LIFECYCLE_FILE, index=False)

# =========================================================
# REPORT
# =========================================================

print("\n✅ Portfolio Lifecycle Complete")

print("\n📁 Files Saved:")

print(CURRENT_POSITIONS_FILE)

print(EXITED_POSITIONS_FILE)

print(LIFECYCLE_FILE)
print(EXIT_HISTORY_FILE)
print(f"\n📊 Active Positions: {len(current_df)}")

print(f"📊 Exited Positions: {len(exited_df)}")

print("\n🏆 Current Holdings:\n")

print(current_df.head(20))
