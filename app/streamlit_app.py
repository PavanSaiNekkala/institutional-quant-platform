# =========================================================
# FILE: app/streamlit_app.py
# FINAL INSTITUTIONAL QUANT RESEARCH PLATFORM
# =========================================================

import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

from core.live_regime import (
    detect_market_regime
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(

    page_title="Institutional Quant Platform",

    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title(

    "🏦 Institutional Quant Research Platform"
)

st.markdown("---")

# =========================================================
# CACHE LIVE REGIME
# =========================================================

@st.cache_data(ttl=1800)
def cached_regime():

    return detect_market_regime()


regime = cached_regime()

# =========================================================
# REGIME DISPLAY
# =========================================================

if "BULLISH" in regime:

    st.success(

        f"📈 Live Market Regime: {regime}"
    )

elif "BEARISH" in regime:

    st.error(

        f"📉 Live Market Regime: {regime}"
    )

else:

    st.warning(

        f"📊 Live Market Regime: {regime}"
    )

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header(

    "Institutional Controls"
)

top_n = st.sidebar.slider(

    "Top Stocks",

    25,

    500,

    100
)

max_universe = st.sidebar.slider(

    "Universe Limit",

    100,

    2000,

    500,

    step=100
)

# =========================================================
# LOAD STOCK UNIVERSE
# =========================================================

universe_path = (

    ROOT_DIR
    / "data"
    / "valid_stocks.xlsx"
)

try:

    universe_df = pd.read_excel(

        universe_path
    )

    stocks = (

        universe_df.iloc[:, 0]

        .dropna()

        .astype(str)

        .unique()

        .tolist()
    )

    stocks = [

        stock.strip().upper()

        for stock in stocks

        if ".NS" in stock
    ]

    stocks = list(

        dict.fromkeys(stocks)
    )

    stocks = stocks[:max_universe]

except Exception as e:

    st.error(

        f"Universe load failed: {e}"
    )

    st.stop()

# =========================================================
# PUBLIC VS PRIVATE SECTOR MAP
# =========================================================

SECTOR_MAP = {

    "PRIVATE_BANKS": [

        "HDFCBANK.NS",
        "ICICIBANK.NS",
        "AXISBANK.NS",
        "KOTAKBANK.NS",
        "INDUSINDBK.NS",
        "IDFCFIRSTB.NS",
        "AUBANK.NS",
        "BANDHANBNK.NS",
        "FEDERALBNK.NS"
    ],

    "PSU_BANKS": [

        "SBIN.NS",
        "BANKBARODA.NS",
        "PNB.NS",
        "CANBK.NS",
        "UNIONBANK.NS",
        "IOB.NS",
        "BANKINDIA.NS"
    ],

    "PRIVATE_IT": [

        "TCS.NS",
        "INFY.NS",
        "WIPRO.NS",
        "HCLTECH.NS",
        "TECHM.NS",
        "LTIM.NS",
        "PERSISTENT.NS",
        "COFORGE.NS",
        "KPITTECH.NS"
    ],

    "PRIVATE_FMCG": [

        "HINDUNILVR.NS",
        "NESTLEIND.NS",
        "BRITANNIA.NS",
        "DABUR.NS",
        "MARICO.NS",
        "COLPAL.NS"
    ],

    "PRIVATE_AUTO": [

        "MARUTI.NS",
        "TATAMOTORS.NS",
        "M&M.NS",
        "BAJAJ-AUTO.NS",
        "HEROMOTOCO.NS",
        "TVSMOTOR.NS"
    ],

    "PRIVATE_PHARMA": [

        "SUNPHARMA.NS",
        "DRREDDY.NS",
        "CIPLA.NS",
        "DIVISLAB.NS",
        "LUPIN.NS",
        "ZYDUSLIFE.NS"
    ],

    "PRIVATE_ENERGY": [

        "RELIANCE.NS",
        "ATGL.NS",
        "PETRONET.NS"
    ],

    "PSU_ENERGY": [

        "ONGC.NS",
        "IOC.NS",
        "BPCL.NS",
        "HINDPETRO.NS",
        "GAIL.NS",
        "NTPC.NS",
        "POWERGRID.NS"
    ],

    "PSU_DEFENCE": [

        "HAL.NS",
        "BEL.NS",
        "BDL.NS",
        "MAZDOCK.NS",
        "COCHINSHIP.NS"
    ],

    "PRIVATE_METALS": [

        "TATASTEEL.NS",
        "JSWSTEEL.NS",
        "HINDALCO.NS",
        "VEDL.NS"
    ],

    "PSU_METALS": [

        "SAIL.NS",
        "NMDC.NS",
        "NATIONALUM.NS",
        "MOIL.NS"
    ],

    "PRIVATE_REALTY": [

        "DLF.NS",
        "LODHA.NS",
        "PRESTIGE.NS",
        "OBEROIRLTY.NS"
    ],

    "PRIVATE_CONSUMER": [

        "TITAN.NS",
        "DIXON.NS",
        "VOLTAS.NS",
        "HAVELLS.NS"
    ],

    "PRIVATE_CHEMICALS": [

        "PIDILITIND.NS",
        "SRF.NS",
        "AARTIIND.NS",
        "DEEPAKNTR.NS"
    ]
}

# =========================================================
# SIDEBAR METRIC
# =========================================================

st.sidebar.metric(

    "Universe Size",

    len(stocks)
)

# =========================================================
# SAFE ROUND
# =========================================================

def safe_round(value, digits=4):

    try:

        if value is None:
            return 0

        if np.isnan(value):
            return 0

        if np.isinf(value):
            return 0

        return round(float(value), digits)

    except Exception:

        return 0

# =========================================================
# STOCK ANALYZER
# =========================================================

def analyze_stock(symbol, regime):

    time.sleep(0.25)

    try:

        ticker = yf.Ticker(symbol)

        # =================================================
        # FAST INFO
        # =================================================

        try:

            fast_info = ticker.fast_info

        except Exception:

            fast_info = {}

        market_cap = fast_info.get(

            "market_cap",

            0
        )

        if market_cap is None:

            market_cap = 0

        # =================================================
        # AUTO SECTOR DETECTION
        # =================================================

        sector = "OTHER"

        for sec, members in SECTOR_MAP.items():

            if symbol in members:

                sector = sec

                break

        # =================================================
        # DEFAULT FUNDAMENTALS
        # =================================================

        revenue_growth = 0
        profit_margin = 0
        roe = 0
        operating_margin = 0
        debt_to_equity = 0
        dividend_yield = 0

        # =================================================
        # PRICE DATA
        # =================================================

        data = yf.download(

            symbol,

            period="6mo",

            interval="1d",

            progress=False,

            auto_adjust=True,

            threads=False
        )

        if data.empty:

            return None

        close = data["Close"]

        if isinstance(close, pd.DataFrame):

            close = close.iloc[:, 0]

        close = close.dropna()

        if len(close) < 50:

            return None

        returns = close.pct_change().dropna()

        if len(returns) < 20:

            return None

        # =================================================
        # TECHNICALS
        # =================================================

        momentum = (

            close.iloc[-1]
            / close.iloc[-20]
        ) - 1

        volatility = (

            returns.std()
            * np.sqrt(252)
        )

        if (

            returns.std() is None or

            returns.std() == 0
        ):

            sharpe = 0

        else:

            sharpe = (

                returns.mean()
                / returns.std()
            ) * np.sqrt(252)

        total_return = (

            close.iloc[-1]
            / close.iloc[0]
        ) - 1

        sma20 = (

            close.rolling(20)
            .mean()
            .iloc[-1]
        )

        sma50 = (

            close.rolling(50)
            .mean()
            .iloc[-1]
        )

        if sma50 == 0:

            trend_strength = 0

        else:

            trend_strength = (

                sma20 / sma50
            )

        # =================================================
        # CURRENT PRICE
        # =================================================

        cmp = close.iloc[-1]

        # =================================================
        # VOLATILITY MODEL
        # =================================================

        recent_volatility = (

            close.pct_change()

            .rolling(14)

            .std()

            .iloc[-1]
        )

        if pd.isna(recent_volatility):

            recent_volatility = 0.02

        stop_loss = (

            cmp

            * (1 - recent_volatility * 2)
        )

        target_price = (

            cmp

            * (1 + recent_volatility * 4)
        )

        risk_reward = (

            (target_price - cmp)

            / max(cmp - stop_loss, 0.0001)
        )

        # =================================================
        # REGIME ADAPTATION
        # =================================================

        if "BULLISH" in regime:

            momentum *= 1.20
            sharpe *= 1.10

        elif "BEARISH" in regime:

            volatility *= 1.30

        elif "SIDEWAYS" in regime:

            sharpe *= 1.10
            trend_strength *= 0.80

        # =================================================
        # SECTOR ADAPTIVE FACTOR ENGINE
        # =================================================

        if sector == "PRIVATE_BANKS":

            final_score = (

                sharpe * 0.20 +
                momentum * 0.20 +
                trend_strength * 0.15 +
                total_return * 0.20 +
                roe * 0.25
            )

        elif sector == "PSU_BANKS":

            final_score = (

                momentum * 0.30 +
                total_return * 0.25 +
                dividend_yield * 0.20 +
                sharpe * 0.15 -
                volatility * 0.10
            )

        elif sector == "PRIVATE_IT":

            final_score = (

                revenue_growth * 0.30 +
                operating_margin * 0.20 +
                momentum * 0.20 +
                sharpe * 0.15 +
                total_return * 0.15
            )

        elif sector == "PRIVATE_FMCG":

            final_score = (

                profit_margin * 0.30 +
                roe * 0.25 +
                sharpe * 0.20 -
                volatility * 0.15 +
                trend_strength * 0.10
            )

        elif sector == "PRIVATE_AUTO":

            final_score = (

                momentum * 0.30 +
                total_return * 0.25 +
                revenue_growth * 0.20 +
                trend_strength * 0.15 +
                sharpe * 0.10
            )

        elif sector == "PRIVATE_PHARMA":

            final_score = (

                profit_margin * 0.25 +
                sharpe * 0.25 +
                momentum * 0.20 +
                total_return * 0.15 -
                volatility * 0.15
            )

        elif sector == "PRIVATE_ENERGY":

            final_score = (

                total_return * 0.25 +
                momentum * 0.25 +
                sharpe * 0.20 +
                trend_strength * 0.15 +
                dividend_yield * 0.15
            )

        elif sector == "PSU_ENERGY":

            final_score = (

                dividend_yield * 0.35 +
                total_return * 0.20 +
                trend_strength * 0.20 +
                sharpe * 0.15 -
                volatility * 0.10
            )

        elif sector == "PSU_DEFENCE":

            final_score = (

                momentum * 0.35 +
                total_return * 0.25 +
                trend_strength * 0.20 +
                sharpe * 0.10 +
                revenue_growth * 0.10
            )

        elif sector == "PRIVATE_METALS":

            final_score = (

                momentum * 0.35 +
                total_return * 0.25 +
                trend_strength * 0.20 -
                volatility * 0.10 +
                sharpe * 0.10
            )

        elif sector == "PSU_METALS":

            final_score = (

                dividend_yield * 0.25 +
                total_return * 0.25 +
                momentum * 0.20 +
                sharpe * 0.15 -
                volatility * 0.15
            )

        else:

            final_score = (

                momentum * 0.25 +
                sharpe * 0.25 +
                total_return * 0.25 +
                trend_strength * 0.15 -
                volatility * 0.10
            )

        # =================================================
        # CLASSIFICATION
        # =================================================

        if final_score >= 1.20:

            classification = "STRONG_BUY"

        elif final_score >= 0.80:

            classification = "BUY"

        elif final_score >= 0.50:

            classification = "WATCH"

        else:

            classification = "AVOID"

        percentile = (

            final_score * 100
        )

        return {

            "Symbol": symbol,
            "Sector": sector,
            "Market Cap": safe_round(market_cap, 0),
            "Current Price": safe_round(cmp, 2),
            "Stop Loss": safe_round(stop_loss, 2),
            "Target": safe_round(target_price, 2),
            "Risk Reward": safe_round(risk_reward, 2),
            "Momentum": safe_round(momentum),
            "Volatility": safe_round(volatility),
            "Sharpe": safe_round(sharpe),
            "Trend Strength": safe_round(trend_strength),
            "Total Return": safe_round(total_return),
            "Final Score": safe_round(final_score),
            "Percentile": safe_round(percentile, 2),
            "Classification": classification
        }

    except Exception:

        return None
