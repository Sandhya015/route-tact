"""
Vercel serverless function to get current user
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from flask import Flask, request, jsonify
from flask_cors import CORS
from bson import ObjectId
from utils.db import get_db
from utils.auth import get_user_from_token

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET', 'OPTIONS'])
def get_current_user():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        if not db:
            return jsonify({'message': 'Database connection failed'}), 500
        
        # Get user from token
        payload = get_user_from_token(request)
        if not payload:
            return jsonify({'message': 'Unauthorized'}), 401
        
        # Find user
        user = db.users.find_one({'_id': ObjectId(payload['user_id'])})
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
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
        
        return jsonify(user_doc), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def handler(request):
    with app.app_context():
        return app.full_dispatch_request()

