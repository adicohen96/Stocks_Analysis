import unittest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from config.config import DATABASE_URI
from src.database import Database
import pandas as pd

class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database_uri = 'postgresql://adic:123123@localhost/stockdb'  # Update with correct details
        cls.engine = create_engine(cls.database_uri)
        cls.Session = sessionmaker(bind=cls.engine)

    def test_connection(self):
        try:
            with self.engine.connect() as conn:
                self.assertFalse(conn.closed)
        except OperationalError as e:
            self.fail(f"Database connection test failed: {e}")
    def test_create_table(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS test_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL
        )
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text(create_table_sql))
                result = conn.execute(text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'test_table')"))
                exists = result.fetchone()[0]
                self.assertTrue(exists, "Table 'test_table' was not created.")
        except OperationalError as e:
            self.fail(f"Table creation test failed: {e}")

    def test_execute_query(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS query_test (
            id SERIAL PRIMARY KEY,
            value INTEGER
        )
        """
        insert_sql = "INSERT INTO query_test (value) VALUES (1)"
        select_sql = "SELECT value FROM query_test"

        try:
            with self.engine.connect() as conn:
                # Create table
                conn.execute(text(create_table_sql))
                # Insert data
                conn.execute(text(insert_sql))
                # Query data
                result = conn.execute(text(select_sql))
                values = result.fetchall()
                self.assertIn((1,), values, "Expected value not found in 'query_test' table.")
        except OperationalError as e:
            self.fail(f"Query execution test failed: {e}")

if __name__ == '__main__':
    db_connection = Database(DATABASE_URI)

    # Define the SQL query
    query = "SELECT ticker FROM stocks WHERE market_cap IS NULL;"

    # Execute the query and load the data into a DataFrame
    df = pd.read_sql_query(query, db_connection.get_connection())

    # Extract the list of tickers
    tickers = df['ticker'].tolist()

    print(tickers)
    print(len(tickers))
    #unittest.main()
