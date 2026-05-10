import yfinance as yf
import pandas as pd
import numpy as np
import vectorbt as vbt

from core.indicators import (
    EMA,
    RSI,
    ATR,
    volatility,
    momentum,
    distance_from_high,
    volume_ratio,
    trend_quality,
    volatility_contraction
)

from core.scoring import (
    calculate_score
)

# =========================================================
# FEATURE ENGINEERING
# =========================================================

def build_features(df):

    df = df.copy()

    # =====================================================
    # MOVING AVERAGES
    # =====================================================

    df["ema20"] = EMA(df["close"], 20)

    df["ema50"] = EMA(df["close"], 50)

    df["ema100"] = EMA(df["close"], 100)

    df["ema200"] = EMA(df["close"], 200)

    # =====================================================
    # RSI
    # =====================================================

    df["rsi"] = RSI(df["close"])

    # =====================================================
    # ATR
    # =====================================================

    df["atr"] = ATR(df)

    # =====================================================
    # VOLATILITY
    # =====================================================

    df["volatility"] = volatility(df["close"])

    # =====================================================
    # MOMENTUM
    # =====================================================

    df["momentum_1m"] = momentum(df["close"], 21)

    df["momentum_3m"] = momentum(df["close"], 63)

    df["momentum_6m"] = momentum(df["close"], 126)

    df["momentum_12m"] = momentum(df["close"], 252)

    # =====================================================
    # DISTANCE FROM HIGH
    # =====================================================

    df["distance_from_high"] = (
        distance_from_high(df["close"])
    )

    # =====================================================
    # VOLUME RATIO
    # =====================================================

    df["volume_ratio"] = (
        volume_ratio(df["volume"])
    )

    # =====================================================
    # TREND QUALITY
    # =====================================================

    df["trend_quality"] = (
        trend_quality(df)
    )

    # =====================================================
    # VOLATILITY CONTRACTION
    # =====================================================

    df["volatility_contraction"] = (
        volatility_contraction(df)
    )

    return df.dropna()

# =========================================================
# SCORE STOCK
# =========================================================

def score_stock(df):

    if df.empty:
        return None

    last = df.iloc[-1]

    score = calculate_score(last)

    return score

# =========================================================
# BACKTEST ENGINE
# =========================================================

def run_backtest(stock_data):

    scores = []

    # =====================================================
    # SCORE ALL STOCKS
    # =====================================================

    for symbol, df in stock_data.items():

        try:

            features = build_features(df)

            score = score_stock(features)

            if score is None:
                continue

            scores.append({

                "symbol": symbol,

                "score": score
            })

        except:
            continue

    # =====================================================
    # RANK STOCKS
    # =====================================================

    scores_df = pd.DataFrame(scores)

    scores_df = scores_df.sort_values(

        "score",

        ascending=False
    )

    # =====================================================
    # SELECT TOP STOCKS
    # =====================================================

    top_stocks = (

        scores_df

        .head(10)

        ["symbol"]

        .tolist()
    )

    return scores_df, top_stocks
    
    # =========================================================
# PORTFOLIO RETURN ENGINE
# =========================================================

def simulate_portfolio(

    stock_data,

    top_stocks,

    initial_capital=100000

):

    returns_list = []

    valid_symbols = []

        # =====================================================
    # BENCHMARK DATA
    # =====================================================

    benchmark = yf.download(

        "^NSEI",

        period="2y",

        progress=False
    )

    benchmark_close = benchmark["Close"]

    benchmark_returns = (

        benchmark_close

        .pct_change()

        .dropna()
    )

    benchmark_equity = (

        initial_capital *

        (1 + benchmark_returns)

        .cumprod()
    )

    # =====================================================
    # BUILD RETURNS MATRIX
    # =====================================================

    for symbol in top_stocks:

        try:

            df = stock_data[symbol]

            close = df["close"]

            returns = close.pct_change()

            returns.name = symbol

            returns_list.append(returns)

            valid_symbols.append(symbol)

        except:
            continue

    # =====================================================
    # COMBINE RETURNS
    # =====================================================

    returns_df = pd.concat(

        returns_list,

        axis=1
    ).dropna()

    # =====================================================
    # EQUAL WEIGHT PORTFOLIO
    # =====================================================

    weights = np.repeat(

        1 / len(valid_symbols),

        len(valid_symbols)
    )

    # =====================================================
    # PORTFOLIO RETURNS
    # =====================================================

    portfolio_returns = (

        returns_df * weights

    ).sum(axis=1)

    # =====================================================
    # EQUITY CURVE
    # =====================================================

    equity_curve = (

        initial_capital *

        (1 + portfolio_returns)

        .cumprod()
    )

    # =====================================================
    # PERFORMANCE METRICS
    # =====================================================

    cumulative_return = (

        equity_curve.iloc[-1]

        / initial_capital
    ) - 1

    annualized_return = (

        (1 + cumulative_return)

        ** (252 / len(portfolio_returns))

    ) - 1

    annualized_volatility = (

        portfolio_returns.std()

        * np.sqrt(252)
    )

    sharpe_ratio = (

        annualized_return /

        (annualized_volatility + 1e-9)
    )

    rolling_max = equity_curve.cummax()

    drawdown = (

        equity_curve - rolling_max

    ) / rolling_max

    max_drawdown = drawdown.min()
    
    # =====================================================
    # BENCHMARK CAGR
    # =====================================================

    benchmark_cumulative = (

        benchmark_equity.iloc[-1]

        / initial_capital
    ) - 1

    benchmark_annualized = (

        (1 + benchmark_cumulative)

        ** (252 / len(benchmark_returns))

    ) - 1

    # =====================================================
    # ALPHA
    # =====================================================

    alpha = (

        annualized_return -

        benchmark_annualized
    )

    # =====================================================
    # SORTINO RATIO
    # =====================================================

    downside_returns = portfolio_returns[
        portfolio_returns < 0
    ]

    downside_std = (

        downside_returns.std()

        * np.sqrt(252)
    )

    sortino_ratio = (

        annualized_return /

        (downside_std + 1e-9)
    )

    # =====================================================
    # WIN RATE
    # =====================================================

    win_rate = (

        (portfolio_returns > 0)

        .mean()
    )

    # =====================================================
    # CALMAR RATIO
    # =====================================================

    calmar_ratio = (

        annualized_return /

        abs(max_drawdown + 1e-9)
    )

    # =====================================================
    # VOLATILITY-ADJUSTED RETURN
    # =====================================================

    risk_adjusted_return = (

        cumulative_return /

        (annualized_volatility + 1e-9)
    )

    # =====================================================
    # RESULTS
    # =====================================================

    results = {

        "Initial Capital":
            initial_capital,

        "Final Portfolio Value":
            equity_curve.iloc[-1],

        "Cumulative Return":
            cumulative_return,

        "Annualized Return":
            annualized_return,

        "Annualized Volatility":
            annualized_volatility,

        "Sharpe Ratio":
            sharpe_ratio,

        "Sortino Ratio":
            sortino_ratio,

        "Calmar Ratio":
            calmar_ratio,

        "Win Rate":
            win_rate,

        "Risk Adjusted Return":
            risk_adjusted_return,

        "Benchmark Return":
            benchmark_annualized,

        "Alpha":
            alpha,

        "Maximum Drawdown":
            max_drawdown
    }

    return (

        portfolio_returns,

        equity_curve,

        benchmark_equity,

        results
    )