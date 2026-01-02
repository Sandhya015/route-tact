from math import radians, cos, sin, asin, sqrt

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r

def format_service_response(service, user_lat=None, user_lng=None):
    """Format service document for API response"""
    response = {
        '_id': str(service['_id']),
        'type': service.get('type', ''),
        'providerName': service.get('providerName', ''),
        'phone': service.get('phone', ''),
        'village': service.get('village', ''),
        'district': service.get('district', ''),
        'pricePerHour': service.get('pricePerHour'),
        'pricePerTrip': service.get('pricePerTrip'),
        'description': service.get('description', ''),
        'available': service.get('available', True),
        'createdAt': service.get('createdAt', '').isoformat() if service.get('createdAt') else None
    }
    
    # Calculate distance if user location provided
    if user_lat and user_lng and service.get('location'):
        loc = service['location']
        if 'coordinates' in loc:
            distance = calculate_distance(
                user_lat, user_lng,
                loc['coordinates'][1],  # longitude
                loc['coordinates'][0]   # latitude
            )
            response['distance'] = distance
    
    return response

