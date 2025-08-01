from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import asyncpg
import logging
from datetime import datetime
from typing import List

from ..models.schemas import (
    OmnidimSurveySubmission, 
    UserResponse, 
    EmbeddingRequest, 
    EmbeddingResponse
)
from ..database.db import get_db
from ..services.embedding_service import generate_embedding

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/survey-submission/", response_model=UserResponse)
async def submit_survey(
    survey_data: OmnidimSurveySubmission,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Submit survey data from Omnidim.io voice assistant
    
    This endpoint receives structured data from the Omnidim.io voice assistant
    and stores it in the database. It also triggers embedding generation for
    the hobbies field to enable AI-powered matching.
    """
    try:
        logger.info(f"Received survey submission from Omnidim.io session: {survey_data.session_id}")
        
        # Insert user data into database
        query = """
            INSERT INTO users (
                name, age, gender, occupation, sleep_schedule, cleanliness_level,
                noise_tolerance, social_preference, hobbies, dietary_restrictions,
                pet_preference, smoking_preference, budget_range, location_preference
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            RETURNING id, name, age, gender, occupation, sleep_schedule, cleanliness_level,
                      noise_tolerance, social_preference, hobbies, dietary_restrictions,
                      pet_preference, smoking_preference, budget_range, location_preference,
                      created_at, updated_at
        """
        
        user_data = await db.fetchrow(
            query,
            survey_data.name,
            survey_data.age,
            survey_data.gender.value,
            survey_data.occupation,
            survey_data.sleep_schedule.value,
            survey_data.cleanliness_level.value,
            survey_data.noise_tolerance.value,
            survey_data.social_preference.value,
            survey_data.hobbies,
            survey_data.dietary_restrictions,
            survey_data.pet_preference.value,
            survey_data.smoking_preference.value,
            survey_data.budget_range,
            survey_data.location_preference
        )
        
        user_id = user_data['id']
        
        # Generate embedding for hobbies (async task)
        try:
            embedding = await generate_embedding(survey_data.hobbies)
            
            # Update user with embedding
            await db.execute(
                "UPDATE users SET embedding_vector = $1 WHERE id = $2",
                embedding, user_id
            )
            
            logger.info(f"Generated embedding for user {user_id}")
            
        except Exception as e:
            logger.warning(f"Failed to generate embedding for user {user_id}: {e}")
            # Continue without embedding - it can be generated later
        
        # Log Omnidim.io specific data
        if survey_data.voice_data:
            logger.info(f"Voice data received for session {survey_data.session_id}")
        
        if survey_data.confidence_score:
            logger.info(f"Voice confidence score: {survey_data.confidence_score}")
        
        return UserResponse(
            id=user_data['id'],
            name=user_data['name'],
            age=user_data['age'],
            gender=survey_data.gender,
            occupation=user_data['occupation'],
            sleep_schedule=survey_data.sleep_schedule,
            cleanliness_level=survey_data.cleanliness_level,
            noise_tolerance=survey_data.noise_tolerance,
            social_preference=survey_data.social_preference,
            hobbies=user_data['hobbies'],
            dietary_restrictions=user_data['dietary_restrictions'],
            pet_preference=survey_data.pet_preference,
            smoking_preference=survey_data.smoking_preference,
            budget_range=user_data['budget_range'],
            location_preference=user_data['location_preference'],
            created_at=user_data['created_at'],
            updated_at=user_data['updated_at']
        )
        
    except Exception as e:
        logger.error(f"Error processing survey submission: {e}")
        raise HTTPException(status_code=500, detail="Failed to process survey submission")

@router.get("/users/", response_model=List[UserResponse])
async def get_users(db: asyncpg.Connection = Depends(get_db)):
    """Get all users (for testing and admin purposes)"""
    try:
        query = """
            SELECT id, name, age, gender, occupation, sleep_schedule, cleanliness_level,
                   noise_tolerance, social_preference, hobbies, dietary_restrictions,
                   pet_preference, smoking_preference, budget_range, location_preference,
                   created_at, updated_at
            FROM users
            ORDER BY created_at DESC
        """
        
        users = await db.fetch(query)
        
        return [
            UserResponse(
                id=user['id'],
                name=user['name'],
                age=user['age'],
                gender=user['gender'],
                occupation=user['occupation'],
                sleep_schedule=user['sleep_schedule'],
                cleanliness_level=user['cleanliness_level'],
                noise_tolerance=user['noise_tolerance'],
                social_preference=user['social_preference'],
                hobbies=user['hobbies'],
                dietary_restrictions=user['dietary_restrictions'],
                pet_preference=user['pet_preference'],
                smoking_preference=user['smoking_preference'],
                budget_range=user['budget_range'],
                location_preference=user['location_preference'],
                created_at=user['created_at'],
                updated_at=user['updated_at']
            )
            for user in users
        ]
        
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: asyncpg.Connection = Depends(get_db)):
    """Get a specific user by ID"""
    try:
        query = """
            SELECT id, name, age, gender, occupation, sleep_schedule, cleanliness_level,
                   noise_tolerance, social_preference, hobbies, dietary_restrictions,
                   pet_preference, smoking_preference, budget_range, location_preference,
                   created_at, updated_at
            FROM users
            WHERE id = $1
        """
        
        user = await db.fetchrow(query, user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            id=user['id'],
            name=user['name'],
            age=user['age'],
            gender=user['gender'],
            occupation=user['occupation'],
            sleep_schedule=user['sleep_schedule'],
            cleanliness_level=user['cleanliness_level'],
            noise_tolerance=user['noise_tolerance'],
            social_preference=user['social_preference'],
            hobbies=user['hobbies'],
            dietary_restrictions=user['dietary_restrictions'],
            pet_preference=user['pet_preference'],
            smoking_preference=user['smoking_preference'],
            budget_range=user['budget_range'],
            location_preference=user['location_preference'],
            created_at=user['created_at'],
            updated_at=user['updated_at']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user")

@router.post("/generate-embedding/", response_model=EmbeddingResponse)
async def generate_user_embedding(
    request: EmbeddingRequest,
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Generate embedding for a user's hobbies text
    
    This endpoint can be used to generate embeddings for existing users
    or to regenerate embeddings if needed.
    """
    try:
        import time
        start_time = time.time()
        
        # Generate embedding
        embedding = await generate_embedding(request.hobbies_text)
        
        # Update user's embedding in database
        await db.execute(
            "UPDATE users SET embedding_vector = $1, updated_at = $2 WHERE id = $3",
            embedding, datetime.utcnow(), request.user_id
        )
        
        processing_time = time.time() - start_time
        
        return EmbeddingResponse(
            user_id=request.user_id,
            embedding_vector=embedding,
            vector_dimension=len(embedding),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error generating embedding for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate embedding")

@router.get("/omnidim-webhook-status/")
async def get_omnidim_webhook_status():
    """
    Check the status of Omnidim.io webhook integration
    
    This endpoint provides information about the current state
    of the Omnidim.io voice assistant integration.
    """
    return {
        "status": "active",
        "endpoint": "/api/v1/survey-submission/",
        "method": "POST",
        "content_type": "application/json",
        "supported_fields": [
            "session_id", "user_id", "voice_data", "name", "age", "gender",
            "occupation", "sleep_schedule", "cleanliness_level", "noise_tolerance",
            "social_preference", "hobbies", "dietary_restrictions", "pet_preference",
            "smoking_preference", "budget_range", "location_preference",
            "confidence_score", "language", "timestamp"
        ],
        "last_updated": datetime.utcnow().isoformat()
    }

@router.get("/rooms/")
async def get_rooms(db: asyncpg.Connection = Depends(get_db)):
    """Get all rooms (for admin purposes)"""
    try:
        query = """
            SELECT id, room_number, floor_number, room_type, capacity, 
                   monthly_rent, amenities, is_occupied, created_at
            FROM rooms
            ORDER BY room_number
        """
        
        rooms = await db.fetch(query)
        
        return [
            {
                "id": room['id'],
                "room_number": room['room_number'],
                "floor_number": room['floor_number'],
                "room_type": room['room_type'],
                "capacity": room['capacity'],
                "monthly_rent": float(room['monthly_rent']) if room['monthly_rent'] else 0,
                "amenities": room['amenities'],
                "is_occupied": room['is_occupied'],
                "created_at": room['created_at'].isoformat() if room['created_at'] else None
            }
            for room in rooms
        ]
        
    except Exception as e:
        logger.error(f"Error fetching rooms: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch rooms") 