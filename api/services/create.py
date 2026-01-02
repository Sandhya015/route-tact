from flask import Flask, request, jsonify
from flask_cors import CORS
from bson import ObjectId
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_db
from utils.auth import get_user_from_token

app = Flask(__name__)
CORS(app)

@app.route('/api/services', methods=['POST'])
def create_service():
    try:
        db = get_db()
        if not db:
            return jsonify({'message': 'Database connection failed'}), 500
        
        # Check authentication
        payload = get_user_from_token(request)
        if not payload:
            return jsonify({'message': 'Unauthorized'}), 401
        
        if payload['role'] != 'provider':
            return jsonify({'message': 'Only providers can create services'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('type'):
            return jsonify({'message': 'Service type is required'}), 400
        
        # Get user location from user document
        user = db.users.find_one({'_id': ObjectId(payload['user_id'])})
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Create service document
        service_doc = {
            'providerId': ObjectId(payload['user_id']),
            'type': data['type'],
            'pricePerHour': data.get('pricePerHour'),
            'pricePerTrip': data.get('pricePerTrip'),
            'description': data.get('description', ''),
            'available': data.get('available', True),
            'village': user['village'],
            'district': user['district'],
            'location': {
                'type': 'Point',
                'coordinates': [0, 0]  # Will be updated when location is provided
            },
            'createdAt': datetime.utcnow()
        }
        
        # If location provided, update it
        if data.get('latitude') and data.get('longitude'):
            service_doc['location']['coordinates'] = [
                float(data['longitude']),
                float(data['latitude'])
            ]
        
        # Insert service
        result = db.services.insert_one(service_doc)
        
        service_doc['_id'] = str(result.inserted_id)
        service_doc['providerId'] = str(service_doc['providerId'])
        
        return jsonify({
            'message': 'Service created successfully',
            'service': service_doc
        }), 201
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def handler(request):
    return create_service()

if __name__ == '__main__':
    app.run(debug=True, port=5000)

