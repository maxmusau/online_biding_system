import string
import random
from flask import Flask, request, jsonify
import pymysql
import jwt
import datetime
from functools import wraps
import bcrypt  # Add this import at the top

app = Flask(__name__)

# Database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'biddingDB'

# Secret key for JWT
app.config['SECRET_KEY'] = 'LFKSJDWIE($%*$&#@$&#@53498ikdfhnksdjf4i3o)'  # Change this to a strong secret

# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE id = %s", (data['id'],))
            current_user = cur.fetchone()
            cur.close()
        except:
            return jsonify({'message': 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Registration endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    # Input validation here (e.g., check for missing fields)
    
    try:
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        cur = conn.cursor()
        
        # Check if the username or email already exists
        cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (data['username'], data['email']))
        existing_user = cur.fetchone()
        
        if existing_user:
            return jsonify({'message': 'Username or email already exists'}), 400
        
        # Generate a 5-digit varchar ID
        new_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        
        # Hash the password
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        
        cur.execute("INSERT INTO users (id, username, email, password, role) VALUES (%s, %s, %s, %s, %s)",
                    (new_id, data['username'], data['email'], hashed_password, data['role']))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Failed to register user', 'error': str(e)}), 500

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    #... (Input validation here)...

    try:
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (data['email'],))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            print("Stored hashed password:", user[3])  # Print the stored hashed password
            print("Provided password:", data['password'])  # Print the provided password
            print("data['password']: ", data['password'].encode('utf-8'))
            if bcrypt.checkpw(data['password'].encode('utf-8'), user[3].encode('utf-8')):
                # Generate JWT token
                expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                token = jwt.encode({'id': user[0], 'exp': expiration_time}, 
                                   app.config['SECRET_KEY'], algorithm="HS256")
                
                return jsonify({
                    'message': 'Login successful',
                    'token': token,
                    'expires': expiration_time.isoformat()  # Return the expiry date in ISO format
                }), 200
            else:
                return jsonify({'message': 'Invalid email or password'}), 401
        else:
            return jsonify({'message': 'Invalid email or password'}), 401
    except Exception as e:
        return jsonify({'message': 'Failed to log in', 'error': str(e)}), 500

# Example protected endpoint (remains the same)
@app.route('/protected')
@token_required
def protected(current_user):
    return jsonify({'message': 'Protected endpoint accessed', 'user_id': current_user}), 200


if __name__ == '__main__':
    app.run(debug=True)