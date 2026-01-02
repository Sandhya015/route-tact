import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Global connection variables
_client = None
_db = None

# Load environment variables (for Vercel)
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass  # dotenv not available in Vercel, use env vars directly

def get_db():
    """Get database connection (lazy initialization for serverless)"""
    global _client, _db
    
    if _db is not None:
        try:
            # Test connection
            _client.admin.command('ping')
            return _db
        except:
            # Connection lost, reconnect
            _client = None
            _db = None
    
    # Get MongoDB URI from environment
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/rural_services')
    
    if not MONGODB_URI or MONGODB_URI == 'mongodb://localhost:27017/rural_services':
        print("Warning: MONGODB_URI not set, using default (will fail if not local MongoDB)")
    
    try:
        # Create connection
        _client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=5000
        )
        
        # Test connection
        _client.admin.command('ping')
        
        # Get database (extract from URI or use default)
        if 'mongodb+srv://' in MONGODB_URI or 'mongodb://' in MONGODB_URI:
            # Extract database name from URI or use default
            if '/rural_services' in MONGODB_URI:
                db_name = MONGODB_URI.split('/')[-1].split('?')[0]
            else:
                db_name = 'rural_services'
            _db = _client[db_name]
        else:
            _db = _client.get_database()
        
        # Create indexes (only if they don't exist - safe to call multiple times)
        try:
            _db.services.create_index([("location", "2dsphere")], background=True)
            _db.services.create_index([("type", 1)], background=True)
            _db.services.create_index([("providerId", 1)], background=True)
            _db.users.create_index([("email", 1)], unique=True, background=True)
        except Exception as idx_error:
            # Index creation might fail if already exists, that's okay
            print(f"Index creation note: {idx_error}")
        
        print("✅ Connected to MongoDB successfully")
        return _db
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        print(f"   MONGODB_URI: {MONGODB_URI[:50]}...")  # Show first 50 chars
        return None
    except Exception as e:
        print(f"❌ Unexpected error connecting to MongoDB: {e}")
        return None

