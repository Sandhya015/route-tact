from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_db
from utils.auth import verify_password, generate_token

app = Flask(__name__)
CORS(app)

@app.route('/api/auth/login', methods=['POST'])
def login():
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
    return login()

if __name__ == '__main__':
    app.run(debug=True, port=5000)

