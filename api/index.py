"""
Main Vercel serverless function - handles all API routes
"""
import sys
import os
import json

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
def handler(req):
    """Vercel serverless function handler"""
    from werkzeug.wrappers import Request, Response
    
    # Extract path from request
    if hasattr(req, 'path'):
        path = req.path
    elif isinstance(req, dict):
        path = req.get('path', '/')
    else:
        path = '/'
    
    # Remove /api prefix if present
    if path.startswith('/api'):
        path = path[4:] or '/'
    
    # Build WSGI environ
    method = req.method if hasattr(req, 'method') else req.get('method', 'GET')
    headers = req.headers if hasattr(req, 'headers') else req.get('headers', {})
    
    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'QUERY_STRING': '',
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': None,
        'wsgi.errors': None,
        'wsgi.multithread': False,
        'wsgi.multiprocess': True,
        'wsgi.run_once': False,
    }
    
    # Add headers
    for key, value in headers.items():
        key_upper = key.upper().replace('-', '_')
        if key_upper not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            environ['HTTP_' + key_upper] = value
        else:
            environ[key_upper] = value
    
    # Handle body
    body = None
    if hasattr(req, 'body'):
        body = req.body
    elif isinstance(req, dict) and 'body' in req:
        body = req['body']
    
    if body:
        if isinstance(body, str):
            body = body.encode('utf-8')
        environ['wsgi.input'] = body
        environ['CONTENT_LENGTH'] = str(len(body))
    
    # Process request
    with Request(environ) as werkzeug_req:
        with app.request_context(environ):
            try:
                response = app.full_dispatch_request()
                return {
                    'statusCode': response.status_code,
                    'headers': dict(response.headers),
                    'body': response.get_data(as_text=True)
                }
            except Exception as e:
                import traceback
                error_msg = str(e)
                traceback.print_exc()
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'message': error_msg, 'error': 'Internal server error'})
                }
