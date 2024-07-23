from src.database import Database
from config.config import DATABASE_URI

URI = DATABASE_URI

def drop_tables():
    db = Database(DATABASE_URI)
    try:
        db.drop_table('test_table')
        db.drop_table('query_test')
        print("Tables dropped successfully.")
    except Exception as e:
        print(f"Error dropping tables: {e}")

if __name__ == "__main__":
    drop_tables()
