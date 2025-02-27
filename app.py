import string
import random
from flask import Flask, request, jsonify
import pymysql
import jwt
import datetime
from functools import wraps
import bcrypt  # Add this import at the top
from flask_cors import CORS  # Import CORS
import os  # Import os for file handling
from werkzeug.utils import secure_filename


app = Flask(__name__)
CORS(app)  # Enable CORS for the entire application

# connection=pymysql.connect(host="maxmusau.mysql.pythonanywhere-services.com",user="maxmusau",database="maxmusau$default",password="maxwell1234")
# Database configuration
app.config['MYSQL_HOST'] = 'maxmusau.mysql.pythonanywhere-services.com'
app.config['MYSQL_USER'] = 'maxmusau'
app.config['MYSQL_PASSWORD'] = 'maxwell1234'
app.config['MYSQL_DB'] = 'maxmusau$default'

# Secret key for JWT
app.config['SECRET_KEY'] = 'LFKSJDWIE($%*$&#@$&#@53498ikdfhnksdjf4i3o)'  # Change this to a strong secret

# Add this line to set the path for the static folder
STATIC_FOLDER = os.path.join(os.getcwd(), 'static')

#main route
@app.route("/")
def Main():
    return "Weelcome to your application"
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

# Unified Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    try:
        # Check if the email exists in the users table
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (data['email'],))
        user = cur.fetchone()
        
        if user:
            # User found, check the role
            role = user[4]  # Assuming user[4] is the role column
            if role in ['admin', 'user']:
                # Check the hashed password
                if bcrypt.checkpw(data['password'].encode('utf-8'), user[3].encode('utf-8')):  # Assuming user[3] is the hashed password
                    # Generate JWT token with 24 hours expiration
                    expiration_time_utc = datetime.datetime.utcnow() + datetime.timedelta(days=1)  # 24 hours
                    
                    token = jwt.encode({'id': user[0], 'exp': expiration_time_utc}, 
                                       app.config['SECRET_KEY'], algorithm="HS256")
                    
                    return jsonify({
                        'message': 'Login successful',
                        'token': token,
                        'expires': expiration_time_utc.isoformat(),  # Return the expiry date in UTC
                        'role': role  # Return the role
                    }), 200
                else:
                    return jsonify({'message': 'Invalid email or password'}), 401
            else:
                return jsonify({'message': 'Invalid role for user'}), 403
        
        # If not found in users, check in sellers table
        cur.execute("SELECT * FROM sellers WHERE email = %s", (data['email'],))
        seller = cur.fetchone()
        
        if seller:
            # Check the hashed password
            if bcrypt.checkpw(data['password'].encode('utf-8'), seller[3].encode('utf-8')):  # Assuming seller[3] is the hashed password
                # Generate JWT token with 24 hours expiration
                expiration_time_utc = datetime.datetime.utcnow() + datetime.timedelta(days=1)  # 24 hours
                
                token = jwt.encode({'id': seller[0], 'exp': expiration_time_utc}, 
                                   app.config['SECRET_KEY'], algorithm="HS256")

                #fetch the seller id and return it
                seller_id = seller[0]

                return jsonify({
                    'message': 'Seller login successful',
                    'token': token,
                    'expires': expiration_time_utc.isoformat(),  # Return the expiry date in UTC
                    'seller_id': seller_id,
                    'role': 'seller'  # Return the role

                }), 200
            else:
                return jsonify({'message': 'Invalid email or password'}), 401
        else:
            return jsonify({'message': 'Invalid email or password'}), 401
        
    except Exception as e:
        return jsonify({'message': 'Failed to log in', 'error': str(e)}), 500

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
# Example protected endpoint (remains the same)
@app.route('/protected')
@token_required
def protected(current_user):
    return jsonify({'message': 'Protected endpoint accessed', 'user_id': current_user}), 200
@app.route('/items', methods=['GET'])
def get_all_items():
    try:
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM items")
        items = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(items), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch items', 'error': str(e)}), 500

# Add a new item (seller only)
# @app.route('/add-items', methods=['POST'])
# def add_item():
#     data = request.form  # Use request.form to handle form data
#     image_file = request.files['image']  # Get the uploaded image file

#     # Generate a unique ID for the item
#     new_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

#     # Save the image file to the static folder
#     if image_file:
#         image_filename = f"{new_id}_{image_file.filename}"  # Create a unique filename
#         image_path = os.path.join(STATIC_FOLDER, image_filename)
#         image_file.save(image_path)  # Save the file

#     try:
#         conn = pymysql.connect(
#             host=app.config['MYSQL_HOST'],
#             user=app.config['MYSQL_USER'],
#             password=app.config['MYSQL_PASSWORD'],
#             database=app.config['MYSQL_DB']
#         )
#         cur = conn.cursor()
        
#         # Insert the new item into the items table
#         cur.execute("""
#             INSERT INTO items (id, title, description, image, base_price, seller_id, end_time)
#             VALUES (%s, %s, %s, %s, %s, %s, NOW() + INTERVAL 30 MINUTE)
#         """, (new_id, data['title'], data['description'], image_filename, data['base_price'], data['seller_id']))
        
#         conn.commit()
#         cur.close()
#         conn.close()
#         return jsonify({'message': 'Item added successfully'}), 201
#     except Exception as e:
#         print(f"Error occurred: {str(e)}")  # Print the error for debugging
#         return jsonify({'message': 'Failed to add item', 'error': str(e)}), 500

