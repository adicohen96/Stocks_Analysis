from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config.config import DATABASE_URI
import logging

# Configure logging (if not already configured)
logging.basicConfig(
    filename='query_logs.log',
    level=logging.INFO,  # Log level INFO to capture all query logs
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class Database:
    def __init__(self, uri):
        self.engine = create_engine(uri)
        self.Session = sessionmaker(bind=self.engine)

    def get_connection(self):
        return self.engine.connect()

    def execute_query(self, query, parameters=None, connection=None):
        if connection is None:
            with self.engine.connect() as conn:
                try:
                    result = conn.execute(text(query), parameters)
                    # Log successful query execution
                    logging.info(f"Successfully executed query: {query} with parameters: {parameters}")
                    return result
                except Exception as e:
                    # Log error and print failure details
                    logging.error(f"Error executing query: {query} with parameters: {parameters} - {e}")
                    print(f"Error executing query: {query} with parameters: {parameters} - {e}")
                    raise
        else:
            try:
                result = connection.execute(text(query), parameters)
                # Log successful query execution
                logging.info(f"Successfully executed query: {query} with parameters: {parameters}")
                return result
            except Exception as e:
                # Log error and print failure details
                logging.error(f"Error executing query: {query} with parameters: {parameters} - {e}")
                print(f"Error executing query: {query} with parameters: {parameters} - {e}")
                raise


    def create_table(self, create_table_sql):
        with self.engine.connect() as connection:
            try:
                print(f"Executing SQL: {create_table_sql}")
                connection.execute(text(create_table_sql))
                # Commit the transaction to ensure table creation
                connection.commit()
                print("Table created successfully.")
            except Exception as e:
                print(f"Error creating table: {e}")
                raise

    def drop_table(self, table_name):
        drop_table_sql = f"DROP TABLE IF EXISTS {table_name} CASCADE"
        try:
            with self.engine.connect() as connection:
                connection.execute(text(drop_table_sql))
        except Exception as e:
            print(f"Error executing drop table command: {e}")

# Example usage
if __name__ == "__main__":

    URI = DATABASE_URI #'postgresql://adic:123123@localhost/stockdb'
    db = Database(URI)

    # Test the connection
    try:
        with db.get_connection() as conn:
            print("Database connection successful.")
    except Exception as e:
        print(f"Error connecting to the database: {e}")
