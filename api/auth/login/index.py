"""
Vercel serverless function for user login
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.db import get_db
from utils.auth import verify_password, generate_token

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        if not db:
            return jsonify({'message': 'Database connection failed'}), 500
        
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password are required'}), 400
        
        # Find user
        user = db.users.find_one({'email': data['email']})
        
        if not user:
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Verify password
        if not verify_password(data['password'], user['password']):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Generate token
        token = generate_token(user['_id'], user['email'], user['role'])
        
        # Return user data (without password)
        user_doc = {
            '_id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'phone': user['phone'],
            'village': user['village'],
            'district': user['district'],
            'role': user['role']
        }
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user_doc
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def handler(request):
    with app.app_context():
        return app.full_dispatch_request()

