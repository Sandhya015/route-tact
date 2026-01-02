"""
Vercel serverless function for nearby providers
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
def get_nearby_providers():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        if db is None:
            return jsonify({'message': 'Database connection failed'}), 500
        
        payload = get_user_from_token(request)
        if not payload:
            return jsonify({'message': 'Unauthorized'}), 401
        
        customer = db.users.find_one({'_id': ObjectId(payload['user_id'])})
        if not customer:
            return jsonify({'message': 'User not found'}), 404
        
        customer_village = customer.get('village', '')
        customer_district = customer.get('district', '')
        service_type = request.args.get('type', '')
        
        query = {
            'available': True,
            'district': customer_district
        }
        
        if service_type:
            query['type'] = service_type
        
        services = list(db.services.find(query))
        
        providers_map = {}
        for service in services:
            provider_id = str(service['providerId'])
            
            if provider_id not in providers_map:
                provider = db.users.find_one({'_id': ObjectId(service['providerId'])})
                if provider:
                    providers_map[provider_id] = {
                        'providerId': provider_id,
                        'providerName': provider.get('name', 'Unknown'),
                        'phone': provider.get('phone', ''),
                        'email': provider.get('email', ''),
                        'village': provider.get('village', ''),
                        'district': provider.get('district', ''),
                        'isSameVillage': provider.get('village', '') == customer_village,
                        'services': []
                    }
            
            providers_map[provider_id]['services'].append({
                '_id': str(service['_id']),
                'type': service.get('type', ''),
                'pricePerHour': service.get('pricePerHour'),
                'pricePerTrip': service.get('pricePerTrip'),
                'description': service.get('description', ''),
                'available': service.get('available', True)
            })
        
        providers_list = list(providers_map.values())
        providers_list.sort(key=lambda x: (not x['isSameVillage'], x['providerName']))
        
        return jsonify({
            'providers': providers_list,
            'customerLocation': {
                'village': customer_village,
                'district': customer_district
            },
            'total': len(providers_list)
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def handler(request):
    with app.app_context():
        return app.full_dispatch_request()

