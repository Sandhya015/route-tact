"""
Vercel serverless function to get provider's services
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
def get_my_services():
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
        
        # Get services for this provider
        services = list(db.services.find({
            'providerId': ObjectId(payload['user_id'])
        }).sort('createdAt', -1))
        
        # Format response
        results = []
        for service in services:
            service_doc = {
                '_id': str(service['_id']),
                'type': service.get('type', ''),
                'pricePerHour': service.get('pricePerHour'),
                'pricePerTrip': service.get('pricePerTrip'),
                'description': service.get('description', ''),
                'available': service.get('available', True),
                'village': service.get('village', ''),
                'district': service.get('district', ''),
                'createdAt': service.get('createdAt', '').isoformat() if service.get('createdAt') else None
            }
            results.append(service_doc)
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def handler(request):
    with app.app_context():
        return app.full_dispatch_request()

