import time
import requests
import random
import json
import pandas as pd
from src.Limiter import RateLimiter
from typing import List, Union

REQUESTS_PER_SECOND = 3

class NasdaqAPI:

    def __init__(self, headers_file='/Users/adic/Desktop/Projects/stock_analysis/src/headers.json'):
        self.base_url = 'https://api.nasdaq.com/api'
        with open(headers_file, 'r') as file:
            self.headers_list = json.load(file)

    def get_random_headers(self):
        return random.choice(self.headers_list)

    def _fetch_basic_info(self, tickers: List[str]) -> pd.DataFrame:
        def fetch_single_basic_info(ticker):
            url = f'{self.base_url}/quote/{ticker}/summary?assetclass=stocks'
            headers = self.get_random_headers()
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                summary_data = data.get('data', {}).get('summaryData', {})
                return {
                    'Ticker': ticker,
                    'PreviousClose': summary_data.get('PreviousClose', {}).get('value', 'Not available'),
                    'MarketCap': summary_data.get('MarketCap', {}).get('value', 'Not available'),
                    'Sector': summary_data.get('Sector', {}).get('value', 'Not available'),
                    'Industry': summary_data.get('Industry', {}).get('value', 'Not available'),
                    'Exchange': summary_data.get('Exchange', {}).get('value', 'Not available')
                }
            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")
                return {
                    'Ticker': ticker,
                    'PreviousClose': 'Error fetching data',
                    'MarketCap': 'Error fetching data',
                    'Sector': 'Error fetching data',
                    'Industry': 'Error fetching data',
                    'Exchange': 'Error fetching data'
                }
            except Exception as err:
                print(f"An error occurred: {err}")
                return {
                    'Ticker': ticker,
                    'PreviousClose': 'Error fetching data',
                    'MarketCap': 'Error fetching data',
                    'Sector': 'Error fetching data',
                    'Industry': 'Error fetching data',
                    'Exchange': 'Error fetching data'
                }

        rate_limiter = RateLimiter(requests_per_second = REQUESTS_PER_SECOND)
        # basic_info_list = [rate_limiter.apply(fetch_single_basic_info, ticker) for ticker in tickers]

        basic_info_list = []

        for i, ticker in enumerate(tickers):
            if i > 0 and i % 50 == 0:
                # Sleep for 5 seconds after every 50 requests
                print("Performed 50 requests. Sleeping for 5 seconds...")
                time.sleep(5)
            
            info = rate_limiter.apply(fetch_single_basic_info, ticker)
            basic_info_list.append(info)        

        return pd.DataFrame(basic_info_list)

    def get_basic_info(self, tickers: Union[str, List[str]]) -> pd.DataFrame:
        if isinstance(tickers, str):
            tickers = [tickers]
        df = self._fetch_basic_info(tickers)
        return df
    
    def get_sector(self, tickers: Union[str, List[str]]) -> pd.DataFrame:
        df = self.get_basic_info(tickers)
        return df[['Ticker', 'Sector']]

    def get_previous_close(self, tickers: Union[str, List[str]]) -> pd.DataFrame:
        df = self.get_basic_info(tickers)
        return df[['Ticker', 'PreviousClose']]

    def get_market_cap(self, tickers: Union[str, List[str]]) -> pd.DataFrame:
        df = self.get_basic_info(tickers)
        return df[['Ticker', 'MarketCap']]

    def get_exchange(self, tickers: Union[str, List[str]]) -> pd.DataFrame:
        df = self.get_basic_info(tickers)
        return df[['Ticker', 'Exchange']]

    def get_industry(self, tickers: Union[str, List[str]]) -> pd.DataFrame:
        df = self.get_basic_info(tickers)
        return df[['Ticker', 'Industry']]


def main():
    api = NasdaqAPI()
    tickers = ['AAPL', 'AMZN','MSFT','TSLA','UPRO']
    info = api.get_basic_info('PLTR')
    print(info)
    info2 = api.get_market_cap('QQQ')
    print(info2)


    #market_caps = api.get_market_cap(tickers, requests_per_second=1)
    #print(api.get_random_headers())



if __name__ == "__main__":
    main()




    # def fetch_single_market_cap(self, ticker):
    #     url = f'{self.base_url}/quote/{ticker}/summary?assetclass=stocks'
    #     headers = self.get_random_headers()
    #     try:
    #         response = requests.get(url, headers=headers)
    #         response.raise_for_status()
    #         data = response.json()
    #         market_cap = data.get('data', {}).get('summaryData', {}).get('MarketCap', {}).get('value', 'Not available')
    #         return market_cap
    #     except requests.exceptions.HTTPError as http_err:
    #         print(f"HTTP error occurred: {http_err}")
    #         return 'Error fetching data'
    #     except Exception as err:
    #         print(f"An error occurred: {err}")
    #         return 'Error fetching data'  

    # def get_market_cap(self, tickers: Union[str, List[str]], requests_per_second: int = 2) -> dict:
    #     if isinstance(tickers, str):
    #         tickers = [tickers]

    #     rate_limiter = RateLimiter(requests_per_second=requests_per_second)

    #     market_caps = {}
    #     for ticker in tickers:
    #         print(f"Fetching market cap for {ticker}...")
    #         market_cap = rate_limiter.apply(self.fetch_single_market_cap, ticker)
    #         market_caps[ticker] = market_cap
    #         print(f"Market Cap for {ticker}: {market_cap}")

    #     del rate_limiter
    #     return market_caps