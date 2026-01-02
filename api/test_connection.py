"""
Test MongoDB connection
Run this to verify your database connection is working
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from utils.db import get_db

def test_connection():
    print("🔍 Testing MongoDB connection...")
    print(f"MONGODB_URI set: {'Yes' if os.getenv('MONGODB_URI') else 'No'}")
    
    db = get_db()
    
    if db is None:
        print("\n❌ Connection FAILED!")
        print("\nTroubleshooting:")
        print("1. Check if MONGODB_URI is set in .env file")
        print("2. Verify MongoDB Atlas connection string is correct")
        print("3. Check if IP is whitelisted in MongoDB Atlas")
        print("4. Verify database user credentials")
        return False
    
    print("\n✅ Connection SUCCESSFUL!")
    
    # Test database operations
    try:
        # Test users collection
        user_count = db.users.count_documents({})
        print(f"   Users collection: {user_count} documents")
        
        # Test services collection
        service_count = db.services.count_documents({})
        print(f"   Services collection: {service_count} documents")
        
        # Test indexes
        indexes = db.services.list_indexes()
        print(f"   Services indexes: {len(list(indexes))} indexes")
        
        print("\n🎉 Database is ready to use!")
        return True
        
    except Exception as e:
        print(f"\n⚠️  Connection works but error testing collections: {e}")
        return False

if __name__ == '__main__':
    test_connection()

