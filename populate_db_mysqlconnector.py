import mysql.connector
from mysql.connector import Error
import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Union

class SkillexDatabase:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',
            'raise_on_warnings': True
        }
        self.connection = None
    
    def connect(self, database: Optional[str] = None) -> bool:
        """Connect to MySQL with optional database parameter"""
        try:
            config = self.config.copy()
            if database:
                config['database'] = database
            self.connection = mysql.connector.connect(**config)
            if self.connection.is_connected():
                print(f"✅ Connected to {database if database else 'MySQL server'}")
                return True
            return False
        except Error as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close database connection safely"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 Database connection closed")
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[tuple] = None, 
        fetch: bool = False
    ) -> Union[int, List[Dict], None]:
        """Execute a SQL query with comprehensive error handling"""
        cursor = None
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect(self.config.get('database')):
                    return None
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                return result if result else []
            else:
                self.connection.commit()
                return cursor.rowcount
                
        except Error as e:
            print(f"⚠️ Query error: {e}")
            if self.connection:
                self.connection.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
    
    def initialize_database(self) -> bool:
        """Initialize the database and tables with proper checks"""
        try:
            # Connect to server without specifying database
            if not self.connect():
                return False
            
            # Create database if not exists (ignore if exists)
            self.execute_query("CREATE DATABASE IF NOT EXISTS skillex CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            self.disconnect()
            
            # Reconnect to the specific database
            if not self.connect('skillex'):
                return False
            
            # Create tables with IF NOT EXISTS and proper error handling
            self.create_tables()
            
            print("✅ Database initialized successfully")
            return True
        except Error as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    def create_tables(self) -> None:
        """Create all tables with proper constraints and error handling"""
        # Users table
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL DEFAULT 'default_password',
            role ENUM('admin','teacher','student') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_role (role)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Skills table
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS skills (
            skill_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # User-Skills junction table
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS user_skills (
            user_skill_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            skill_id INT NOT NULL,
            proficiency_level ENUM('beginner','intermediate','advanced','expert') DEFAULT 'intermediate',
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE,
            UNIQUE KEY unique_user_skill (user_id, skill_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Teachers table
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS teachers (
            teacher_id INT PRIMARY KEY,
            bio TEXT,
            FOREIGN KEY (teacher_id) REFERENCES users(user_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Students table
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INT PRIMARY KEY,
            learning_goals TEXT,
            FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Lessons table
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS lessons (
            lesson_id INT AUTO_INCREMENT PRIMARY KEY,
            teacher_id INT NOT NULL,
            student_id INT NOT NULL,
            skill_id INT NOT NULL,
            scheduled_time DATETIME NOT NULL,
            duration_minutes INT NOT NULL DEFAULT 60,
            status ENUM('scheduled','completed','canceled') DEFAULT 'scheduled',
            price DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Messages table
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id INT AUTO_INCREMENT PRIMARY KEY,
            sender_id INT NOT NULL,
            receiver_id INT NOT NULL,
            content TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES users(user_id) ON DELETE CASCADE,
            INDEX idx_conversation (sender_id, receiver_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Matches table
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS matches (
            match_id INT AUTO_INCREMENT PRIMARY KEY,
            teacher_id INT NOT NULL,
            student_id INT NOT NULL,
            matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            UNIQUE KEY unique_match (teacher_id, student_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Reviews table
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INT AUTO_INCREMENT PRIMARY KEY,
            lesson_id INT,
            reviewer_id INT NOT NULL,
            reviewee_id INT NOT NULL,
            rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id) ON DELETE SET NULL,
            FOREIGN KEY (reviewer_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (reviewee_id) REFERENCES users(user_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Marketplace products
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS marketplace_products (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            teacher_id INT NOT NULL,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            price DECIMAL(10,2) NOT NULL,
            is_available BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Orders table
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            product_id INT,
            lesson_id INT,
            amount DECIMAL(10,2) NOT NULL,
            status ENUM('pending','completed','refunded') DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES marketplace_products(product_id) ON DELETE SET NULL,
            FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Admin logs
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS admin_logs (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            admin_id INT NOT NULL,
            action VARCHAR(50) NOT NULL,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_id) REFERENCES users(user_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
    
    

def main():
    db = SkillexDatabase()
    try:
        if db.initialize_database():
            pass  # no dummy data
    finally:
        db.disconnect()
        print("🏁 Script execution completed")


if __name__ == "__main__":
    main()