from flask import Flask, request, jsonify, send_from_directory, abort
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from flask_cors import CORS
from functools import wraps
import random

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/users": {"origins": "http://localhost:3000"}})

db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT', 3306))
}

def with_db_connection(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        connection = None
        try:
            connection = mysql.connector.connect(**db_config)
            if not connection.is_connected():
                abort(500, "Database connection failed.")
            return f(connection, *args, **kwargs)
        except Error as err:
            abort(500, str(err))
        finally:
            if connection and connection.is_connected():
                connection.close()
    return decorated_function

# ===================================================================

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# ===================================================================

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# ===================================================================

@app.route('/users', methods=['GET'])
@with_db_connection
def get_users(connection):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    cursor.close()
    return jsonify(results)

# ===================================================================

@app.route('/users/<int:user_id>', methods=['GET'])
@with_db_connection
def get_user(connection, user_id):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return jsonify(user)
    abort(404, "Entry does not exist")

# ===================================================================

def is_valid_employee(id):
    return id.isdigit()

def is_valid_name(name):
    return name.isalpha()

# ===================================================================
@app.route('/users', methods=['POST'])
@with_db_connection
def create_user(connection):
    data = request.get_json()

    # Check for required fields in the input
    if not data or 'first_name' not in data or 'last_name' not in data:
        abort(400, "Invalid data provided.")

    if not is_valid_name(data['first_name']):
        abort(400, 'Please enter alphabetical characters Only')
    
    if not is_valid_name(data['last_name']):
        abort(400, 'Please enter alphabetical characters Only')
    
    cursor = connection.cursor()

    # Generate a unique 4-digit employee_id
    attempts = 0  # To prevent infinite loop in case of unforeseen issues
    while attempts < 10:  # Limit attempts to avoid infinite loop
        employee_id = random.randint(1000, 9999)  # Generate a random 4-digit number
        cursor.execute("SELECT COUNT(*) FROM users WHERE employee_id = %s", (employee_id,))
        if cursor.fetchone()[0] == 0:  # Check if the employee_id is unique
            break
        attempts += 1

    if attempts == 10:
        abort(500, "Could not generate a unique employee ID after multiple attempts.")

    # Insert new user into the database with the generated employee_id
    try:
        cursor.execute(""" 
            INSERT INTO users (employee_id, first_name, last_name)
            VALUES (%s, %s, %s)
        """, (employee_id, data['first_name'], data['last_name']))
        
        connection.commit()
    except Exception as e:
        print(f"Database insert error: {e}")  # Log the exact error
        abort(500, "Failed to create user.")

    cursor.close()

    # Return a success message with the assigned employee_id
    return jsonify({"message": "User created successfully.", "employee_id": employee_id}), 201

# ===================================================================

@app.route('/users/<int:user_id>', methods=['PUT'])
@with_db_connection
def update_user(connection, user_id):
    update_data = request.get_json()
    if not update_data:
        abort(400, "No input data provided.")
    
    if 'first_name' not in update_data or 'last_name' not in update_data:
        abort(400, "First name and last name are required.")

    if not is_valid_employee(user_id):
        abort(400, 'Invalid user ID. Please enter numerical characters only.')

    if not is_valid_name(update_data['first_name']):
        abort(400, 'First name must contain alphabetical characters only.')
    
    if not is_valid_name(update_data['last_name']):
        abort(400, 'Last name must contain alphabetical characters only.')
    
    cursor = connection.cursor()
    
    try:
        cursor.execute("UPDATE users SET first_name = %s, last_name = %s WHERE employee_id = %s",
                       (update_data['first_name'], update_data['last_name'], user_id))
        connection.commit()

        if cursor.rowcount == 0:
            abort(404, "User not found")
        
        return jsonify({"message": "User updated successfully."})
    except Exception as e:
        # Log the exception for debugging
        print("Entry does not exist:")
        abort(500, "NO ENTRY")
    finally:
        cursor.close()

# ===================================================================

@app.route('/users/<int:user_id>', methods=['DELETE'])
@with_db_connection
def delete_user(connection, user_id):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM users WHERE employee_id = %s", (user_id,))
    connection.commit()
    cursor.close()

    if cursor.rowcount == 0:
        abort(404, "Entry does not exist")
    
    return jsonify({"message": "User deleted successfully."})

# ===================================================================

@app.route('/test-db-connection')
@with_db_connection
def test_db_connection(connection):
    return jsonify({"message": "Database connection successful!"}), 200

# ===================================================================

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5500)


