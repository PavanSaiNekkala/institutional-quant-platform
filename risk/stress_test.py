# =========================================================
# SIMPLE STRESS TESTS
# =========================================================

def stress_test_portfolio(

    portfolio_value
):

    scenarios = {

        "Mild Crash (-10%)":
            portfolio_value * 0.90,

        "Moderate Crash (-20%)":
            portfolio_value * 0.80,

        "Severe Crash (-35%)":
            portfolio_value * 0.65,

        "Extreme Crash (-50%)":
            portfolio_value * 0.50
    }

    return scenarios