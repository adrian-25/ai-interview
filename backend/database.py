"""MongoDB database connection and utilities."""
import motor.motor_asyncio
from config import settings
import logging

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database manager."""
    
    client: motor.motor_asyncio.AsyncIOMotorClient = None
    db = None


db_manager = Database()


async def connect_to_mongo():
    """Connect to MongoDB."""
    try:
        db_manager.client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.mongodb_uri,
            maxPoolSize=10,
            minPoolSize=1,
        )
        db_manager.db = db_manager.client.get_database()
        
        # Test connection
        await db_manager.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection."""
    if db_manager.client:
        db_manager.client.close()
        logger.info("Closed MongoDB connection")


async def create_indexes():
    """Create database indexes for optimal query performance."""
    try:
        # Users collection indexes
        await db_manager.db.users.create_index("email", unique=True)
        
        # Sessions collection indexes
        await db_manager.db.sessions.create_index("user_id")
        await db_manager.db.sessions.create_index("status")
        await db_manager.db.sessions.create_index("started_at")
        await db_manager.db.sessions.create_index([("user_id", 1), ("status", 1)])
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")


def get_database():
    """Get database instance."""
    return db_manager.db
