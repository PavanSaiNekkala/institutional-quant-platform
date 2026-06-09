import numpy as np
import pandas as pd
import yfinance as yf

# =========================================================
# FACTOR ANALYSIS
# =========================================================


def analyze_factor_exposure(symbol, benchmark="^NSEI", period="6mo"):

    try:
        # =================================================
        # STOCK DATA
        # =================================================

        stock_data = yf.download(symbol, period=period, progress=False, auto_adjust=True)

        benchmark_data = yf.download(benchmark, period=period, progress=False, auto_adjust=True)

        if stock_data.empty:
            return None

        if benchmark_data.empty:
            return None

        stock_close = stock_data["Close"]

        benchmark_close = benchmark_data["Close"]

        if isinstance(stock_close, pd.DataFrame):
            stock_close = stock_close.iloc[:, 0]

        if isinstance(benchmark_close, pd.DataFrame):
            benchmark_close = benchmark_close.iloc[:, 0]

        stock_returns = stock_close.pct_change().dropna()

        benchmark_returns = benchmark_close.pct_change().dropna()

        aligned = pd.concat([stock_returns, benchmark_returns], axis=1).dropna()

        aligned.columns = ["stock", "benchmark"]

        # =================================================
        # FACTORS
        # =================================================

        covariance = np.cov(aligned["stock"], aligned["benchmark"])

        beta = covariance[0][1] / covariance[1][1]

        momentum = (stock_close.iloc[-1] / stock_close.iloc[-20]) - 1

        volatility = stock_returns.std() * np.sqrt(252)

        correlation = aligned.corr().iloc[0, 1]

        return {
            "Symbol": symbol,
            "Beta": round(beta, 4),
            "Momentum Exposure": round(momentum, 4),
            "Volatility Exposure": round(volatility, 4),
            "Market Correlation": round(correlation, 4),
        }

    except Exception:
        return None


# =========================================================
# PORTFOLIO FACTOR ENGINE
# =========================================================


class FactorExposureEngine:
    def run_analysis(self, symbols):

        results = []

        for symbol in symbols:
            result = analyze_factor_exposure(symbol)

            if result:
                results.append(result)

        return pd.DataFrame(results)
