"""
Vercel serverless function for auto-suggestions
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
def get_suggestions():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        if db is None:
            return jsonify({'message': 'Database connection failed'}), 500
        
        payload = get_user_from_token(request)
        if not payload:
            return jsonify({'message': 'Unauthorized'}), 401
        
        user = db.users.find_one({'_id': ObjectId(payload['user_id'])})
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        user_village = user.get('village', '')
        user_district = user.get('district', '')
        
        same_location_services = list(db.services.find({
            'available': True,
            'village': user_village,
            'district': user_district
        }).limit(10))
        
        same_district_services = list(db.services.find({
            'available': True,
            'district': user_district,
            'village': {'$ne': user_village}
        }).limit(10))
        
        suggestions = []
        seen_providers = set()
        
        for service in same_location_services:
            provider = db.users.find_one({'_id': ObjectId(service['providerId'])})
            if provider and str(service['providerId']) not in seen_providers:
                seen_providers.add(str(service['providerId']))
                suggestions.append({
                    '_id': str(service['_id']),
                    'type': service.get('type', ''),
                    'providerName': provider.get('name', 'Unknown'),
                    'phone': provider.get('phone', ''),
                    'village': service.get('village', ''),
                    'district': service.get('district', ''),
                    'pricePerHour': service.get('pricePerHour'),
                    'pricePerTrip': service.get('pricePerTrip'),
                    'description': service.get('description', ''),
                    'matchType': 'same_location',
                    'matchText': 'Same Location - ' + user_village
                })
        
        for service in same_district_services:
            provider = db.users.find_one({'_id': ObjectId(service['providerId'])})
            if provider and str(service['providerId']) not in seen_providers:
                seen_providers.add(str(service['providerId']))
                suggestions.append({
                    '_id': str(service['_id']),
                    'type': service.get('type', ''),
                    'providerName': provider.get('name', 'Unknown'),
                    'phone': provider.get('phone', ''),
                    'village': service.get('village', ''),
                    'district': service.get('district', ''),
                    'pricePerHour': service.get('pricePerHour'),
                    'pricePerTrip': service.get('pricePerTrip'),
                    'description': service.get('description', ''),
                    'matchType': 'nearby',
                    'matchText': 'Nearby - ' + service.get('village', '') + ', ' + user_district
                })
        
        return jsonify({
            'suggestions': suggestions,
            'userLocation': {
                'village': user_village,
                'district': user_district
            },
            'total': len(suggestions)
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def handler(request):
    with app.app_context():
        return app.full_dispatch_request()

