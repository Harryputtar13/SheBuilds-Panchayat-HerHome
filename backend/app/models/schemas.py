from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class SleepSchedule(str, Enum):
    EARLY_BIRD = "early_bird"
    NIGHT_OWL = "night_owl"
    FLEXIBLE = "flexible"
    REGULAR = "regular"

class CleanlinessLevel(str, Enum):
    VERY_CLEAN = "very_clean"
    CLEAN = "clean"
    MODERATE = "moderate"
    RELAXED = "relaxed"

class NoiseTolerance(str, Enum):
    VERY_QUIET = "very_quiet"
    QUIET = "quiet"
    MODERATE = "moderate"
    NOISY = "noisy"

class SocialPreference(str, Enum):
    VERY_SOCIAL = "very_social"
    SOCIAL = "social"
    MODERATE = "moderate"
    INTROVERT = "introvert"

class PetPreference(str, Enum):
    LOVE_PETS = "love_pets"
    OK_WITH_PETS = "ok_with_pets"
    NO_PETS = "no_pets"
    HAVE_PETS = "have_pets"

class SmokingPreference(str, Enum):
    SMOKER = "smoker"
    NON_SMOKER = "non_smoker"
    OK_WITH_SMOKING = "ok_with_smoking"

# Omnidim.io Voice Assistant Integration Models
class OmnidimSurveySubmission(BaseModel):
    """Model for receiving survey data from Omnidim.io voice assistant"""
    session_id: str = Field(..., description="Unique session ID from Omnidim.io")
    user_id: Optional[str] = Field(None, description="User ID if available from Omnidim.io")
    voice_data: Optional[Dict[str, Any]] = Field(None, description="Raw voice processing data")
    
    # Core user information
    name: str = Field(..., description="User's full name")
    age: int = Field(..., ge=18, le=100, description="User's age")
    gender: Gender = Field(..., description="User's gender")
    occupation: str = Field(..., description="User's occupation or field of study")
    
    # Lifestyle preferences
    sleep_schedule: SleepSchedule = Field(..., description="Preferred sleep schedule")
    cleanliness_level: CleanlinessLevel = Field(..., description="Cleanliness preference")
    noise_tolerance: NoiseTolerance = Field(..., description="Noise tolerance level")
    social_preference: SocialPreference = Field(..., description="Social interaction preference")
    
    # Hobbies and interests (natural language from voice)
    hobbies: str = Field(..., description="Hobbies and interests (natural language)")
    
    # Additional preferences
    dietary_restrictions: Optional[str] = Field(None, description="Dietary restrictions or preferences")
    pet_preference: PetPreference = Field(..., description="Pet preferences")
    smoking_preference: SmokingPreference = Field(..., description="Smoking preferences")
    
    # Practical preferences
    budget_range: str = Field(..., description="Monthly budget range for rent")
    location_preference: Optional[str] = Field(None, description="Preferred location or area")
    
    # Omnidim.io specific fields
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Voice recognition confidence")
    language: Optional[str] = Field("en", description="Language used in voice input")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

class UserResponse(BaseModel):
    """Response model for user creation/update"""
    id: int
    name: str
    age: int
    gender: Gender
    occupation: str
    sleep_schedule: SleepSchedule
    cleanliness_level: CleanlinessLevel
    noise_tolerance: NoiseTolerance
    social_preference: SocialPreference
    hobbies: str
    dietary_restrictions: Optional[str]
    pet_preference: PetPreference
    smoking_preference: SmokingPreference
    budget_range: str
    location_preference: Optional[str]
    created_at: datetime
    updated_at: datetime

class MatchingRequest(BaseModel):
    """Request model for roommate matching"""
    user_id: int = Field(..., description="ID of the user seeking a roommate")
    max_results: int = Field(5, ge=1, le=20, description="Maximum number of matches to return")
    include_rooms: bool = Field(False, description="Whether to include room recommendations")

class MatchResult(BaseModel):
    """Model for roommate match results"""
    user_id: int
    name: str
    age: int
    occupation: str
    compatibility_score: float = Field(..., ge=0, le=1)
    knn_score: float = Field(..., ge=0, le=1)
    svd_score: float = Field(..., ge=0, le=1)
    explanation: str
    common_interests: List[str]
    potential_conflicts: List[str]
    room_recommendation: Optional[Dict[str, Any]] = None

class MatchingResponse(BaseModel):
    """Response model for matching results"""
    user_id: int
    matches: List[MatchResult]
    total_matches_found: int
    processing_time: float
    model_versions: Dict[str, str]
    
    class Config:
        protected_namespaces = ()

class EmbeddingRequest(BaseModel):
    """Request model for generating embeddings"""
    user_id: int
    hobbies_text: str

class EmbeddingResponse(BaseModel):
    """Response model for embedding generation"""
    user_id: int
    embedding_vector: List[float]
    vector_dimension: int
    processing_time: float

class HealthCheck(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    services: Dict[str, str]
    omnidim_webhook_status: str 