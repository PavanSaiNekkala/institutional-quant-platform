from portfolio.portfolio_analytics import PortfolioAnalytics
from portfolio.risk_parity import RiskParity


class PortfolioService:

    @staticmethod
    def portfolio_summary():

        analytics = PortfolioAnalytics()

        return analytics.generate_summary()

    @staticmethod
    def risk_parity_weights(data):

        allocator = RiskParity()

        return allocator.allocate(data)
