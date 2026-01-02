"""Check database contents"""
import os
from dotenv import load_dotenv
load_dotenv()

from utils.db import get_db
from bson import ObjectId

db = get_db()
if db is not None:
    print('=== USERS ===')
    users = list(db.users.find({}))
    print(f"Total Users: {len(users)}")
    for user in users:
        print(f"  - {user.get('name', 'N/A')} ({user.get('email', 'N/A')}) - {user.get('role', 'N/A')} - {user.get('village', 'N/A')}, {user.get('district', 'N/A')}")
    
    print('\n=== SERVICES ===')
    services = list(db.services.find({}))
    print(f"Total Services: {len(services)}")
    for service in services:
        provider = db.users.find_one({'_id': ObjectId(service['providerId'])})
        provider_name = provider.get('name', 'N/A') if provider else 'N/A'
        print(f"  - {service.get('type', 'N/A')} by {provider_name} - {service.get('village', 'N/A')}, {service.get('district', 'N/A')}")
else:
    print('Database not connected')

