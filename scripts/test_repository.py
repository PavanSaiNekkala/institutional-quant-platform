from services.market_service import MarketService

df = MarketService.get_stock_metadata()

print(df.head())
