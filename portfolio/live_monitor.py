import pandas as pd
import numpy as np

from signals.live_data import (
    fetch_stock_data
)

# =========================================================
# FETCH LIVE RETURNS
# =========================================================

def fetch_returns(

    symbol,

    period="3mo"
):

    data = fetch_stock_data(

        symbol,

        period=period
    )

    prices = data["Close"]

    # HANDLE DATAFRAME
    if isinstance(prices, pd.DataFrame):

        prices = prices.iloc[:, 0]

    returns = (

        prices.pct_change()

        .dropna()
    )

    return returns

# =========================================================
# PORTFOLIO VOLATILITY
# =========================================================

def portfolio_volatility(

    returns_df,

    weights
):

    cov = returns_df.cov()

    vol = np.sqrt(

        np.dot(

            weights.T,

            np.dot(cov, weights)
        )
    )

    return vol * np.sqrt(252)

# =========================================================
# PORTFOLIO RETURN
# =========================================================

def portfolio_return(

    returns_df,

    weights
):

    mean_returns = (

        returns_df.mean()
    )

    port_return = np.dot(

        mean_returns,

        weights
    )

    return port_return * 252

# =========================================================
# LIVE PORTFOLIO REPORT
# =========================================================

def live_portfolio_report(

    symbols,

    weights
):

    returns_data = {}

    for symbol in symbols:

        returns_data[symbol] = (

            fetch_returns(symbol)
        )

    returns_df = pd.DataFrame(

        returns_data
    ).dropna()

    port_vol = portfolio_volatility(

        returns_df,

        weights
    )

    port_return = portfolio_return(

        returns_df,

        weights
    )

    sharpe = (

        port_return

        / port_vol
    )

    report = {

        "Portfolio Return":

            round(port_return, 4),

        "Portfolio Volatility":

            round(port_vol, 4),

        "Sharpe Ratio":

            round(sharpe, 4),

        "Assets":

            len(symbols)
    }

    return report