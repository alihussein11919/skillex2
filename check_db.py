import mysql.connector
from mysql.connector import Error

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'skillex'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"❌ Database connection error: {e}")
        return None

def check_tables():
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return
    
    cursor = conn.cursor()
    
    try:
        # List all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\n=== Tables in skillex database ===")
        for table in tables:
            print(f"- {table[0]}")
        
        # Check lessons table structure
        try:
            cursor.execute("DESCRIBE lessons")
            columns = cursor.fetchall()
            print("\n=== Structure of lessons table ===")
            for col in columns:
                print(f"- {col[0]}: {col[1]}")
        except Error as e:
            print(f"\nlessons table doesn't exist or can't be accessed: {e}")
        
        # Check if any lessons exist
        try:
            cursor.execute("SELECT COUNT(*) FROM lessons")
            count = cursor.fetchone()[0]
            print(f"\n=== Count of lessons: {count} ===")
            
            if count > 0:
                cursor.execute("SELECT * FROM lessons LIMIT 5")
                lessons = cursor.fetchall()
                print("\nFirst few lessons:")
                for lesson in lessons:
                    print(f"- ID: {lesson[0]}, Teacher: {lesson[1]}, Title: {lesson[2]}")
        except Error as e:
            print(f"\nCannot query lessons: {e}")
    
    except Error as e:
        print(f"Error querying database: {e}")
    
    finally:
        cursor.close()
        conn.close()
        print("\nDatabase connection closed")

if __name__ == "__main__":
    check_tables() 