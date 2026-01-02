"""
Main Vercel serverless function - handles all API routes
"""
import sys
import os
import json
from io import BytesIO

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Add utils to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS

from utils.db import get_db
from utils.auth import hash_password, verify_password, generate_token, get_user_from_token
from utils.helpers import format_service_response
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)
CORS(app)

# Test route
@app.route('/api/test', methods=['GET'])
def test():
    db = get_db()
    if db is not None:
        return jsonify({'message': 'API is working!', 'db_connected': True}), 200
    return jsonify({'message': 'API is working but DB not connected', 'db_connected': False}), 200

# Auth routes
@app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        if db is None:
            return jsonify({'message': 'Database connection failed'}), 500
        
        data = request.get_json()
        
        required_fields = ['name', 'email', 'password', 'phone', 'village', 'district', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400
        
        if db.users.find_one({'email': data['email']}):
            return jsonify({'message': 'User already exists'}), 400
        
        hashed_password = hash_password(data['password'])
        user_doc = {
            'name': data['name'],
            'email': data['email'],
            'password': hashed_password,
            'phone': data['phone'],
            'village': data['village'],
            'district': data['district'],
            'role': data['role'],
            'createdAt': datetime.utcnow()
        }
        
        result = db.users.insert_one(user_doc)
        token = generate_token(result.inserted_id, data['email'], data['role'])
        
        user_doc['_id'] = str(result.inserted_id)
        del user_doc['password']
        
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': user_doc
        }), 201
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        if db is None:
            return jsonify({'message': 'Database connection failed'}), 500
        
        data = request.get_json()
        if not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Email and password are required'}), 400
        
        user = db.users.find_one({'email': data['email']})
        if not user or not verify_password(data['password'], user['password']):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        token = generate_token(user['_id'], user['email'], user['role'])
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

@app.route('/api/users/me', methods=['GET', 'OPTIONS'])
def get_current_user():
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

# Services routes
@app.route('/api/services/search', methods=['GET', 'OPTIONS'])
def search_services():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        if db is None:
            return jsonify({'message': 'Database connection failed'}), 500
        
        lat = float(request.args.get('lat', 0))
        lng = float(request.args.get('lng', 0))
        radius = float(request.args.get('radius', 10))
        service_type = request.args.get('type', '')
        search_term = request.args.get('search', '').lower()
        
        if not lat or not lng:
            return jsonify({'message': 'Location coordinates are required'}), 400
        
        query = {
            'available': True,
            'location': {
                '$near': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': [lng, lat]
                    },
                    '$maxDistance': radius * 1000
                }
            }
        }
        
        if service_type:
            query['type'] = service_type
        
        services = list(db.services.find(query).limit(50))
        
        results = []
        for service in services:
            provider = db.users.find_one({'_id': ObjectId(service['providerId'])})
            if not provider:
                continue
            
            service_data = format_service_response(service, lat, lng)
            service_data['providerName'] = provider.get('name', 'Unknown')
            service_data['phone'] = provider.get('phone', '')
            
            if search_term:
                if (search_term in service_data['providerName'].lower() or
                    search_term in service_data['village'].lower() or
                    search_term in service_data['district'].lower()):
                    results.append(service_data)
            else:
                results.append(service_data)
        
        results.sort(key=lambda x: x.get('distance', float('inf')))
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/services/suggestions', methods=['GET', 'OPTIONS'])
def get_suggestions():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        if db is None:
            return jsonify({'message': 'Database connection failed'}), 500
        
        user_id = request.args.get('userId')
        if not user_id:
            return jsonify({'message': 'User ID is required'}), 400
        
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        user_village = user.get('village', '')
        user_district = user.get('district', '')
        
        suggestions = []
        
        # Find providers in same village
        if user_village:
            same_village_providers = db.users.find({
                'role': 'provider',
                'village': user_village,
                '_id': {'$ne': ObjectId(user_id)}
            })
            for provider in same_village_providers:
                provider_services = db.services.find({
                    'providerId': provider['_id'],
                    'available': True
                })
                for service in provider_services:
                    service_data = format_service_response(service, 0, 0)
                    service_data['providerName'] = provider.get('name', 'Unknown')
                    service_data['phone'] = provider.get('phone', '')
                    service_data['matchType'] = 'same_location'
                    service_data['matchText'] = f'Same Location - {user_village}'
                    suggestions.append(service_data)
        
        # Find providers in same district
        if user_district:
            same_district_providers = db.users.find({
                'role': 'provider',
                'district': user_district,
                '_id': {'$ne': ObjectId(user_id)}
            })
            for provider in same_district_providers:
                already_suggested = any(s.get('providerId') == str(provider['_id']) for s in suggestions)
                if not already_suggested:
                    provider_services = db.services.find({
                        'providerId': provider['_id'],
                        'available': True
                    })
                    for service in provider_services:
                        service_data = format_service_response(service, 0, 0)
                        service_data['providerName'] = provider.get('name', 'Unknown')
                        service_data['phone'] = provider.get('phone', '')
                        service_data['matchType'] = 'nearby'
                        service_data['matchText'] = f'Nearby - {user_district}'
                        suggestions.append(service_data)
        
        return jsonify(suggestions), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/services', methods=['POST', 'OPTIONS'])
