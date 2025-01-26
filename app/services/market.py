import requests
import random
import asyncio

class MarketService:
    def __init__(self):
        self.btc_price = None
        self.eth_price = None
        self.fetch_prices()

    def fetch_prices(self):
        try:
            btc_response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
            btc_data = btc_response.json()
            self.btc_price = float(btc_data['price'])

            eth_response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT")
            eth_data = eth_response.json()
            self.eth_price = float(eth_data['price'])
        except Exception as e:
            self.btc_price = 30000  
            self.eth_price = 2000   

    def get_btc_price(self):
        if self.btc_price is None:
            self.fetch_prices()
        fluctuation = random.uniform(-0.01, 0.01) 
        return self.btc_price * (1 + fluctuation)

    def get_eth_price(self):
        if self.eth_price is None:
            self.fetch_prices()
        fluctuation = random.uniform(-0.01, 0.01)  
        return self.eth_price * (1 + fluctuation)

    async def get_prices(self):
        if self.btc_price is None or self.eth_price is None:
            self.fetch_prices()
        
        btc_fluctuation = random.uniform(-0.01, 0.01)
        eth_fluctuation = random.uniform(-0.01, 0.01)
        
        btc_price = self.btc_price * (1 + btc_fluctuation)
        eth_price = self.eth_price * (1 + eth_fluctuation)
        
        return btc_price, eth_price