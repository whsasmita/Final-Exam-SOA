import pymysql
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def get_connection():
    """Membuat koneksi ke database MySQL."""
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.Error as err:
        print(f"Error: {err}")
        return None

def execute_query(query, params=None, fetch=True):
    """Eksekusi query dengan parameter."""
    connection = get_connection()
    if not connection:
        return None
    
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
            else:
                connection.commit()
                result = cursor.rowcount
                
        return result
    except pymysql.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        connection.close()

if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print("✅ Database connection successful!")
        conn.close()
    else:
        print("❌ Database connection failed!")