MEDIA_FOLDER = os.path.join(os.getcwd(), "media", "images")
os.makedirs(MEDIA_FOLDER, exist_ok=True)  # Create if it doesn't exist

# @app.route('/add-items', methods=['POST'])
# def add_item():
#     try:
#         data = request.form  # Use request.form to handle form data
#         image_file = request.files.get('image')  # Get the uploaded image file

#         # Generate a unique ID for the item
#         new_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

#         # Save the image file to the media folder
#         if image_file:
#             image_filename = f"{new_id}_{secure_filename(image_file.filename)}"
#             image_path = os.path.join(MEDIA_FOLDER, image_filename)
#             image_file.save(image_path)  # Save the file
#         else:
#             image_filename = None  # No image uploaded

#         # Connect to MySQL database
#         conn = pymysql.connect(
#             host=app.config['MYSQL_HOST'],
#             user=app.config['MYSQL_USER'],
#             password=app.config['MYSQL_PASSWORD'],
#             database=app.config['MYSQL_DB']
#         )
#         cur = conn.cursor()

#         # Insert the new item into the database
#         cur.execute("""
#             INSERT INTO items (id, title, description, image, base_price, seller_id, end_time)
#             VALUES (%s, %s, %s, %s, %s, %s, NOW() + INTERVAL 30 MINUTE)
#         """, (new_id, data['title'], data['description'], image_filename, data['base_price'], data['seller_id']))

#         conn.commit()
#         cur.close()
#         conn.close()

#         return jsonify({'message': 'Item added successfully'}), 201

#     except Exception as e:
#         print(f"Error occurred: {str(e)}")  # Debugging
#         return jsonify({'message': 'Failed to add item', 'error': str(e)}), 500





# new code
@app.route('/add-items', methods=['POST'])
def add_item():
    try:
        # Log form data
        print("Form Data:", request.form)
        # Log files
        print("Files:", request.files)

        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        base_price = request.form.get('base_price')
        seller_id = request.form.get('seller_id')
        image_file = request.files.get('image')  # Get the uploaded image file

        # Validate required fields
        if not all([title, description, base_price, seller_id]):
            return jsonify({'message': 'Missing required fields'}), 400

        # Generate a unique ID for the item
        new_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

        # Save the image file to the media folder
        if image_file:
            image_filename = f"{new_id}_{secure_filename(image_file.filename)}"
            image_path = os.path.join(app.config['MEDIA_FOLDER'], image_filename)
            image_file.save(image_path)  # Save the file
        else:
            image_filename = None  # No image uploaded

        # Connect to MySQL database
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        
        cur = conn.cursor()

        # Insert the new item into the database
        cur.execute("""
            INSERT INTO items (item_id, title, description, image, base_price, seller_id, end_time)
            VALUES (%s, %s, %s, %s, %s, %s, NOW() + INTERVAL 30 MINUTE)
        """, (new_id, title, description, image_filename, base_price, seller_id))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'message': 'Item added successfully'}), 201

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debugging
        return jsonify({'message': 'Failed to add item', 'error': str(e)}), 500



# # Place a bid


@app.route('/bid/<item_id>', methods=['POST'])
# @token_required
def place_bid(current_user, item_id):
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
        cur.execute("INSERT INTO bids (item_id, bidder_id,title, bid_amount, timestamp) VALUES (%s, %s, %s, NOW())",
                    (item_id, current_user, data['bid_amount']))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Bid placed successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Failed to place bid', 'error': str(e)}), 500

# Fetch bid history
@app.route('/bid-history/<item_id>', methods=['GET'])
def get_bid_history(item_id):
    try:
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM bids WHERE item_id = %s ORDER BY timestamp", (item_id,))
        bid_history = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(bid_history), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch bid history', 'error': str(e)}), 500

# Fetch auction winner
@app.route('/winner/<item_id>', methods=['GET'])
def get_winner(item_id):
    try:
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        cur = conn.cursor()
        cur.execute("SELECT bidder_id, MAX(bid_amount) FROM bids WHERE item_id = %s GROUP BY bidder_id ORDER BY MAX(bid_amount) DESC LIMIT 1", (item_id,))
        winner = cur.fetchone()
        cur.close()
        conn.close()
        if winner:
            return jsonify({'winner': winner}), 200  # Return the bidder_id of the winner
        else:
            return jsonify({'message': 'No bids found for this item'}), 404
    except Exception as e:
        return jsonify({'message': 'Failed to fetch winner', 'error': str(e)}), 500

# Add a new seller
@app.route('/add-seller', methods=['POST'])
def add_seller():
    data = request.get_json()
    
    # Generate a unique seller ID
    seller_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    # Hash the password for security
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

    try:
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        cur = conn.cursor()
        
        # Check if the username or email already exists
        cur.execute("SELECT * FROM sellers WHERE username = %s OR email = %s", (data['username'], data['email']))
        existing_seller = cur.fetchone()
        
        if existing_seller:
            return jsonify({'message': 'Username or email already exists'}), 400
        
        # Insert the new seller into the sellers table
        cur.execute("""
            INSERT INTO sellers (seller_id, username, email, password, phone, address, role)
            VALUES (%s, %s, %s, %s, %s, %s, 'seller')
        """, (seller_id, data['username'], data['email'], hashed_password, data['phone'], data['address']))
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Seller added successfully', 'seller_id': seller_id}), 201
    except Exception as e:
        return jsonify({'message': 'Failed to add seller', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)