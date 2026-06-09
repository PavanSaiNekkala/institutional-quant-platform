import yfinance as yf

# =========================================================
# FETCH SINGLE STOCK
# =========================================================


def fetch_stock_data(symbol, period="6mo", interval="1d"):

    data = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)

    return data


# =========================================================
# FETCH MULTIPLE STOCKS
# =========================================================


def fetch_multiple_stocks(symbols, period="6mo"):

    data = yf.download(symbols, period=period, auto_adjust=True, progress=False)

    return data


# =========================================================
# COMPUTE RETURNS
# =========================================================


def compute_returns(prices):

    return prices.pct_change().dropna()


# =========================================================
# MARKET SNAPSHOT
# =========================================================


def market_snapshot(symbol):

    data = fetch_stock_data(symbol, period="5d")

    latest_close = data["Close"].iloc[-1]

    latest_volume = data["Volume"].iloc[-1]

    returns = compute_returns(data["Close"])

    volatility = returns.std() * (252**0.5)

    snapshot = {
        "Symbol": symbol,
        "Latest Price": round(latest_close, 2),
        "Latest Volume": int(latest_volume),
        "Annualized Volatility": round(volatility, 4),
    }

    return snapshot
