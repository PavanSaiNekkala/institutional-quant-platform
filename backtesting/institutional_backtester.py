import numpy as np
import pandas as pd
import yfinance as yf

# =========================================================
# INSTITUTIONAL BACKTESTER
# =========================================================

class InstitutionalBacktester:

    def __init__(

        self,

        initial_capital=100000
    ):

        self.initial_capital = initial_capital

    # =====================================================
    # LOAD DATA
    # =====================================================

    def load_data(

        self,

        symbols,

        period="1y"
    ):

        prices = pd.DataFrame()

        for symbol in symbols:

            try:

                data = yf.download(

                    symbol,

                    period=period,

                    progress=False,

                    auto_adjust=True
                )

                if data.empty:

                    continue

                close = data["Close"]

                if isinstance(close, pd.DataFrame):

                    close = close.iloc[:, 0]

                prices[symbol] = close

            except:

                continue

        return prices.dropna()

    # =====================================================
    # EQUAL WEIGHT STRATEGY
    # =====================================================

    def equal_weight_strategy(

        self,

        returns
    ):

        num_assets = len(

            returns.columns
        )

        weights = np.array(

            [1 / num_assets]

            * num_assets
        )

        portfolio_returns = returns.dot(

            weights
        )

        return portfolio_returns

    # =====================================================
    # PERFORMANCE METRICS
    # =====================================================

    def performance_metrics(

        self,

        portfolio_returns
    ):

        cumulative_returns = (

            1 + portfolio_returns
        ).cumprod()

        total_return = (

            cumulative_returns.iloc[-1]

            - 1
        )

        annual_return = (

            portfolio_returns.mean()

            * 252
        )

        annual_volatility = (

            portfolio_returns.std()

            * np.sqrt(252)
        )

        sharpe_ratio = (

            annual_return

            / annual_volatility
        )

        rolling_max = cumulative_returns.cummax()

        drawdown = (

            cumulative_returns

            / rolling_max

            - 1
        )

        max_drawdown = drawdown.min()

        return {

            "Total Return":

                round(total_return, 4),

            "Annual Return":

                round(annual_return, 4),

            "Annual Volatility":

                round(annual_volatility, 4),

            "Sharpe Ratio":

                round(sharpe_ratio, 4),

            "Max Drawdown":

                round(max_drawdown, 4)
        }

    # =====================================================
    # RUN BACKTEST
    # =====================================================

    def run_backtest(

        self,

        symbols,

        period="1y"
    ):

        prices = self.load_data(

            symbols,

            period
        )

        if prices.empty:

            return None

        returns = prices.pct_change().dropna()

        portfolio_returns = self.equal_weight_strategy(

            returns
        )

        metrics = self.performance_metrics(

            portfolio_returns
        )

        cumulative_curve = (

            1 + portfolio_returns
        ).cumprod()

        return {

            "metrics":

                metrics,

            "equity_curve":

                cumulative_curve,

            "returns":

                portfolio_returns
        }