def create_service():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        if db is None:
            return jsonify({'message': 'Database connection failed'}), 500
        
        payload = get_user_from_token(request)
        if not payload:
            return jsonify({'message': 'Unauthorized'}), 401
        
        if payload['role'] != 'provider':
            return jsonify({'message': 'Only providers can create services'}), 403
        
        data = request.get_json()
        if not data.get('type'):
            return jsonify({'message': 'Service type is required'}), 400
        
        user = db.users.find_one({'_id': ObjectId(payload['user_id'])})
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
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
                'coordinates': [0, 0]
            },
            'createdAt': datetime.utcnow()
        }
        
        if data.get('latitude') and data.get('longitude'):
            service_doc['location']['coordinates'] = [
                float(data['longitude']),
                float(data['latitude'])
            ]
        
        result = db.services.insert_one(service_doc)
        service_doc['_id'] = str(result.inserted_id)
        service_doc['providerId'] = str(service_doc['providerId'])
        
        return jsonify({
            'message': 'Service created successfully',
            'service': service_doc
        }), 201
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/services/my-services', methods=['GET', 'OPTIONS'])
def get_my_services():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        if db is None:
            return jsonify({'message': 'Database connection failed'}), 500
        
        payload = get_user_from_token(request)
        if not payload:
            return jsonify({'message': 'Unauthorized'}), 401
        
        services = list(db.services.find({
            'providerId': ObjectId(payload['user_id'])
        }).sort('createdAt', -1))
        
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

@app.route('/api/services/<service_id>', methods=['PATCH', 'DELETE', 'OPTIONS'])
def update_or_delete_service(service_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        if db is None:
            return jsonify({'message': 'Database connection failed'}), 500
        
        payload = get_user_from_token(request)
        if not payload:
            return jsonify({'message': 'Unauthorized'}), 401
        
        service = db.services.find_one({'_id': ObjectId(service_id)})
        if not service:
            return jsonify({'message': 'Service not found'}), 404
        
        if str(service['providerId']) != payload['user_id']:
            return jsonify({'message': 'Unauthorized'}), 403
        
        if request.method == 'PATCH':
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
            db.services.delete_one({'_id': ObjectId(service_id)})
            return jsonify({'message': 'Service deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# Vercel serverless function handler
def handler(request):
    """Vercel serverless function handler - compatible with Vercel Python runtime"""
    # Vercel passes a request object with specific attributes
    # Handle both dict and object formats
    
    # Extract path
    if isinstance(request, dict):
        path = request.get('path', '/')
        method = request.get('method', 'GET')
        headers = request.get('headers', {})
        body = request.get('body', '')
        query = request.get('query', {})
    else:
        path = getattr(request, 'path', '/')
        method = getattr(request, 'method', 'GET')
        headers = getattr(request, 'headers', {})
        body = getattr(request, 'body', '')
        query = getattr(request, 'query', {})
    
    # Build query string
    query_string = '&'.join([f'{k}={v}' for k, v in query.items()]) if query else ''
    
    # Convert body to bytes if it's a string
    if isinstance(body, str):
        body_bytes = body.encode('utf-8')
    else:
        body_bytes = body or b''
    
    # Use Flask's test request context
    with app.test_request_context(
        path=path,
        method=method,
        headers=headers,
        data=body_bytes,
        query_string=query_string
    ):
        try:
            response = app.full_dispatch_request()
            
            # Convert response to Vercel format
            response_headers = dict(response.headers)
            # Ensure CORS headers are included
            if 'Access-Control-Allow-Origin' not in response_headers:
                response_headers['Access-Control-Allow-Origin'] = '*'
            if 'Access-Control-Allow-Methods' not in response_headers:
                response_headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
            if 'Access-Control-Allow-Headers' not in response_headers:
                response_headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            
            return {
                'statusCode': response.status_code,
                'headers': response_headers,
                'body': response.get_data(as_text=True)
            }
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error in handler: {error_trace}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': str(e),
                    'error': 'Internal server error'
                })
            }
