import numpy as np
import pandas as pd
import yfinance as yf

from core.task_queue import (
    TaskQueue
)

# =========================================================
# FACTOR RESEARCH
# =========================================================

def factor_research(

    symbol,

    period="6mo"
):

    try:

        data = yf.download(

            symbol,

            period=period,

            progress=False,

            auto_adjust=True
        )

        if data.empty:

            return None

        close = data["Close"]

        if isinstance(close, pd.DataFrame):

            close = close.iloc[:, 0]

        returns = close.pct_change().dropna()

        if len(returns) < 20:

            return None

        momentum = (

            close.iloc[-1]

            / close.iloc[-20]

        ) - 1

        volatility = (

            returns.std()

            * np.sqrt(252)
        )

        sharpe = (

            returns.mean()

            / returns.std()

        ) * np.sqrt(252)

        alpha_score = (

            momentum * 0.4

            + sharpe * 0.4

            - volatility * 0.2
        )

        return {

            "Symbol":

                symbol,

            "Momentum":

                round(momentum, 4),

            "Volatility":

                round(volatility, 4),

            "Sharpe":

                round(sharpe, 4),

            "Alpha Score":

                round(alpha_score, 4)
        }

    except:

        return None

# =========================================================
# DISTRIBUTED RESEARCH
# =========================================================

class DistributedResearch:

    def __init__(self):

        self.queue = TaskQueue()

    # =====================================================
    # RUN RESEARCH
    # =====================================================

    def run_research(

        self,

        symbols,

        workers=8
    ):

        self.queue.start_workers(

            num_workers=workers
        )

        for symbol in symbols:

            self.queue.add_task(

                factor_research,

                symbol
            )

        self.queue.wait_completion()

        self.queue.stop_workers()

        results = [

            r for r in self.queue.results

            if r is not None
        ]

        return pd.DataFrame(results)