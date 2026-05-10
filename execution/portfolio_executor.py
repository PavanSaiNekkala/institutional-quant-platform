import pandas as pd

# =========================================================
# POSITION SIZING
# =========================================================

def position_size(

    capital,

    weight,

    price
):

    allocation = capital * weight

    quantity = int(

        allocation / price
    )

    return max(quantity, 0)

# =========================================================
# GENERATE ORDERS
# =========================================================

def generate_orders(

    portfolio_df,

    capital=1_000_000
):

    orders = []

    for _, row in portfolio_df.iterrows():

        symbol = row["Symbol"]

        weight = row["Weight"]

        price = row["Price"]

        quantity = position_size(

            capital,

            weight,

            price
        )

        orders.append({

            "Symbol":

                symbol,

            "Weight":

                weight,

            "Price":

                price,

            "Quantity":

                quantity,

            "Order Value":

                round(

                    quantity * price,

                    2
                )
        })

    return pd.DataFrame(

        orders
    )

# =========================================================
# EXECUTE PORTFOLIO
# =========================================================

def execute_portfolio(

    broker,

    orders_df
):

    executions = []

    for _, row in orders_df.iterrows():

        result = broker.place_order(

            row["Symbol"],

            int(row["Quantity"]),

            "BUY"
        )

        executions.append(

            result
        )

    return pd.DataFrame(

        executions
    )