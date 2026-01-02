from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_db
from utils.auth import get_user_from_token

app = Flask(__name__)
CORS(app)

@app.route('/api/users/me', methods=['GET'])
def get_current_user():
    try:
        db = get_db()
        if not db:
            return jsonify({'message': 'Database connection failed'}), 500
        
        # Get user from token
        payload = get_user_from_token(request)
        if not payload:
            return jsonify({'message': 'Unauthorized'}), 401
        
        # Find user
        from bson import ObjectId
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
    return get_current_user()

if __name__ == '__main__':
    app.run(debug=True, port=5000)

