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
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'biddingsystem'

# Secret key for JWT
app.config['SECRET_KEY'] = 'LFKSJDWIE($%*$&#@$&#@53498ikdfhnksdjf4i3o)'  # Change this to a strong secret

# Add this line to set the path for the static folder
# STATIC_FOLDER = os.path.join(os.getcwd(), 'static')

# Define MEDIA_FOLDER at the top of your app.py
MEDIA_FOLDER = os.path.join(os.getcwd(), "static")  # Use the static folder for images
os.makedirs(MEDIA_FOLDER, exist_ok=True)  # Create if it doesn't exist

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
        cur = conn.cursor(pymysql.cursors.DictCursor)  # Use DictCursor to return dictionaries
        cur.execute("SELECT * FROM items")
        items = cur.fetchall()  # This will now return a list of dictionaries
        cur.close()
        conn.close()
        return jsonify(items), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch items', 'error': str(e)}), 500
# Add a new item (seller only)
# @app.route('/add-items', methods=['POST'])
# def add_item():
#     try:
#         # Log form data
#         print("Form Data:", request.form)
#         # Log files
#         print("Files:", request.files)

#         # Get form data
#         title = request.form.get('title')
#         description = request.form.get('description')
#         base_price = request.form.get('base_price')
#         seller_id = request.form.get('seller_id')
#         image_file = request.files.get('image')  # Get the uploaded image file

#         # Validate required fields
#         if not all([title, description, base_price, seller_id]):
#             return jsonify({'message': 'Missing required fields'}), 400

#         # Generate a unique ID for the item
#         new_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

#         # Save the image file to the MEDIA_FOLDER
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
#         """, (new_id, title, description, image_filename, base_price, seller_id))

#         conn.commit()
#         cur.close()
#         conn.close()

#         return jsonify({'message': 'Item added successfully'}), 201

#     except Exception as e:
#         print(f"Error occurred: {str(e)}")  # Debugging
#         return jsonify({'message': 'Failed to add item', 'error': str(e)}), 500

import os
import random
import string
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import pymysql



