import pandas as pd
import requests
from time import sleep
from fake_useragent import UserAgent
import yfinance as yf
import logging
import os
from src.database import Database
from sqlalchemy.exc import SQLAlchemyError
from config.config import DATABASE_URI

# Initialize database connection
db = Database(DATABASE_URI)

# Initialize UserAgent
ua = UserAgent()

# Create a session
session = requests.Session()

# Setup logging
logging.basicConfig(
    filename='failed_downloads.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def fetch_data_with_limit(ticker, session):
    # Update user agent
    session.headers['User-agent'] = ua.random
    
    # Fetch data
    try:
        df = yf.download(ticker, start='2023-01-01', end=pd.Timestamp.today().strftime('%Y-%m-%d'), session=session)
        df.index = df.index.date
        df.index.name = 'Date'
        df = df.astype({
            'Open': 'float',
            'High': 'float',
            'Low': 'float',
            'Close': 'float',
            'Volume': 'float'
        })
        return df
    except Exception as e:
        logging.error(f"Error downloading data for {ticker}: {e}")
        return None

def fetch_stock_details(ticker):
    stock = yf.Ticker(ticker)
    name = stock.info.get('shortName', 'N/A')
    market_cap_str = stock.info.get('marketCap', 'N/A')
    
    # Convert market_cap to a numeric value or None
    try:
        market_cap = float(market_cap_str)
    except (ValueError, TypeError):
        market_cap = None
    
    return {
        'ticker': ticker,
        'name': name,
        'market_cap': market_cap
    }

def download_historical_data(ticker, session):
    # Fetch data with rate limiting
    df = fetch_data_with_limit(ticker, session)
    return df

def main():
    db = Database(DATABASE_URI)
    
    # Path to the tickers file
    tickers_file_path = 'data/usa_stocks_over_15B.csv'
    tickers = pd.read_csv(tickers_file_path)['symbol'].tolist()
    #tickers = ['AAPL', 'AMZN', 'MSFT']

    tickers_map = {}
    failed_tickers = {}

    for index, ticker in enumerate(tickers):
        print(f"Downloading data for {ticker}...")
        stock_details = fetch_stock_details(ticker)
        
        # Insert stock data
        insert_stock_query = """
        INSERT INTO stocks (ticker, name, market_cap) 
        VALUES (:ticker, :name, :market_cap)
        ON CONFLICT (ticker) DO UPDATE
        SET name = EXCLUDED.name, market_cap = EXCLUDED.market_cap
        """
        connection = db.get_connection()  # Get a connection from the database
        try:
            with connection.begin():  # Ensure transaction is committed
                db.execute_query(insert_stock_query, {
                    'ticker': stock_details['ticker'],
                    'name': stock_details['name'],
                    'market_cap': stock_details['market_cap']
                }, connection)
                # Commit the transaction
                connection.commit()
        except SQLAlchemyError as e:
            logging.error(f"Error inserting stock data for {ticker}: {e}")
            connection.rollback()  # Rollback transaction in case of error
            continue  # Skip to the next ticker if insert fails
        
        # Verify if the stock has been inserted correctly
        select_id_query = "SELECT id FROM stocks WHERE ticker = :ticker"
        try:
            result = db.execute_query(select_id_query, {'ticker': ticker}, connection)
            stock_id = result.scalar()  # Use scalar() to get single value
        except SQLAlchemyError as e:
            logging.error(f"Error selecting stock id for {ticker}: {e}")
            continue  # Skip to the next ticker if select fails
        
        if stock_id is None:
            logging.error(f"Failed to retrieve stock_id for ticker: {ticker}")
            continue  # Skip to the next ticker if stock_id is not found

        print(f"Stock ID for {ticker}: {stock_id}")  # Debugging line
        
        # Download historical data
        df = download_historical_data(ticker, session)
        if df is not None:
            tickers_map[ticker] = df
            
            # Insert historical data
            for date, row in df.iterrows():
                insert_historical_query = """
                INSERT INTO historical_data (stock_id, date, open, high, low, close, volume) 
                VALUES (:stock_id, :date, :open, :high, :low, :close, :volume)
                ON CONFLICT (stock_id, date) DO UPDATE
                SET open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low, close = EXCLUDED.close, volume = EXCLUDED.volume
                """
                try:
                    with connection.begin():  # Ensure transaction is committed
                        db.execute_query(insert_historical_query, {
                            'stock_id': stock_id,
                            'date': date,
                            'open': float(row['Open']),
                            'high': float(row['High']),
                            'low': float(row['Low']),
                            'close': float(row['Close']),
                            'volume': float(row['Volume'])
                        }, connection)
                        # Commit the transaction
                        connection.commit()
                except SQLAlchemyError as e:
                    logging.error(f"Error inserting historical data for {ticker} on {date}: {e}")
                    connection.rollback()  # Rollback transaction in case of error
        else:
            failed_tickers[ticker] = 'Data fetch failed'
        
        # Sleep for 7 seconds after every 50 tickers (not needed here but left for structure)
        if (index + 1) % 50 == 0:
            print("Sleeping for 7 seconds...")
            sleep(7)

    print("Data download complete.")
    
    # Log failed tickers
    if failed_tickers:
        logging.error("Failed to download data for the following tickers:")
        for ticker, reason in failed_tickers.items():
            logging.error(f"{ticker}: {reason}")

    return tickers_map

if __name__ == "__main__":
    main()



# def get_stock_id(ticker):
#     # Define the query to get the stock_id for a given ticker
#     select_id_query = "SELECT id FROM stocks WHERE ticker = :ticker"
    
#     # Execute the query
#     result = db.execute_query(select_id_query, {'ticker': ticker})
    
#     # Fetch the stock_id from the result
#     stock_id = result.scalar()  # Use scalar() to get a single value
    
#     return stock_id

# # Example usage
# ticker = 'AMZN'
# stock_id = get_stock_id(ticker)
# print(f"Stock ID for {ticker}: {stock_id}")