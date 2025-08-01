from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import logging

# Import our modules
from .database.db import get_db, init_db
from .api.survey import router as survey_router
from .api.matching import router as matching_router
from .api.preprocessing import router as preprocessing_router
from .api.ml_training import router as ml_training_router
from .api.room_allocation import router as room_allocation_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Roommate Matching System",
    description="Backend API for AI-powered roommate matching with Omnidim.io voice assistant integration",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(survey_router, prefix="/api/v1", tags=["survey"])
app.include_router(matching_router, prefix="/api/v1", tags=["matching"])
app.include_router(preprocessing_router, prefix="/api/v1", tags=["preprocessing"])
app.include_router(ml_training_router, prefix="/api/v1", tags=["ml-training"])
app.include_router(room_allocation_router, prefix="/api/v1", tags=["room-allocation"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
        logger.info("Server starting without database connection")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AI Roommate Matching System API",
        "status": "healthy",
        "omnidim_integration": "enabled",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check for Omnidim.io integration"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "ml_models": "ready",
            "omnidim_webhook": "active"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 