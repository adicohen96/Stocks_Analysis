import random
import time
from pyrate_limiter import Rate, Limiter, Duration, BucketFullException
from contextlib import contextmanager
from typing import List, Union
import requests

class RateLimiter:
    total_time = 0

    def __init__(self, requests_per_second):
        self.rate = Rate(requests_per_second, Duration.SECOND)
        self.limiter = Limiter(self.rate)

    def _wait_for_available_slot(self):
        while True:
            try:
                self.limiter.try_acquire('key')
                break
            except BucketFullException as e:
                delay = random.uniform(1, 2)
                print(f"Rate limit exceeded. Retrying in {delay:.2f} seconds.")
                time.sleep(delay)

    def apply(self, func, *args, **kwargs):
        self._wait_for_available_slot()
        with self.time_it():
            result = func(*args, **kwargs)
        return result

    @contextmanager
    def time_it(self):
        start_time = time.time()
        yield
        end_time = time.time()
        elapsed_time = end_time - start_time
        RateLimiter.total_time += elapsed_time

    def __del__(self):
        print(f"Total time taken for API requests: {RateLimiter.total_time:.2f} seconds")

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






# import random
# import time
# import requests
# from pyrate_limiter import Limiter, Duration, Rate, BucketFullException
# from contextlib import contextmanager


# class RateLimiter:
#     total_time = 0

#     def __init__(self, requests_per_second):
#         self.rate = Rate(requests_per_second, Duration.SECOND)
#         self.limiter = Limiter(self.rate)

#     def _wait_for_available_slot(self):
#         while True:
#             try:
#                 self.limiter.try_acquire('key')
#                 break
#             except BucketFullException as e:
#                 delay = random.uniform(1, 3)
#                 print(f"Rate limit exceeded. Retrying in {delay:.2f} seconds.")
#                 time.sleep(delay)

#     def apply(self, func, *args, **kwargs):
#         self._wait_for_available_slot()
#         with self.time_it():
#             result = func(*args, **kwargs)
#         return result

#     @contextmanager
#     def time_it(self):
#         start_time = time.time()
#         yield
#         end_time = time.time()
#         elapsed_time = end_time - start_time
#         RateLimiter.total_time += elapsed_time

#     def __del__(self):
#         print(f"Total time taken for API requests: {RateLimiter.total_time:.2f} seconds")



# def get_market_cap(ticker):
#     url = f'https://api.nasdaq.com/api/quote/{ticker}/summary?assetclass=stocks'
#     headers = {
#         'User-Agent': random.choice([
#             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#             'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
#             'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
#         ]),
#         'Accept-Language': 'en-US,en;q=0.9',
#         'Accept-Encoding': 'gzip, deflate, br',
#         'Connection': 'keep-alive'
#     }
    
#     try:
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()
#         data = response.json()
#         market_cap = data.get('data', {}).get('summaryData', {}).get('MarketCap', {}).get('value', 'Not available')
#         return market_cap
#     except requests.exceptions.HTTPError as http_err:
#         print(f"HTTP error occurred for {ticker}: {http_err}")
#         return 'Error fetching data'
#     except Exception as err:
#         print(f"An error occurred for {ticker}: {err}")
#         return 'Error fetching data'
    

# def main():
#     rate_limiter = RateLimiter(requests_per_second=2)

#     # List of tickers to fetch market cap for
#     tickers = ['AGNCL', 'AGNCO', 'AGNCP', 'APOS', 'AQNB', 'ARGD', 'ASBA', 'BKDT', 'BNH', 'BNJ', 'DUKB', 'ECCF', 'FITBP', 'HBANP', 'HBANM', 'KKRS', 'PFH', 'QRTEP', 'SOJE', 'SOJD', 'SREA', 'TBC']

#     # Dictionary to store market caps
#     market_caps = {}

#     # Fetch market cap for each ticker
#     for ticker in tickers:
#         print(f"Fetching market cap for {ticker}...")
#         market_cap = rate_limiter.apply(get_market_cap, ticker)
#         market_caps[ticker] = market_cap
#         print(f"Market Cap for {ticker}: {market_cap}")

#     print("Market cap data fetch complete.")



# # Example usage
# if __name__ == "__main__":
#     main()