import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# =========================================================
# FACTOR REGRESSION
# =========================================================

def factor_regression(

    portfolio_returns,

    factor_returns
):

    model = LinearRegression()

    X = factor_returns.values

    y = portfolio_returns.values

    model.fit(X, y)

    exposures = pd.Series(

        model.coef_,

        index=factor_returns.columns
    )

    alpha = model.intercept_

    r2 = model.score(X, y)

    return {

        "Exposures":

            exposures,

        "Alpha":

            alpha,

        "R2":

            r2
    }

# =========================================================
# FACTOR CONTRIBUTION
# =========================================================

def factor_contribution(

    exposures,

    factor_means
):

    contribution = (

        exposures

        * factor_means
    )

    return contribution

# =========================================================
# FULL ATTRIBUTION REPORT
# =========================================================

def attribution_report(

    portfolio_returns,

    factor_returns
):

    regression = factor_regression(

        portfolio_returns,

        factor_returns
    )

    exposures = regression["Exposures"]

    alpha = regression["Alpha"]

    r2 = regression["R2"]

    contributions = factor_contribution(

        exposures,

        factor_returns.mean()
    )

    report = pd.DataFrame({

        "Factor":

            exposures.index,

        "Exposure":

            exposures.values,

        "Contribution":

            contributions.values
    })

    return {

        "Alpha":

            round(alpha, 6),

        "R2":

            round(r2, 4),

        "Report":

            report
    }