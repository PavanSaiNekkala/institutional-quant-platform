import pandas as pd

from risk.regime_detection import (
    RegimeDetector
)

# =========================================================
# DYNAMIC STRATEGY SWITCHER
# =========================================================

class DynamicStrategySwitcher:

    def __init__(self):

        self.regime_engine = RegimeDetector()

    # =====================================================
    # SELECT STRATEGY
    # =====================================================

    def select_strategy(

        self,

        symbol="^NSEI"
    ):

        regime = self.regime_engine.detect(

            symbol=symbol
        )

        if regime is None:

            return None

        trend = regime[

            "Trend Regime"
        ]

        volatility = regime[

            "Volatility Regime"
        ]

        momentum = regime[

            "Momentum Regime"
        ]

        # =================================================
        # STRATEGY LOGIC
        # =================================================

        if (

            trend == "BULL"

            and volatility == "LOW VOL"

            and momentum == "POSITIVE"
        ):

            strategy = "AGGRESSIVE MOMENTUM"

            allocation = "HIGH EQUITY"

            risk_level = "HIGH"

        elif (

            trend == "BULL"

            and volatility == "HIGH VOL"
        ):

            strategy = "VOLATILITY CONTROL"

            allocation = "MODERATE EQUITY"

            risk_level = "MEDIUM"

        elif (

            trend == "BEAR"

            and volatility == "HIGH VOL"
        ):

            strategy = "DEFENSIVE"

            allocation = "LOW EQUITY"

            risk_level = "LOW"

        else:

            strategy = "BALANCED"

            allocation = "BALANCED"

            risk_level = "MEDIUM"

        return {

            "Regime":

                regime["Overall Regime"],

            "Selected Strategy":

                strategy,

            "Portfolio Allocation":

                allocation,

            "Risk Level":

                risk_level
        }

    # =====================================================
    # MULTI-ASSET SWITCHING
    # =====================================================

    def multi_asset_switching(

        self,

        symbols
    ):

        results = []

        for symbol in symbols:

            result = self.select_strategy(

                symbol
            )

            if result:

                result["Symbol"] = symbol

                results.append(result)

        return pd.DataFrame(results)