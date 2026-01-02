"""
Vercel serverless function to update/delete services
Note: Vercel uses [id].py for dynamic routes
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from flask import Flask, request, jsonify
from flask_cors import CORS
from bson import ObjectId
from utils.db import get_db
from utils.auth import get_user_from_token

app = Flask(__name__)
CORS(app)

def handler(request):
    """Vercel serverless function handler"""
    # Extract service_id from path
    path = request.path
    service_id = path.split('/')[-1]
    
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        if not db:
            return jsonify({'message': 'Database connection failed'}), 500
        
        # Check authentication
        payload = get_user_from_token(request)
        if not payload:
            return jsonify({'message': 'Unauthorized'}), 401
        
        # Find service
        service = db.services.find_one({'_id': ObjectId(service_id)})
        if not service:
            return jsonify({'message': 'Service not found'}), 404
        
        # Check ownership
        if str(service['providerId']) != payload['user_id']:
            return jsonify({'message': 'Unauthorized'}), 403
        
        if request.method == 'PATCH':
            # Update service
            data = request.get_json()
            update_doc = {}
            
            if 'available' in data:
                update_doc['available'] = data['available']
            if 'pricePerHour' in data:
                update_doc['pricePerHour'] = data['pricePerHour']
            if 'pricePerTrip' in data:
                update_doc['pricePerTrip'] = data['pricePerTrip']
            if 'description' in data:
                update_doc['description'] = data['description']
            
            db.services.update_one(
                {'_id': ObjectId(service_id)},
                {'$set': update_doc}
            )
            
            return jsonify({'message': 'Service updated successfully'}), 200
        
        elif request.method == 'DELETE':
            # Delete service
            db.services.delete_one({'_id': ObjectId(service_id)})
            return jsonify({'message': 'Service deleted successfully'}), 200
        
        else:
            return jsonify({'message': 'Method not allowed'}), 405
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

