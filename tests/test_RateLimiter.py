import random
import time
from pyrate_limiter import Rate, Limiter, Duration, BucketFullException
from contextlib import contextmanager
from typing import List, Union
import requests


def get_market_cap(tickers: Union[str, List[str]], requests_per_second: int = 2) -> dict:
    def fetch_single_market_cap(ticker):
        url = f'https://api.nasdaq.com/api/quote/{ticker}/summary?assetclass=stocks'
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            market_cap = data.get('data', {}).get('summaryData', {}).get('MarketCap', {}).get('value', 'Not available')
            return market_cap
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return 'Error fetching data'
        except Exception as err:
            print(f"An error occurred: {err}")
            return 'Error fetching data'

    if isinstance(tickers, str):
        tickers = [tickers]

    rate_limiter = RateLimiter(requests_per_second=requests_per_second)

    market_caps = {}
    for ticker in tickers:
        print(f"Fetching market cap for {ticker}...")
        market_cap = rate_limiter.apply(fetch_single_market_cap, ticker)
        market_caps[ticker] = market_cap
        print(f"Market Cap for {ticker}: {market_cap}")
    
    del rate_limiter
    return market_caps

def main():
    tickers = ['AGNCL', 'AGNCO', 'AGNCP', 'APOS', 'AQNB', 'ARGD', 'ASBA', 'BKDT', 'BNH', 'BNJ', 'DUKB', 'ECCF', 'FITBP', 'HBANP', 'HBANM', 'KKRS', 'PFH', 'QRTEP', 'SOJE', 'SOJD', 'SREA', 'TBC']
    market_caps = get_market_cap(tickers, requests_per_second=2)
    print(market_caps)

if __name__ == "__main__":
    main()
