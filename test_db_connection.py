# test_db_connection.py
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import pymysql
from sqlalchemy import text

pymysql.install_as_MySQLdb()  # Force pymysql to replace MySQLdb

# Define the database URI for local testing
DATABASE_URI = "mysql://root:JBPrjzJPqKoyrMfvEuReoqPcknAhQuBU@yamanote.proxy.rlwy.net:12386/railway"  # Adjust password if needed

def test_connection():
    try:
        # Create an SQLAlchemy engine
        engine = create_engine(DATABASE_URI, echo=True)  # echo=True for debug output
        print(f"Using URI: {DATABASE_URI}")
        
        # Attempt to connect
        connection = engine.connect()
        print("Connection successful!")
        
        # Run a simple query using text()
        result = connection.execute(text("SELECT DATABASE()")).fetchone()
        print(f"Connected to database: {result[0]}")
        connection.close()
    except OperationalError as e:
        print(f"Connection failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'connection' in locals():
            connection.close()
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    # Verify pymysql is available
    try:
        import pymysql
        print("pymysql is installed and imported successfully")
    except ImportError:
        print("pymysql is not installed. Please run 'pip install pymysql'")
        exit(1)
    
    test_connection()