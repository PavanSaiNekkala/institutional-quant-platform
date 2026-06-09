import pandas as pd

# =========================================================
# FACTOR CONTRIBUTION
# =========================================================


def factor_contribution(factor_returns, factor_weights):

    contribution = factor_returns * factor_weights

    return contribution


# =========================================================
# TOTAL PORTFOLIO RETURN
# =========================================================


def total_portfolio_return(contribution):

    return contribution.sum()


# =========================================================
# CONTRIBUTION REPORT
# =========================================================


def contribution_report(factor_returns, factor_weights):

    contribution = factor_contribution(factor_returns, factor_weights)

    total_return = total_portfolio_return(contribution)

    report = pd.DataFrame(
        {
            "Factor": factor_returns.index,
            "Factor Return": factor_returns.values,
            "Weight": factor_weights.values,
            "Contribution": contribution.values,
        }
    )

    report["Contribution %"] = report["Contribution"] / total_return

    return report


# =========================================================
# TOP CONTRIBUTORS
# =========================================================


def top_contributors(report, top_n=3):

    return report.sort_values(by="Contribution", ascending=False).head(top_n)


# =========================================================
# WORST CONTRIBUTORS
# =========================================================


def worst_contributors(report, top_n=3):

    return report.sort_values(by="Contribution", ascending=True).head(top_n)
