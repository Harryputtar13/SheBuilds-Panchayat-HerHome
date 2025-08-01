from fastapi import APIRouter, HTTPException, Depends
import asyncpg
import logging

from ..database.db import get_db
from ..services.ml_service import ml_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/train-models/")
async def train_models(db: asyncpg.Connection = Depends(get_db)):
    """
    Train all ML models using current user data
    
    This endpoint will:
    1. Fetch all users with embeddings
    2. Train KNN, SVD, and Logistic Regression models
    3. Save models to disk
    4. Return training results
    """
    try:
        logger.info("Starting ML model training via API")
        
        # Train models
        result = await ml_service.train_models(db)
        
        if result["status"] == "insufficient_data":
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient data for training: {result['message']}"
            )
        elif result["status"] == "error":
            raise HTTPException(
                status_code=500, 
                detail=f"Training failed: {result['message']}"
            )
        
        return {
            "message": "ML models trained successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in train_models endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-status/")
async def get_model_status():
    """
    Get the current status of all ML models
    """
    try:
        status = ml_service.get_model_status()
        
        return {
            "models_status": status,
            "message": "Model status retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/load-models/")
async def load_models():
    """
    Load the most recent trained models from disk
    """
    try:
        success = await ml_service.load_models()
        
        if success:
            return {
                "message": "Models loaded successfully",
                "status": "loaded"
            }
        else:
            raise HTTPException(
                status_code=404,
                detail="No trained models found. Please train models first."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/training-requirements/")
async def get_training_requirements(db: asyncpg.Connection = Depends(get_db)):
    """
    Get information about training requirements and current data status
    """
    try:
        # Get user statistics
        total_users = await db.fetchval("SELECT COUNT(*) FROM users")
        users_with_embeddings = await db.fetchval("""
            SELECT COUNT(*) FROM users WHERE embedding_vector IS NOT NULL
        """)
        
        # Check if we have enough data for training
        can_train = users_with_embeddings >= 10
        
        return {
            "training_requirements": {
                "minimum_users": 10,
                "current_users": users_with_embeddings,
                "total_users": total_users,
                "can_train": can_train
            },
            "model_status": ml_service.get_model_status(),
            "message": "Training requirements retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting training requirements: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 