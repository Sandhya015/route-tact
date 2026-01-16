"""
Main Flask app for local development
This is for testing locally. For Vercel, use serverless functions in each folder.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Import utilities
from utils.db import get_db
from utils.auth import hash_password, verify_password, generate_token, get_user_from_token
from utils.helpers import format_service_response
from utils.ai import extract_intent, generate_explanation, generate_summary
from datetime import datetime
from bson import ObjectId

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
    """Get auto-suggested providers based on customer's location"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        if db is None:
            return jsonify({'message': 'Database connection failed'}), 500
        
        payload = get_user_from_token(request)
        if not payload:
            return jsonify({'message': 'Unauthorized'}), 401
        
        # Get current user's location
        user = db.users.find_one({'_id': ObjectId(payload['user_id'])})
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        user_village = user.get('village', '')
        user_district = user.get('district', '')
        
        # Find services in same village/district (exact match - highest priority)
        same_location_services = list(db.services.find({
            'available': True,
            'village': user_village,
            'district': user_district
        }).limit(10))
        
        # Find services in same district but different village (nearby - second priority)
        same_district_services = list(db.services.find({
            'available': True,
            'district': user_district,
            'village': {'$ne': user_village}
        }).limit(10))
        
        # Combine and format results
        suggestions = []
        seen_providers = set()
        
        # Add same location services first (marked as "Same Location")
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
        
        # Add same district services (marked as "Nearby")
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

@app.route('/api/providers/nearby', methods=['GET', 'OPTIONS'])
def get_nearby_providers():
    """Get nearby providers mapped to customer's location"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        if db is None:
            return jsonify({'message': 'Database connection failed'}), 500
        
        payload = get_user_from_token(request)
        if not payload:
            return jsonify({'message': 'Unauthorized'}), 401
        
        # Get current user (customer)
        customer = db.users.find_one({'_id': ObjectId(payload['user_id'])})
        if not customer:
            return jsonify({'message': 'User not found'}), 404
        
        customer_village = customer.get('village', '')
        customer_district = customer.get('district', '')
        service_type = request.args.get('type', '')  # Optional filter by service type
        
        # Build query
        query = {
            'available': True,
            'district': customer_district  # Same district
        }
        
        if service_type:
            query['type'] = service_type
        
        # Get all services in same district
        services = list(db.services.find(query))
        
        # Group by provider and format
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
            
            # Add service to provider
            providers_map[provider_id]['services'].append({
                '_id': str(service['_id']),
                'type': service.get('type', ''),
                'pricePerHour': service.get('pricePerHour'),
                'pricePerTrip': service.get('pricePerTrip'),
                'description': service.get('description', ''),
                'available': service.get('available', True)
            })
        
        # Convert to list and sort (same village first)
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

@app.route('/api/services/ai-search', methods=['POST', 'OPTIONS'])
def ai_search_services():
    """AI-powered natural language service search"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        db = get_db()
        if db is None:
            return jsonify({'message': 'Database connection failed'}), 500
        
        data = request.get_json()
        if not data or not data.get('query'):
            return jsonify({'message': 'Query is required'}), 400
        
        query_text = data.get('query', '').strip()
        lat = float(data.get('location', {}).get('lat', 0))
        lng = float(data.get('location', {}).get('lng', 0))
        radius = float(data.get('radius', 50))  # Default 50km
        
        if not lat or not lng:
            return jsonify({'message': 'Location coordinates are required'}), 400
        
        # Extract intent using AI
        extracted_intent = extract_intent(query_text)
        
        # Build database query based on extracted intent
        db_query = {
            'available': True,
            'location': {
                '$near': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': [lng, lat]
                    },
                    '$maxDistance': radius * 1000  # Convert km to meters
                }
            }
        }
        
        # Add service type filter if extracted
        if extracted_intent.get('serviceType'):
            db_query['type'] = extracted_intent['serviceType']
        
        # Query database
        services = list(db.services.find(db_query).limit(50))
        
        # Format results and add provider info
        results = []
        for service in services:
            provider = db.users.find_one({'_id': ObjectId(service['providerId'])})
            if not provider:
                continue
            
            service_data = format_service_response(service, lat, lng)
            service_data['providerName'] = provider.get('name', 'Unknown')
            service_data['phone'] = provider.get('phone', '')
            
            # Filter by budget if specified
            customer_budget = extracted_intent.get('budget')
            if customer_budget:
                service_price = service_data.get('pricePerHour') or service_data.get('pricePerTrip', 0)
                # Allow ±200 range for budget matching
                if service_price > customer_budget + 200:
                    continue
            
            results.append(service_data)
        
        # Sort by distance
        results.sort(key=lambda x: x.get('distance', float('inf')))
        
        # Generate AI explanations for top results (limit to top 5 for cost efficiency)
        top_results = results[:5]
        for service_data in top_results:
            try:
                explanation = generate_explanation(service_data, extracted_intent)
                service_data['aiExplanation'] = explanation
                # Calculate relevance score (0-1) based on distance and price match
                distance_score = 1.0 / (1.0 + service_data.get('distance', 10))
                price_score = 1.0
                if customer_budget:
                    service_price = service_data.get('pricePerHour') or service_data.get('pricePerTrip', 0)
                    price_diff = abs(service_price - customer_budget)
                    price_score = max(0, 1.0 - (price_diff / customer_budget))
                service_data['relevanceScore'] = round((distance_score * 0.6 + price_score * 0.4), 2)
            except Exception as e:
                print(f"Error generating explanation: {e}")
                service_data['aiExplanation'] = "Good match based on location and availability."
                service_data['relevanceScore'] = 0.5
        
        # Add explanations to remaining results (simple)
        for service_data in results[5:]:
            service_data['aiExplanation'] = "Good match based on location and availability."
            service_data['relevanceScore'] = 0.4
        
        # Re-sort by relevance score
        results.sort(key=lambda x: x.get('relevanceScore', 0), reverse=True)
        
        # Generate summary
        summary = generate_summary(results, extracted_intent)
        
        return jsonify({
            'extractedIntent': extracted_intent,
            'results': results,
            'summary': summary,
            'total': len(results)
        }), 200
        
    except Exception as e:
        print(f"AI search error: {e}")
        return jsonify({'message': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Flask server...")
    print("📝 Make sure you have:")
    print("   1. Created api/.env file")
    print("   2. Added MONGODB_URI to .env")
    print("   3. Tested connection with: python test_connection.py")
    print()
    
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
