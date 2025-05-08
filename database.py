import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',  # XAMPP default is empty
            'database': 'skillex',
            'raise_on_warnings': True
        }
        self.connection = None

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                print("Successfully connected to MySQL database")
                return self.connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

    def execute_query(self, query, params=None):
        """Execute a SQL query"""
        cursor = None
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
                
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            # For SELECT queries
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            # For INSERT/UPDATE/DELETE
            else:
                self.connection.commit()
                return cursor.rowcount
                
        except Error as e:
            print(f"Database error: {e}")
            if self.connection:
                self.connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()

    def initialize_database(self):
        """Create database and tables if they don't exist"""
        temp_conn = None
        cursor = None
        try:
            # First connect without specifying database
            print("Attempting to connect to MySQL server...")
            temp_conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password=''
            )
            
            if not temp_conn.is_connected():
                print("Failed to connect to MySQL server")
                return False
                
            print("Connected to MySQL server successfully")
            cursor = temp_conn.cursor()
            
            # Create database
            print("Attempting to create 'skillex' database...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS skillex")
            print("Database creation command executed")
            
            # Switch to database
            print("Switching to 'skillex' database...")
            cursor.execute("USE skillex")
            
            # Create users table
            print("Creating users table...")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """)
            
            temp_conn.commit()
            print("Database 'skillex' initialized successfully")
            return True
            
        except Error as e:
            print(f"Initialization error: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if temp_conn and temp_conn.is_connected():
                temp_conn.close()
                print("Temporary connection closed")