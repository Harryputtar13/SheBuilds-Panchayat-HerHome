from fastapi import APIRouter, HTTPException, Depends
import asyncpg
import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import json

from ..database.db import get_db
from ..services.embedding_service import generate_embedding, preprocess_hobbies_text

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/preprocess-dataset/")
async def preprocess_dataset(db: asyncpg.Connection = Depends(get_db)):
    """
    Preprocess the entire dataset and generate embeddings
    
    This endpoint processes all user data and generates embeddings for:
    - Hobbies and interests
    - Lifestyle preferences
    - Personal characteristics
    """
    try:
        # Fetch all users from database
        users = await db.fetch("""
            SELECT id, name, age, gender, occupation, sleep_schedule, 
                   cleanliness_level, noise_tolerance, social_preference,
                   hobbies, dietary_restrictions, pet_preference, 
                   smoking_preference, budget_range, location_preference
            FROM users
        """)
        
        if not users:
            return {
                "message": "No users found in database",
                "processed_count": 0,
                "status": "completed"
            }
        
        processed_count = 0
        
        for user in users:
            # Create comprehensive text representation for embedding
            user_text = _create_user_text_representation(user)
            
            # Generate embedding
            embedding = await generate_embedding(user_text)
            
            # Update user with embedding
            await db.execute("""
                UPDATE users 
                SET embedding_vector = $1, updated_at = CURRENT_TIMESTAMP
                WHERE id = $2
            """, embedding, user['id'])
            
            processed_count += 1
            logger.info(f"Processed user {user['id']}: {user['name']}")
        
        return {
            "message": f"Successfully processed {processed_count} users",
            "processed_count": processed_count,
            "status": "completed"
        }
        
    except Exception as e:
        logger.error(f"Error preprocessing dataset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/preprocess-user/{user_id}")
async def preprocess_user(user_id: int, db: asyncpg.Connection = Depends(get_db)):
    """
    Preprocess a specific user and generate their embedding
    """
    try:
        # Fetch user data
        user = await db.fetchrow("""
            SELECT id, name, age, gender, occupation, sleep_schedule, 
                   cleanliness_level, noise_tolerance, social_preference,
                   hobbies, dietary_restrictions, pet_preference, 
                   smoking_preference, budget_range, location_preference
            FROM users WHERE id = $1
        """, user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create text representation
        user_text = _create_user_text_representation(user)
        
        # Generate embedding
        embedding = await generate_embedding(user_text)
        
        # Update user
        await db.execute("""
            UPDATE users 
            SET embedding_vector = $1, updated_at = CURRENT_TIMESTAMP
            WHERE id = $2
        """, embedding, user_id)
        
        return {
            "message": f"Successfully processed user {user_id}",
            "user_id": user_id,
            "embedding_dimension": len(embedding),
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error preprocessing user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preprocessing-stats/")
async def get_preprocessing_stats(db: asyncpg.Connection = Depends(get_db)):
    """
    Get statistics about data preprocessing status
    """
    try:
        # Get total users
        total_users = await db.fetchval("SELECT COUNT(*) FROM users")
        
        # Get users with embeddings
        users_with_embeddings = await db.fetchval("""
            SELECT COUNT(*) FROM users WHERE embedding_vector IS NOT NULL
        """)
        
        # Get users without embeddings
        users_without_embeddings = total_users - users_with_embeddings
        
        return {
            "total_users": total_users,
            "users_with_embeddings": users_with_embeddings,
            "users_without_embeddings": users_without_embeddings,
            "completion_percentage": round((users_with_embeddings / total_users * 100) if total_users > 0 else 0, 2)
        }
        
    except Exception as e:
        logger.error(f"Error getting preprocessing stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _create_user_text_representation(user: Dict[str, Any]) -> str:
    """
    Create a comprehensive text representation of user data for embedding generation
    """
    text_parts = []
    
    # Basic information
    if user['name']:
        text_parts.append(f"Name: {user['name']}")
    
    if user['age']:
        text_parts.append(f"Age: {user['age']} years old")
    
    if user['gender']:
        text_parts.append(f"Gender: {user['gender']}")
    
    if user['occupation']:
        text_parts.append(f"Occupation: {user['occupation']}")
    
    # Lifestyle preferences
    if user['sleep_schedule']:
        text_parts.append(f"Sleep schedule: {user['sleep_schedule']}")
    
    if user['cleanliness_level']:
        text_parts.append(f"Cleanliness: {user['cleanliness_level']}")
    
    if user['noise_tolerance']:
        text_parts.append(f"Noise tolerance: {user['noise_tolerance']}")
    
    if user['social_preference']:
        text_parts.append(f"Social preference: {user['social_preference']}")
    
    # Hobbies and interests (most important for matching)
    if user['hobbies']:
        hobbies_text = preprocess_hobbies_text(user['hobbies'])
        text_parts.append(f"Hobbies and interests: {hobbies_text}")
    
    # Dietary preferences
    if user['dietary_restrictions']:
        text_parts.append(f"Dietary restrictions: {user['dietary_restrictions']}")
    
    # Pet preferences
    if user['pet_preference']:
        text_parts.append(f"Pet preference: {user['pet_preference']}")
    
    # Smoking preferences
    if user['smoking_preference']:
        text_parts.append(f"Smoking preference: {user['smoking_preference']}")
    
    # Budget and location
    if user['budget_range']:
        text_parts.append(f"Budget range: {user['budget_range']}")
    
    if user['location_preference']:
        text_parts.append(f"Location preference: {user['location_preference']}")
    
    # Combine all parts
    return " | ".join(text_parts) if text_parts else "No information available" 