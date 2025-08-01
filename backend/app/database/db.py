import asyncpg
import os
from typing import Optional
from dotenv import load_dotenv
import logging
import ssl

load_dotenv()

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/roommate_matcher")
NEON_DATABASE_URL = os.getenv("NEON_DATABASE_URL", DATABASE_URL)

# Connection pool
pool: Optional[asyncpg.Pool] = None

def get_database_url():
    """Get the appropriate database URL based on environment"""
    # Prefer Neon URL if available
    if NEON_DATABASE_URL and NEON_DATABASE_URL != DATABASE_URL:
        return NEON_DATABASE_URL
    return DATABASE_URL

def create_ssl_context():
    """Create SSL context for Neon DB"""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    return ssl_context

async def get_db():
    """Get database connection from pool"""
    if pool is None:
        raise Exception("Database pool not initialized")
    async with pool.acquire() as connection:
        yield connection

async def init_db():
    """Initialize database connection pool and create tables"""
    global pool
    
    try:
        database_url = get_database_url()
        logger.info(f"Connecting to database: {database_url.split('@')[1] if '@' in database_url else 'local'}")
        
        # Configure connection pool based on database type
        if "neon" in database_url.lower() or "sslmode=require" in database_url:
            # Neon DB configuration
            pool = await asyncpg.create_pool(
                database_url,
                min_size=int(os.getenv("NEON_POOL_SIZE", "5")),
                max_size=int(os.getenv("NEON_MAX_OVERFLOW", "20")),
                command_timeout=60,
                ssl=create_ssl_context(),
                server_settings={
                    'jit': 'off'  # Disable JIT for better performance on serverless
                }
            )
            logger.info("Connected to Neon DB with SSL")
        else:
            # Local PostgreSQL configuration
            pool = await asyncpg.create_pool(
                database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("Connected to local PostgreSQL")
        
        # Create tables
        async with pool.acquire() as conn:
            await create_tables(conn)
            
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def create_tables(conn):
    """Create all necessary tables"""
    
    # Users table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            age INTEGER,
            gender VARCHAR(20),
            occupation VARCHAR(100),
            sleep_schedule VARCHAR(50),
            cleanliness_level VARCHAR(50),
            noise_tolerance VARCHAR(50),
            social_preference VARCHAR(50),
            hobbies TEXT,
            dietary_restrictions TEXT,
            pet_preference VARCHAR(20),
            smoking_preference VARCHAR(20),
            budget_range VARCHAR(50),
            location_preference VARCHAR(100),
            embedding_vector REAL[],
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Rooms table for Stage 6
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id SERIAL PRIMARY KEY,
            room_number VARCHAR(20) UNIQUE NOT NULL,
            floor_number INTEGER,
            room_type VARCHAR(50),
            capacity INTEGER DEFAULT 2,
            is_occupied BOOLEAN DEFAULT FALSE,
            preferences TEXT,
            monthly_rent DECIMAL(10,2),
            amenities TEXT[],
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Room assignments table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS room_assignments (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            room_id INTEGER REFERENCES rooms(id),
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'active',
            UNIQUE(user_id, room_id)
        )
    """)
    
    # Compatibility scores table for ML model results
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS compatibility_scores (
            id SERIAL PRIMARY KEY,
            user1_id INTEGER REFERENCES users(id),
            user2_id INTEGER REFERENCES users(id),
            knn_score DECIMAL(5,4),
            svd_score DECIMAL(5,4),
            final_score DECIMAL(5,4),
            explanation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user1_id, user2_id)
        )
    """)
    
    logger.info("Database tables created successfully")

async def close_db():
    """Close database connection pool"""
    global pool
    if pool:
        await pool.close()
        logger.info("Database pool closed") 