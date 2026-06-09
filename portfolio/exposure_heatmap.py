import pandas as pd
import yfinance as yf

# =========================================================
# EXPOSURE HEATMAP ENGINE
# =========================================================


class ExposureHeatmap:
    def __init__(self, positions):

        self.positions = positions

    # =====================================================
    # MARKET VALUE
    # =====================================================

    def position_values(self):

        results = []

        total_value = 0

        for symbol, quantity in self.positions.items():
            if quantity <= 0:
                continue

            try:
                data = yf.download(symbol, period="5d", progress=False, auto_adjust=True)

                if data.empty:
                    continue

                close = data["Close"]

                if isinstance(close, pd.DataFrame):
                    close = close.iloc[:, 0]

                price = float(close.iloc[-1])

                market_value = quantity * price

                total_value += market_value

                results.append(
                    {
                        "Symbol": symbol,
                        "Quantity": quantity,
                        "Price": round(price, 2),
                        "Market Value": round(market_value, 2),
                    }
                )

            except Exception:
                continue

        df = pd.DataFrame(results)

        if df.empty:
            return df

        df["Exposure %"] = (df["Market Value"] / total_value) * 100

        df["Exposure %"] = df["Exposure %"].round(2)

        return df.sort_values(by="Exposure %", ascending=False)

    # =====================================================
    # CONCENTRATION METRICS
    # =====================================================

    def concentration_metrics(self, df):

        if df.empty:
            return {}

        max_exposure = df["Exposure %"].max()

        top3 = df["Exposure %"].head(3).sum()

        return {
            "Largest Position Exposure %": round(max_exposure, 2),
            "Top 3 Concentration %": round(top3, 2),
        }
