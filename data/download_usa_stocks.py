import requests
import pandas as pd
import os

def get_usa_stock_data():
  # URL and headers
  csv_url = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25&offset=0&download=true"
  headers = {
      "Accept": "application/json, text/plain, */*",
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67",
  }

  # Fetching the data
  response = requests.get(csv_url, headers=headers).json()
  data = response['data']

  # Extracting columns and rows
  columns = data['headers']
  body = data['rows']

  # Creating a DataFrame
  df = pd.DataFrame(body, columns=columns)
  return df


if __name__ == "__main__":

    df = get_usa_stock_data()
    df['marketCap'] = pd.to_numeric(df['marketCap'], errors='coerce')
    filtered_df = df[(df['marketCap'] != 0) & (df['marketCap'].notna())]

    # Filter rows where 'Market Cap' is greater than 15,000,000,000
    filtered_df = filtered_df[filtered_df['marketCap'] > 15000000000]
    # Define the symbols to drop
    symbols_to_drop = ['BRK/A', 'BRK/B']

    # Use boolean indexing with isin() to drop rows
    filtered_df = filtered_df[~filtered_df['symbol'].isin(symbols_to_drop)]
    
    # List of tickers for stocks whose market cap is greater than 15,000,000,000
    tickers = filtered_df['symbol'].tolist()

    # Directory and file path
    data_dir = 'data'
    output_file = os.path.join(data_dir, 'usa_stocks_over_15B.csv')

    # Create the directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)

    # Save the tickers to a CSV file
    pd.DataFrame(tickers, columns=['symbol']).to_csv(output_file, index=False)

    print(f"Saved {len(tickers)} tickers to {output_file}")