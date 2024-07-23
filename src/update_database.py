import pandas as pd
from datetime import datetime, time
import pytz
from src.database import Database
from config.config import DATABASE_URI

# Initialize database connection
db = Database(DATABASE_URI)

def get_latest_date_for_ticker(ticker):
    # Query to get the latest date for the ticker
    query = """
    SELECT MAX(date) FROM historical_data
    JOIN stocks ON historical_data.stock_id = stocks.id
    WHERE stocks.ticker = :ticker
    """
    result = db.execute_query(query, {'ticker': ticker})
    return result.scalar()  # Return the latest date or None

def should_skip_fetch(latest_date):
    tz = pytz.timezone('Asia/Jerusalem')
    now = datetime.now(tz)
    
    if latest_date is None:
        return False  # No data in the table, so always fetch

    # Check if the latest date is Friday
    if latest_date.weekday() == 4:  # 4 means Friday
        # If today is Saturday or Sunday, skip fetch
        if now.weekday() in [5, 6]:  # 5 means Saturday, 6 means Sunday
            return True
        # If today is Monday, check time
        elif now.weekday() == 0 and now.time() < time(23, 0):
            return True
    
    return False

def update_data():
    # Get all tickers
    tickers_query = "SELECT ticker FROM stocks"
    tickers = db.execute_query(tickers_query).scalars().all()

    for ticker in tickers:
        print(f"Checking data for {ticker}...")
        latest_date = get_latest_date_for_ticker(ticker)
        if should_skip_fetch(latest_date):
            print(f"Skipping {ticker} as data is up-to-date.")
            continue
        
        # Perform data fetch and update if necessary
        print(f"Fetching new data for {ticker}...")
        # Add your data fetching and updating logic here
        
        # Example: df = fetch_data(ticker)
        # and then update your database with the new data

if __name__ == "__main__":
    update_data()