# Define the static folder for storing images
STATIC_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(STATIC_FOLDER, exist_ok=True)  # Ensure the folder exists

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

        # Save the image file in static/uploads folder
        image_filename = None  # Default to None in case no image is uploaded
        if image_file:
            image_filename = f"{new_id}_{secure_filename(image_file.filename)}"
            image_path = os.path.join(STATIC_FOLDER, image_filename)
            image_file.save(image_path)  # Save image to static/uploads

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
            INSERT INTO items (id, title, description, image, base_price, seller_id, end_time)
            VALUES (%s, %s, %s, %s, %s, %s, NOW() + INTERVAL 30 MINUTE)
        """, (new_id, title, description, image_filename, base_price, seller_id))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'message': 'Item added successfully', 'image_url': f'/static/uploads/{image_filename}'}), 201

    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debugging
        return jsonify({'message': 'Failed to add item', 'error': str(e)}), 500




# # Place a bid


@app.route('/bid/<item_id>', methods=['POST'])
@token_required  # Ensure the user is authenticated
def place_bid(current_user, item_id):
    data = request.get_json()
    
    try:
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        cur = conn.cursor()
        cur.execute("INSERT INTO bids (item_id, bidder_id, bid_amount, timestamp) VALUES (%s, %s, %s, NOW())",
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

# Endpoint to fetch users with role "user"
@app.route('/users', methods=['GET'])
def get_users():
    try:
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE role = 'user'")  # Fetch users with role 'user'
        users = cur.fetchall()
        cur.close()
        conn.close()
        
        # Convert the result to a list of dictionaries for better readability
        user_list = []
        for user in users:
            user_list.append({
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'role': user[4]  # Assuming role is at index 4
            })
        
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch users', 'error': str(e)}), 500

# Endpoint to fetch all sellers
@app.route('/sellers', methods=['GET'])
def get_sellers():
    try:
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM sellers")  # Fetch all sellers
        sellers = cur.fetchall()
        cur.close()
        conn.close()
        
        # Convert the result to a list of dictionaries for better readability
        seller_list = []
        for seller in sellers:
            seller_list.append({
                'seller_id': seller[0],
                'username': seller[1],
                'email': seller[2],
                'phone': seller[4],  # Assuming phone is at index 4
                'address': seller[5],  # Assuming address is at index 5
                'role': seller[6]  # Assuming role is at index 6
            })
        
        return jsonify(seller_list), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch sellers', 'error': str(e)}), 500

# Endpoint to fetch items based on seller_id
@app.route('/items/<seller_id>', methods=['GET'])
def get_items_by_seller(seller_id):
    try:
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM items WHERE seller_id = %s", (seller_id,))  # Fetch items for the given seller_id
        items = cur.fetchall()
        cur.close()
        conn.close()
        
        # Convert the result to a list of dictionaries for better readability
        item_list = []
        for item in items:
            item_list.append({
                'id': item[0],
                'title': item[1],
                'description': item[2],
                'image': item[3],
                'base_price': item[4],
                'seller_id': item[5],
                'end_time': item[6]
            })
        
        return jsonify(item_list), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch items', 'error': str(e)}), 500

# Fetch won bids
@app.route('/won-bids', methods=['GET'])
def get_won_bids():
    try:
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        cur = conn.cursor()
        # Fetch the highest bid for each item where the auction has ended
        cur.execute("""
            SELECT item_id, bidder_id, MAX(bid_amount) AS winning_bid
            FROM bids
            WHERE item_id IN (SELECT id FROM items WHERE end_time < NOW())
            GROUP BY item_id
        """)
        won_bids = cur.fetchall()
        cur.close()
        conn.close()
        
        # Convert the result to a list of dictionaries for better readability
        won_bid_list = []
        for bid in won_bids:
            won_bid_list.append({
                'item_id': bid[0],
                'winner_id': bid[1],
                'winning_bid': bid[2]
            })
        
        return jsonify(won_bid_list), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch won bids', 'error': str(e)}), 500

# Fetch active bids based on item_id
@app.route('/active-bids/<item_id>', methods=['GET'])
def get_active_bids(item_id):
    try:
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM bids WHERE item_id = %s AND timestamp < NOW()", (item_id,))
        active_bids = cur.fetchall()
        cur.close()
        conn.close()
        
        # Convert the result to a list of dictionaries for better readability
        active_bid_list = []
        for bid in active_bids:
            active_bid_list.append({
                'item_id': bid[0],
                'bidder_id': bid[1],
                'bid_amount': bid[2],
                'timestamp': bid[3]
            })
        
        return jsonify(active_bid_list), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch active bids', 'error': str(e)}), 500

# Fetch all active bids
@app.route('/active-bids', methods=['GET'])
def get_all_active_bids():
    try:
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM bids WHERE timestamp < NOW()")  # Fetch all active bids
        active_bids = cur.fetchall()
        cur.close()
        conn.close()
        
        # Convert the result to a list of dictionaries for better readability
        active_bid_list = []
        for bid in active_bids:
            active_bid_list.append({
                'item_id': bid[0],
                'bidder_id': bid[1],
                'bid_amount': bid[2],
                'timestamp': bid[3]
            })
        
        return jsonify(active_bid_list), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch all active bids', 'error': str(e)}), 500

# Endpoint to fetch details of a single item based on item_id
@app.route('/single-item/<item_id>', methods=['GET'])
def get_item_by_id(item_id):
    try:
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        cur = conn.cursor(pymysql.cursors.DictCursor)  # Use DictCursor to return dictionaries
        cur.execute("SELECT * FROM items WHERE id = %s", (item_id,))  # Fetch item for the given item_id
        item = cur.fetchone()  # Fetch a single item
        cur.close()
        conn.close()
        
        if item:
            return jsonify(item), 200  # Return the item details
        else:
            return jsonify({'message': 'Item not found'}), 404  # Item not found
    except Exception as e:
        return jsonify({'message': 'Failed to fetch item', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)