"""
Vercel serverless function for searching services
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from flask import Flask, request, jsonify
from flask_cors import CORS
from bson import ObjectId
from utils.db import get_db
from utils.helpers import format_service_response

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET', 'OPTIONS'])
def search_services():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        if not db:
            return jsonify({'message': 'Database connection failed'}), 500
        
        # Get query parameters
        lat = float(request.args.get('lat', 0))
        lng = float(request.args.get('lng', 0))
        radius = float(request.args.get('radius', 10))  # km
        service_type = request.args.get('type', '')
        search_term = request.args.get('search', '').lower()
        
        if not lat or not lng:
            return jsonify({'message': 'Location coordinates are required'}), 400
        
        # Build query
        query = {
            'available': True,
            'location': {
                '$near': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': [lng, lat]  # MongoDB uses [longitude, latitude]
                    },
                    '$maxDistance': radius * 1000  # Convert km to meters
                }
            }
        }
        
        # Add service type filter
        if service_type:
            query['type'] = service_type
        
        # Search services
        services = list(db.services.find(query).limit(50))
        
        # Get provider details and format response
        results = []
        for service in services:
            # Get provider info
            provider = db.users.find_one({'_id': ObjectId(service['providerId'])})
            if not provider:
                continue
            
            # Format service response
            service_data = format_service_response(service, lat, lng)
            service_data['providerName'] = provider.get('name', 'Unknown')
            service_data['phone'] = provider.get('phone', '')
            
            # Filter by search term if provided
            if search_term:
                if (search_term in service_data['providerName'].lower() or
                    search_term in service_data['village'].lower() or
                    search_term in service_data['district'].lower()):
                    results.append(service_data)
            else:
                results.append(service_data)
        
        # Sort by distance
        results.sort(key=lambda x: x.get('distance', float('inf')))
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def handler(request):
    with app.app_context():
        return app.full_dispatch_request()

