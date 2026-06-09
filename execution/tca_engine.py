import numpy as np
import pandas as pd

# =========================================================
# SLIPPAGE MODEL
# =========================================================


def estimate_slippage(price, volatility, participation_rate):

    slippage = price * volatility * np.sqrt(participation_rate)

    return round(slippage, 4)


# =========================================================
# SPREAD COST
# =========================================================


def spread_cost(price, spread_bps=5):

    return round(price * spread_bps / 10000, 4)


# =========================================================
# COMMISSION MODEL
# =========================================================


def commission_cost(trade_value, commission_bps=2):

    return round(trade_value * commission_bps / 10000, 4)


# =========================================================
# IMPLEMENTATION SHORTFALL
# =========================================================


def implementation_shortfall(arrival_price, execution_price, quantity):

    return round((execution_price - arrival_price) * quantity, 2)


# =========================================================
# FULL TCA REPORT
# =========================================================


def tca_report(symbol, quantity, arrival_price, execution_price, volatility, participation_rate):

    trade_value = execution_price * quantity

    slippage = estimate_slippage(execution_price, volatility, participation_rate)

    spread = spread_cost(execution_price)

    commission = commission_cost(trade_value)

    shortfall = implementation_shortfall(arrival_price, execution_price, quantity)

    total_cost = slippage + spread + commission

    return pd.DataFrame(
        {
            "Metric": [
                "Symbol",
                "Quantity",
                "Arrival Price",
                "Execution Price",
                "Slippage",
                "Spread Cost",
                "Commission",
                "Implementation Shortfall",
                "Total Estimated Cost",
            ],
            "Value": [
                symbol,
                quantity,
                arrival_price,
                execution_price,
                slippage,
                spread,
                commission,
                shortfall,
                total_cost,
            ],
        }
    )
