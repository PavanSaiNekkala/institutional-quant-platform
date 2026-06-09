from repositories.stock_repository import StockRepository


class MarketService:
    @staticmethod
    def get_stock_metadata():
        return StockRepository.get_all()
