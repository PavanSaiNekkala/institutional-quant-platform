import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path

# =========================================================
# FILES
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "optimised_portfolio.csv"
)

REGIME_FILE = (
    ROOT
    / "data"
    / "market_regime.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "stoploss_signals.csv"
)

# =========================================================
# SETTINGS
# =========================================================

LOOKBACK_DAYS = 120

EMA_PERIOD = 50

ATR_PERIOD = 20

ATR_MULTIPLIER = 3

HARD_STOP_LOSS = 0.15

# =========================================================
# LOAD PORTFOLIO
# =========================================================

print("\n📥 Loading Portfolio...")

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

if "Symbol" not in portfolio.columns:

    raise ValueError(
        "Symbol column missing"
    )

# =========================================================
# LOAD REGIME
# =========================================================

regime = "NEUTRAL"

if REGIME_FILE.exists():

    try:

        regime_df = pd.read_csv(
            REGIME_FILE
        )

        if "REGIME" in regime_df.columns:

            regime = str(

                regime_df["REGIME"]

                .iloc[0]

            ).upper()

    except:

        pass

print(
    f"\n📊 Market Regime: {regime}"
)

# =========================================================
# SYMBOLS
# =========================================================

symbols = []

for sym in portfolio["Symbol"]:

    sym = str(sym).upper().strip()

    if not sym.endswith(".NS"):

        sym += ".NS"

    symbols.append(sym)

# =========================================================
# DOWNLOAD DATA
# =========================================================

print(
    f"\n📡 Downloading {len(symbols)} stocks..."
)

prices = yf.download(

    tickers=symbols,

    period="1y",

    auto_adjust=True,

    progress=False

)

if prices.empty:

    raise Exception(
        "No price data downloaded."
    )

# =========================================================
# CLOSE
# =========================================================

if isinstance(
    prices.columns,
    pd.MultiIndex
):

    close = prices["Close"]

    high = prices["High"]

    low = prices["Low"]

else:

    close = prices

    high = prices

    low = prices

# =========================================================
# PROCESS
# =========================================================

results = []

for symbol in symbols:

    try:

        c = close[symbol].dropna()

        h = high[symbol].dropna()

        l = low[symbol].dropna()

        if len(c) < EMA_PERIOD:

            continue

        current_price = c.iloc[-1]

        ema50 = (

            c

            .ewm(
                span=EMA_PERIOD,
                adjust=False
            )

            .mean()

            .iloc[-1]

        )

        # ATR

        tr1 = h - l

        tr2 = (

            h

            - c.shift(1)

        ).abs()

        tr3 = (

            l

            - c.shift(1)

        ).abs()

        tr = pd.concat(

            [tr1, tr2, tr3],

            axis=1

        ).max(axis=1)

        atr = (

            tr

            .rolling(
                ATR_PERIOD
            )

            .mean()

            .iloc[-1]

        )

        atr_stop = (

            current_price

            - ATR_MULTIPLIER * atr
        )

        hard_stop = (

            current_price

            * (1 - HARD_STOP_LOSS)
        )

        # =================================================
        # SIGNAL LOGIC
        # =================================================

        action = "HOLD"

        stop_type = "NONE"

        stop_price = np.nan

        if current_price < ema50:

            action = "EXIT"

            stop_type = "EMA50"

            stop_price = ema50

        elif current_price < atr_stop:

            action = "EXIT"

            stop_type = "ATR"

            stop_price = atr_stop

        elif regime == "BEAR":

            action = "REDUCE"

            stop_type = "REGIME"

            stop_price = atr_stop

        results.append({

            "Symbol":
                symbol.replace(
                    ".NS",
                    ""
                ),

            "Current_Price":
                round(
                    current_price,
                    2
                ),

            "EMA50":
                round(
                    ema50,
                    2
                ),

            "ATR":
                round(
                    atr,
                    2
                ),

            "ATR_Stop":
                round(
                    atr_stop,
                    2
                ),

            "Hard_Stop":
                round(
                    hard_stop,
                    2
                ),

            "Stop_Type":
                stop_type,

            "Action":
                action

        })

    except Exception as e:

        print(
            f"⚠️ {symbol}: {e}"
        )

# =========================================================
# OUTPUT
# =========================================================

signals = pd.DataFrame(
    results
)

signals = signals.sort_values(

    by="Action",

    ascending=True

)

# =========================================================
# SAVE
# =========================================================

signals.to_csv(

    OUTPUT_FILE,

    index=False

)

# =========================================================
# REPORT
# =========================================================

print(
    "\n✅ Stop Loss Engine Complete"
)

print(
    "\n📁 Saved:"
)

print(
    OUTPUT_FILE
)

print(
    "\n📊 Action Summary:\n"
)

print(

    signals["Action"]

    .value_counts()

)

print(
    "\n🚨 Exit Signals:\n"
)

print(

    signals[
        signals["Action"]

        != "HOLD"
    ]

)
