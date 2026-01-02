from flask import Flask, request, jsonify
from flask_cors import CORS
from bson import ObjectId
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_db
from utils.auth import get_user_from_token

app = Flask(__name__)
CORS(app)

@app.route('/api/services/<service_id>', methods=['PATCH', 'DELETE'])
def update_or_delete_service(service_id):
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
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def handler(request, service_id):
    return update_or_delete_service(service_id)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

