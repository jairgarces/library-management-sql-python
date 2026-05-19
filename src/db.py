import mysql.connector
from mysql.connector import Error

# Adjust these to match your MySQL setup
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,  #your port
    "user": "Antonio", #your sql username
    "password": "", # yoursqlpassword
    "database": "book_fetch",  # or whatever schema name you used
}


def get_connection():
    """
    Returns a new MySQL connection using the config above.
    Raises an Error if connection fails.
    """
    return mysql.connector.connect(**DB_CONFIG)


def test_connection():
    """
    Simple test: connect and run SELECT 1.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        print("DB test result:", result)
        cursor.close()
        conn.close()
        print("Database connection successful.")
    except Error as e:
        print("Database connection failed:")
        print(e)


if __name__ == "__main__":
    test_connection()
