import numpy as np
import pandas as pd
import yfinance as yf

from core.task_queue import (
    TaskQueue
)

# =========================================================
# FORECAST MODEL
# =========================================================

def ai_forecast(

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

        close = close.dropna()

        if len(close) < 30:

            return None

        # =================================================
        # SIMPLE AI FORECAST
        # =================================================

        returns = close.pct_change().dropna()

        forecast_return = (

            returns.tail(10).mean()
        )

        volatility = (

            returns.std()

            * np.sqrt(252)
        )

        forecast_price = (

            close.iloc[-1]

            * (1 + forecast_return)
        )

        confidence = max(

            0,

            1 - volatility
        )

        return {

            "Symbol":

                symbol,

            "Current Price":

                round(close.iloc[-1], 2),

            "Forecast Price":

                round(forecast_price, 2),

            "Forecast Return":

                round(forecast_return, 4),

            "Confidence":

                round(confidence, 4)
        }

    except:

        return None

# =========================================================
# DISTRIBUTED AI FORECASTING
# =========================================================

class DistributedForecasting:

    def __init__(self):

        self.queue = TaskQueue()

    # =====================================================
    # RUN FORECASTS
    # =====================================================

    def run_forecasts(

        self,

        symbols,

        workers=8
    ):

        self.queue.start_workers(

            num_workers=workers
        )

        for symbol in symbols:

            self.queue.add_task(

                ai_forecast,

                symbol
            )

        self.queue.wait_completion()

        self.queue.stop_workers()

        results = [

            r for r in self.queue.results

            if r is not None
        ]

        return pd.DataFrame(results)