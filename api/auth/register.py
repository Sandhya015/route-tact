from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_db
from utils.auth import hash_password, generate_token

app = Flask(__name__)
CORS(app)

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        db = get_db()
        if not db:
            return jsonify({'message': 'Database connection failed'}), 500
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password', 'phone', 'village', 'district', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        # Check if user already exists
        if db.users.find_one({'email': data['email']}):
            return jsonify({'message': 'User already exists'}), 400
        
        # Hash password
        hashed_password = hash_password(data['password'])
        
        # Create user document
        user_doc = {
            'name': data['name'],
            'email': data['email'],
            'password': hashed_password,
            'phone': data['phone'],
            'village': data['village'],
            'district': data['district'],
            'role': data['role'],  # 'customer' or 'provider'
            'createdAt': __import__('datetime').datetime.utcnow()
        }
        
        # Insert user
        result = db.users.insert_one(user_doc)
        user_id = result.inserted_id
        
        # Generate token
        token = generate_token(user_id, data['email'], data['role'])
        
        # Return user data (without password)
        user_doc['_id'] = str(user_id)
        del user_doc['password']
        
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': user_doc
        }), 201
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# For Vercel serverless
def handler(request):
    return register()

if __name__ == '__main__':
    app.run(debug=True, port=5000)

