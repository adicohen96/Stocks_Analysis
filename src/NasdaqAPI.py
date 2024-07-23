import time
import requests
import random
import json
import os
import pandas as pd
from src.Limiter import RateLimiter
from typing import List, Union
from datetime import datetime
import pytz

# Define the number of requests allowed per second and cache file path
REQUESTS_PER_SECOND = 3
CACHE_FILE_PATH = '/Users/adic/Desktop/Projects/stock_analysis/src/cache.json'
HEADERS_PATH = '/Users/adic/Desktop/Projects/stock_analysis/src/headers.json'

class NasdaqAPI:

    def __init__(self, headers_file=HEADERS_PATH):
        self.base_url = 'https://api.nasdaq.com/api'

        # Load headers from file
        if not os.path.exists(headers_file):
            raise FileNotFoundError(f"Headers file not found: {headers_file}")
        with open(headers_file, 'r') as file:
            self.headers_list = json.load(file)
        if not self.headers_list:
            raise ValueError("Headers list is empty. Please provide valid headers.")

        # Load cache file if it exists
        if os.path.exists(CACHE_FILE_PATH):
            try:
                with open(CACHE_FILE_PATH, 'r') as cache_file:
                    self.cache = json.load(cache_file)
                    if not self.cache:
                        print("Cache file is empty. Initializing empty cache.")
                        self.cache = {}
            except json.JSONDecodeError:
                print("Cache file is not a valid JSON. Initializing empty cache.")
                self.cache = {}
        else:
            self.cache = {}

    def __save_cache(self):
        """Save the cache to a file."""
        with open(CACHE_FILE_PATH, 'w') as cache_file:
            json.dump(self.cache, cache_file, indent=4) 

    def __is_cache_valid(self, ticker):
        """Check if the cache for the given ticker is valid."""
        if ticker not in self.cache:
            return False
        
        cache_date = self.cache[ticker].get('date')
        if not cache_date:
            return False

        # Convert cache_date to datetime object
        cache_date = datetime.strptime(cache_date, '%Y-%m-%d')
        eastern = pytz.timezone('US/Eastern')
        now = datetime.now(eastern)
        
        # Check if the cache is for today and if the stock market is still open
        if cache_date.date() == now.date() and now.time() < datetime.strptime('16:00', '%H:%M').time():
            return True
        
        # Check if the cache is from Friday and today is Saturday, Sunday, or Monday before 16:00 Eastern time
        if cache_date.weekday() == 4:  # Friday
            if now.weekday() in [5, 6] or (now.weekday() == 0 and now.time() < datetime.strptime('16:00', '%H:%M').time()):
                return True
        
        return False   

    def __get_random_headers(self):
        """Get a random set of headers from the headers list."""
        if not self.headers_list:
            raise ValueError("Headers list is empty. Please provide valid headers.")
        return random.choice(self.headers_list)

    def _fetch_basic_info(self, tickers: List[str]) -> pd.DataFrame:
        """Fetch basic information for a list of tickers."""
        def fetch_single_basic_info(ticker):
            """Fetch basic info for a single ticker, with caching."""
            if self.__is_cache_valid(ticker):
                return self.cache[ticker]

            url = f'{self.base_url}/quote/{ticker}/summary?assetclass=stocks'
            headers = self.__get_random_headers()
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                summary_data = data.get('data', {}).get('summaryData', {})
                info = {
                    'Ticker': ticker,
                    'PreviousClose': summary_data.get('PreviousClose', {}).get('value', 'Not available'),
                    'MarketCap': summary_data.get('MarketCap', {}).get('value', 'Not available'),
                    'Sector': summary_data.get('Sector', {}).get('value', 'Not available'),
                    'Industry': summary_data.get('Industry', {}).get('value', 'Not available'),
                    'Exchange': summary_data.get('Exchange', {}).get('value', 'Not available'),
                    'date': datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d')
                }
                self.cache[ticker] = info
                return info
            
            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")
                return {
                    'Ticker': ticker,
                    'PreviousClose': 'Error fetching data',
                    'MarketCap': 'Error fetching data',
                    'Sector': 'Error fetching data',
                    'Industry': 'Error fetching data',
                    'Exchange': 'Error fetching data',
                    'date': datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d')
                }
            
            except Exception as err:
                print(f"An error occurred: {err}")
                return {
                    'Ticker': ticker,
                    'PreviousClose': 'Error fetching data',
                    'MarketCap': 'Error fetching data',
                    'Sector': 'Error fetching data',
                    'Industry': 'Error fetching data',
                    'Exchange': 'Error fetching data',
                    'date': datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d')
                }

        # Apply rate limiting to prevent hitting the API too frequently
        rate_limiter = RateLimiter(requests_per_second=REQUESTS_PER_SECOND)
        basic_info_list = []

        for i, ticker in enumerate(tickers):
            if i > 0 and i % 50 == 0:
                # Sleep for 5 seconds after every 50 requests
                print("Performed 50 requests. Sleeping for 5 seconds...")
                time.sleep(5)
            
            info = rate_limiter.apply(fetch_single_basic_info, ticker)
            basic_info_list.append(info)  

        # Save the cache after fetching data
        self.__save_cache()
        del rate_limiter
        return pd.DataFrame(basic_info_list)

    def get_basic_info(self, tickers: Union[str, List[str]]) -> pd.DataFrame:
        """Fetch basic information for one or more tickers."""
        if isinstance(tickers, str):
            tickers = [tickers]
        df = self._fetch_basic_info(tickers)
        return df
    
    def get_sector(self, tickers: Union[str, List[str]]) -> pd.DataFrame:
        """Get sector information for one or more tickers."""
        df = self.get_basic_info(tickers)
        return df[['Ticker', 'Sector']]

    def get_previous_close(self, tickers: Union[str, List[str]]) -> pd.DataFrame:
        """Get previous close prices for one or more tickers."""
        df = self.get_basic_info(tickers)
        return df[['Ticker', 'PreviousClose']]

    def get_market_cap(self, tickers: Union[str, List[str]]) -> pd.DataFrame:
        """Get market capitalization for one or more tickers."""
        df = self.get_basic_info(tickers)
        return df[['Ticker', 'MarketCap']]

    def get_exchange(self, tickers: Union[str, List[str]]) -> pd.DataFrame:
        """Get exchange information for one or more tickers."""
        df = self.get_basic_info(tickers)
        return df[['Ticker', 'Exchange']]

    def get_industry(self, tickers: Union[str, List[str]]) -> pd.DataFrame:
        """Get industry information for one or more tickers."""
        df = self.get_basic_info(tickers)
        return df[['Ticker', 'Industry']]
