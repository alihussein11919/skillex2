from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

# Database Connection
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Keep blank if no password
    'database': 'skillex'  # Make sure this matches your database name
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Test API
@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({"message": "API is working!"})

# Fetch all users
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")  # Ensure you have a 'users' table
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

# Add a new user
@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.json  # Get JSON data from request
    name = data['name']
    email = data['email']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "User added successfully!"}), 201
    
@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Skillex API!"})

if __name__ == "__main__":
    app.run(debug=True, port=5002)  # Runs on port 5002 to avoid conflicts
