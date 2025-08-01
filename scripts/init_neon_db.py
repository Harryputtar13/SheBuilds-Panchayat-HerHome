#!/usr/bin/env python3
"""
Neon Database Initialization Script

This script initializes the Neon PostgreSQL database with the required schema
for the AI Roommate Matching System.
"""

import asyncio
import asyncpg
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Database schema
SCHEMA_SQL = """
-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INTEGER CHECK (age >= 18 AND age <= 100),
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
);

-- Create rooms table
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
);

-- Create room assignments table
CREATE TABLE IF NOT EXISTS room_assignments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    UNIQUE(user_id, room_id)
);

-- Create compatibility scores table
CREATE TABLE IF NOT EXISTS compatibility_scores (
    id SERIAL PRIMARY KEY,
    user1_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    user2_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    knn_score DECIMAL(5,4),
    svd_score DECIMAL(5,4),
    final_score DECIMAL(5,4),
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user1_id, user2_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_embedding ON users USING GIN (embedding_vector);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_rooms_occupied ON rooms(is_occupied);
CREATE INDEX IF NOT EXISTS idx_compatibility_scores ON compatibility_scores(user1_id, user2_id);

-- Insert sample rooms for testing
INSERT INTO rooms (room_number, floor_number, room_type, capacity, monthly_rent, amenities) VALUES
('101', 1, 'shared', 2, 800.00, ARRAY['WiFi', 'Kitchen', 'Bathroom']),
('102', 1, 'shared', 2, 850.00, ARRAY['WiFi', 'Kitchen', 'Bathroom', 'Balcony']),
('201', 2, 'shared', 2, 900.00, ARRAY['WiFi', 'Kitchen', 'Bathroom', 'Study Desk']),
('202', 2, 'shared', 2, 950.00, ARRAY['WiFi', 'Kitchen', 'Bathroom', 'Balcony', 'Study Desk']),
('301', 3, 'shared', 2, 1000.00, ARRAY['WiFi', 'Kitchen', 'Bathroom', 'Study Desk', 'Air Conditioning'])
ON CONFLICT (room_number) DO NOTHING;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
"""

async def init_neon_database():
    """Initialize Neon database with schema"""
    
    # Get database URL from environment
    database_url = os.getenv("NEON_DATABASE_URL") or os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ Error: No database URL found in environment variables")
        print("Please set NEON_DATABASE_URL or DATABASE_URL in your .env file")
        sys.exit(1)
    
    print(f"🔗 Connecting to Neon database...")
    print(f"   URL: {database_url.split('@')[1] if '@' in database_url else 'local'}")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(database_url)
        
        print("✅ Connected to Neon database successfully!")
        
        # Execute schema
        print("📋 Creating database schema...")
        await conn.execute(SCHEMA_SQL)
        
        print("✅ Database schema created successfully!")
        
        # Verify tables
        print("🔍 Verifying tables...")
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """)
        
        print("📊 Created tables:")
        for table in tables:
            print(f"   - {table['table_name']}")
        
        # Check sample data
        room_count = await conn.fetchval("SELECT COUNT(*) FROM rooms")
        print(f"🏠 Sample rooms created: {room_count}")
        
        await conn.close()
        print("🎉 Neon database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

async def test_connection():
    """Test database connection"""
    
    database_url = os.getenv("NEON_DATABASE_URL") or os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ Error: No database URL found")
        return False
    
    try:
        conn = await asyncpg.connect(database_url)
        version = await conn.fetchval("SELECT version()")
        await conn.close()
        
        print("✅ Database connection test successful!")
        print(f"   PostgreSQL version: {version.split(',')[0]}")
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

async def main():
    """Main function"""
    print("🚀 Neon Database Setup for AI Roommate Matching System")
    print("=" * 60)
    
    # Test connection first
    if not await test_connection():
        return
    
    # Initialize database
    await init_neon_database()
    
    print("\n🎯 Next Steps:")
    print("1. Start your application: docker-compose -f docker-compose.neon.yml up")
    print("2. Access the admin dashboard: http://localhost:3000/admin")
    print("3. Add users through the survey interface")
    print("4. Preprocess data and train ML models")

if __name__ == "__main__":
    asyncio.run(main()) 