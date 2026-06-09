from risk.risk_engine import RiskEngine
from risk.var import calculate_var


class RiskService:
    @staticmethod
    def portfolio_risk(portfolio):

        engine = RiskEngine()

        return engine.evaluate(portfolio)

    @staticmethod
    def value_at_risk(portfolio):

        return calculate_var(portfolio)
