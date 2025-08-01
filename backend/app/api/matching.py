from fastapi import APIRouter, HTTPException, Depends
import asyncpg
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..database.db import get_db
from ..services.ml_service import ml_service
from ..services.embedding_service import generate_embedding, calculate_similarity

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/match/{user_id}")
async def get_matches(user_id: int, limit: int = 5, db: asyncpg.Connection = Depends(get_db)):
    """
    Get roommate matches for a user using ML models
    
    This endpoint uses:
    - KNN for finding similar users
    - SVD for dimensionality reduction
    - Logistic Regression for compatibility prediction
    - Embedding similarity for fine-tuning
    """
    try:
        # Check if user exists and has embedding
        user = await db.fetchrow("""
            SELECT id, name, age, gender, occupation, sleep_schedule,
                   cleanliness_level, noise_tolerance, social_preference,
                   hobbies, dietary_restrictions, pet_preference,
                   smoking_preference, budget_range, location_preference,
                   embedding_vector
            FROM users WHERE id = $1
        """, user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user['embedding_vector']:
            raise HTTPException(
                status_code=400, 
                detail="User has no embedding. Please preprocess user data first."
            )
        
        # Check if ML models are trained
        model_status = ml_service.get_model_status()
        if not model_status["models_trained"]:
            # Try to load models
            await ml_service.load_models()
            model_status = ml_service.get_model_status()
            
            if not model_status["models_trained"]:
                raise HTTPException(
                    status_code=503,
                    detail="ML models not available. Please train models first."
                )
        
        # Get matches using different algorithms
        matches = await _get_comprehensive_matches(user, limit, db)
        
        return {
            "user_id": user_id,
            "user_name": user['name'],
            "matches": matches,
            "total_matches": len(matches),
            "algorithms_used": ["knn", "svd", "logistic_regression", "embedding_similarity"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting matches for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/match/{user_id}/simple")
async def get_simple_matches(user_id: int, limit: int = 5, db: asyncpg.Connection = Depends(get_db)):
    """
    Get simple matches using only embedding similarity (fallback method)
    """
    try:
        # Get user data
        user = await db.fetchrow("""
            SELECT id, name, age, gender, hobbies, embedding_vector
            FROM users WHERE id = $1
        """, user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user['embedding_vector']:
            raise HTTPException(
                status_code=400, 
                detail="User has no embedding. Please preprocess user data first."
            )
        
        # Get all other users with embeddings
        other_users = await db.fetch("""
            SELECT id, name, age, gender, hobbies, embedding_vector
            FROM users 
            WHERE id != $1 AND embedding_vector IS NOT NULL
        """, user_id)
        
        if not other_users:
            return {
                "user_id": user_id,
                "matches": [],
                "message": "No other users found with embeddings"
            }
        
        # Calculate similarities
        similarities = []
        user_embedding = np.array(user['embedding_vector'])
        
        for other_user in other_users:
            other_embedding = np.array(other_user['embedding_vector'])
            similarity = await calculate_similarity(user_embedding, other_embedding)
            
            similarities.append({
                "user_id": other_user['id'],
                "name": other_user['name'],
                "age": other_user['age'],
                "gender": other_user['gender'],
                "hobbies": other_user['hobbies'],
                "similarity_score": round(similarity, 4),
                "algorithm": "embedding_similarity"
            })
        
        # Sort by similarity and return top matches
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        top_matches = similarities[:limit]
        
        return {
            "user_id": user_id,
            "user_name": user['name'],
            "matches": top_matches,
            "total_matches": len(top_matches),
            "algorithm": "embedding_similarity"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting simple matches for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate-compatibility/{user1_id}/{user2_id}")
async def calculate_compatibility(
    user1_id: int, 
    user2_id: int, 
    db: asyncpg.Connection = Depends(get_db)
):
    """
    Calculate detailed compatibility score between two users
    """
    try:
        # Get both users
        user1 = await db.fetchrow("""
            SELECT id, name, age, gender, occupation, sleep_schedule,
                   cleanliness_level, noise_tolerance, social_preference,
                   hobbies, dietary_restrictions, pet_preference,
                   smoking_preference, budget_range, location_preference,
                   embedding_vector
            FROM users WHERE id = $1
        """, user1_id)
        
        user2 = await db.fetchrow("""
            SELECT id, name, age, gender, occupation, sleep_schedule,
                   cleanliness_level, noise_tolerance, social_preference,
                   hobbies, dietary_restrictions, pet_preference,
                   smoking_preference, budget_range, location_preference,
                   embedding_vector
            FROM users WHERE id = $2
        """, user2_id)
        
        if not user1 or not user2:
            raise HTTPException(status_code=404, detail="One or both users not found")
        
        # Calculate compatibility scores
        compatibility_scores = await _calculate_detailed_compatibility(user1, user2)
        
        # Store compatibility score in database
        await _store_compatibility_score(user1_id, user2_id, compatibility_scores, db)
        
        return {
            "user1": {"id": user1_id, "name": user1['name']},
            "user2": {"id": user2_id, "name": user2['name']},
            "compatibility_scores": compatibility_scores,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating compatibility between {user1_id} and {user2_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _get_comprehensive_matches(user: Dict[str, Any], limit: int, db: asyncpg.Connection) -> List[Dict[str, Any]]:
    """
    Get comprehensive matches using multiple ML algorithms
    """
    matches = []
    
    try:
        # Get all other users with embeddings
        other_users = await db.fetch("""
            SELECT id, name, age, gender, occupation, sleep_schedule,
                   cleanliness_level, noise_tolerance, social_preference,
                   hobbies, dietary_restrictions, pet_preference,
                   smoking_preference, budget_range, location_preference,
                   embedding_vector
            FROM users 
            WHERE id != $1 AND embedding_vector IS NOT NULL
        """, user['id'])
        
        if not other_users:
            return []
        
        # Calculate scores for each potential match
        for other_user in other_users:
            match_score = await _calculate_match_score(user, other_user)
            
            matches.append({
                "user_id": other_user['id'],
                "name": other_user['name'],
                "age": other_user['age'],
                "gender": other_user['gender'],
                "occupation": other_user['occupation'],
                "hobbies": other_user['hobbies'],
                "sleep_schedule": other_user['sleep_schedule'],
                "cleanliness_level": other_user['cleanliness_level'],
                "noise_tolerance": other_user['noise_tolerance'],
                "social_preference": other_user['social_preference'],
                "dietary_restrictions": other_user['dietary_restrictions'],
                "pet_preference": other_user['pet_preference'],
                "smoking_preference": other_user['smoking_preference'],
                "budget_range": other_user['budget_range'],
                "location_preference": other_user['location_preference'],
                "scores": match_score,
                "final_score": match_score['final_score']
            })
        
        # Sort by final score and return top matches
        matches.sort(key=lambda x: x['final_score'], reverse=True)
        return matches[:limit]
        
    except Exception as e:
        logger.error(f"Error in comprehensive matching: {e}")
        return []

async def _get_similarity_matches(user: Dict[str, Any], limit: int, db: asyncpg.Connection) -> List[Dict[str, Any]]:
    """
    Get matches using only embedding similarity (fallback method)
    """
    try:
        # Get all other users with embeddings
        other_users = await db.fetch("""
            SELECT id, name, age, gender, hobbies, embedding_vector
            FROM users 
            WHERE id != $1 AND embedding_vector IS NOT NULL
        """, user['id'])
        
        if not other_users:
            return []
        
        # Calculate similarities
        similarities = []
        user_embedding = np.array(user['embedding_vector'])
        
        for other_user in other_users:
            other_embedding = np.array(other_user['embedding_vector'])
            similarity = await calculate_similarity(user_embedding, other_embedding)
            
            similarities.append({
                "user_id": other_user['id'],
                "name": other_user['name'],
                "age": other_user['age'],
                "gender": other_user['gender'],
                "hobbies": other_user['hobbies'],
                "similarity_score": round(similarity, 4),
                "algorithm": "embedding_similarity"
            })
        
        # Sort by similarity and return top matches
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similarities[:limit]
        
    except Exception as e:
        logger.error(f"Error in similarity matching: {e}")
        return []

async def _calculate_match_score(user1: Dict[str, Any], user2: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate match score using multiple algorithms
    """
    scores = {}
    
    try:
        # 1. Embedding similarity score
        if user1['embedding_vector'] and user2['embedding_vector']:
            embedding_sim = await calculate_similarity(
                user1['embedding_vector'], 
                user2['embedding_vector']
            )
            scores['embedding_similarity'] = round(embedding_sim, 4)
        else:
            scores['embedding_similarity'] = 0.0
        
        # 2. KNN score (if model available)
        if ml_service.knn_model:
            knn_score = await _calculate_knn_score(user1, user2)
            scores['knn_score'] = round(knn_score, 4)
        else:
            scores['knn_score'] = 0.0
        
        # 3. SVD score (if model available)
        if ml_service.svd_model:
            svd_score = await _calculate_svd_score(user1, user2)
            scores['svd_score'] = round(svd_score, 4)
        else:
            scores['svd_score'] = 0.0
        
        # 4. Logistic Regression score (if model available)
        if ml_service.logistic_model:
            logistic_score = await _calculate_logistic_score(user1, user2)
            scores['logistic_score'] = round(logistic_score, 4)
        else:
            scores['logistic_score'] = 0.0
        
        # 5. Rule-based compatibility score
        rule_score = _calculate_rule_based_score(user1, user2)
        scores['rule_based_score'] = round(rule_score, 4)
        
        # Calculate final weighted score
        final_score = _calculate_final_score(scores)
        scores['final_score'] = round(final_score, 4)
        
        return scores
        
    except Exception as e:
        logger.error(f"Error calculating match score: {e}")
        return {
            'embedding_similarity': 0.0,
            'knn_score': 0.0,
            'svd_score': 0.0,
            'logistic_score': 0.0,
            'rule_based_score': 0.0,
            'final_score': 0.0
        }

async def _calculate_knn_score(user1: Dict[str, Any], user2: Dict[str, Any]) -> float:
    """
    Calculate KNN-based similarity score
    """
    try:
        # Create feature vector for user1
        user1_features = _create_feature_vector(user1)
        user2_features = _create_feature_vector(user2)
        
        # Scale features
        user1_scaled = ml_service.scaler.transform([user1_features])
        user2_scaled = ml_service.scaler.transform([user2_features])
        
        # Calculate distance using KNN model
        distances, indices = ml_service.knn_model.kneighbors(user1_scaled)
        
        # Check if user2 is in the nearest neighbors
        if user2['id'] in indices[0]:
            # Return inverse of distance (closer = higher score)
            distance_idx = list(indices[0]).index(user2['id'])
            distance = distances[0][distance_idx]
            return max(0, 1 - distance)
        else:
            return 0.0
            
    except Exception as e:
        logger.error(f"Error calculating KNN score: {e}")
        return 0.0

async def _calculate_svd_score(user1: Dict[str, Any], user2: Dict[str, Any]) -> float:
    """
    Calculate SVD-based similarity score
    """
    try:
        # Create feature vectors
        user1_features = _create_feature_vector(user1)
        user2_features = _create_feature_vector(user2)
        
        # Scale features
        user1_scaled = ml_service.scaler.transform([user1_features])
        user2_scaled = ml_service.scaler.transform([user2_features])
        
        # Transform using SVD
        user1_reduced = ml_service.svd_model.transform(user1_scaled)
        user2_reduced = ml_service.svd_model.transform(user2_scaled)
        
        # Calculate cosine similarity in reduced space
        similarity = np.dot(user1_reduced[0], user2_reduced[0]) / (
            np.linalg.norm(user1_reduced[0]) * np.linalg.norm(user2_reduced[0])
        )
        
        return max(0, similarity)
        
    except Exception as e:
        logger.error(f"Error calculating SVD score: {e}")
        return 0.0

async def _calculate_logistic_score(user1: Dict[str, Any], user2: Dict[str, Any]) -> float:
    """
    Calculate Logistic Regression compatibility score
    """
    try:
        # Create combined feature vector
        combined_features = _create_combined_feature_vector(user1, user2)
        
        # Scale features
        combined_scaled = ml_service.scaler.transform([combined_features])
        
        # Get probability from logistic regression
        probability = ml_service.logistic_model.predict_proba(combined_scaled)[0][1]
        
        return probability
        
    except Exception as e:
        logger.error(f"Error calculating logistic score: {e}")
        return 0.0

def _calculate_rule_based_score(user1: Dict[str, Any], user2: Dict[str, Any]) -> float:
    """
    Calculate rule-based compatibility score
    """
    score = 0.5  # Base score
    
    # Sleep schedule compatibility
    if user1['sleep_schedule'] == user2['sleep_schedule']:
        score += 0.1
    elif user1['sleep_schedule'] == 'flexible' or user2['sleep_schedule'] == 'flexible':
        score += 0.05
    
    # Cleanliness compatibility
    if user1['cleanliness_level'] == user2['cleanliness_level']:
        score += 0.1
    elif abs(_cleanliness_to_number(user1['cleanliness_level']) - 
             _cleanliness_to_number(user2['cleanliness_level'])) <= 1:
        score += 0.05
    
    # Noise tolerance compatibility
    if user1['noise_tolerance'] == user2['noise_tolerance']:
        score += 0.1
    elif abs(_noise_to_number(user1['noise_tolerance']) - 
             _noise_to_number(user2['noise_tolerance'])) <= 1:
        score += 0.05
    
    # Social preference compatibility
    if user1['social_preference'] == user2['social_preference']:
        score += 0.1
    elif abs(_social_to_number(user1['social_preference']) - 
             _social_to_number(user2['social_preference'])) <= 1:
        score += 0.05
    
    # Pet preference compatibility
    if user1['pet_preference'] == user2['pet_preference']:
        score += 0.1
    
    # Smoking preference compatibility
    if user1['smoking_preference'] == user2['smoking_preference']:
        score += 0.1
    
    return min(score, 1.0)

def _cleanliness_to_number(level: str) -> int:
    """Convert cleanliness level to number"""
    mapping = {
        'very_clean': 4,
        'clean': 3,
        'moderate': 2,
        'relaxed': 1,
        'very_relaxed': 0
    }
    return mapping.get(level, 2)

def _noise_to_number(level: str) -> int:
    """Convert noise tolerance to number"""
    mapping = {
        'very_quiet': 0,
        'quiet': 1,
        'moderate': 2,
        'tolerant': 3,
        'very_tolerant': 4
    }
    return mapping.get(level, 2)

def _social_to_number(level: str) -> int:
    """Convert social preference to number"""
    mapping = {
        'very_private': 0,
        'private': 1,
        'moderate': 2,
        'social': 3,
        'very_social': 4
    }
    return mapping.get(level, 2)

def _create_feature_vector(user: Dict[str, Any]) -> np.ndarray:
    """Create feature vector for ML models"""
    features = []
    
    # Embedding vector
    if user['embedding_vector']:
        features.extend(user['embedding_vector'])
    else:
        features.extend([0.0] * 384)  # Default embedding size
    
    # Additional features
    if user['age']:
        features.append(user['age'] / 100.0)
    else:
        features.append(0.5)
    
    # Categorical features
    features.extend(_encode_categorical_features(user))
    
    return np.array(features)

def _create_combined_feature_vector(user1: Dict[str, Any], user2: Dict[str, Any]) -> np.ndarray:
    """Create combined feature vector for compatibility prediction"""
    # Combine features from both users
    user1_features = _create_feature_vector(user1)
    user2_features = _create_feature_vector(user2)
    
    # Concatenate and add interaction features
    combined = np.concatenate([user1_features, user2_features])
    
    # Add interaction features (differences)
    differences = np.abs(user1_features - user2_features)
    combined = np.concatenate([combined, differences])
    
    return combined

def _encode_categorical_features(user: Dict[str, Any]) -> List[float]:
    """Encode categorical features as numerical values"""
    features = []
    
    # Sleep schedule encoding
    sleep_encoding = {
        'early_bird': 0.0,
        'night_owl': 1.0,
        'flexible': 0.5
    }
    features.append(sleep_encoding.get(user.get('sleep_schedule', 'flexible'), 0.5))
    
    # Cleanliness level encoding
    cleanliness_encoding = {
        'very_clean': 1.0,
        'clean': 0.75,
        'moderate': 0.5,
        'relaxed': 0.25,
        'very_relaxed': 0.0
    }
    features.append(cleanliness_encoding.get(user.get('cleanliness_level', 'moderate'), 0.5))
    
    # Noise tolerance encoding
    noise_encoding = {
        'very_quiet': 0.0,
        'quiet': 0.25,
        'moderate': 0.5,
        'tolerant': 0.75,
        'very_tolerant': 1.0
    }
    features.append(noise_encoding.get(user.get('noise_tolerance', 'moderate'), 0.5))
    
    # Social preference encoding
    social_encoding = {
        'very_social': 1.0,
        'social': 0.75,
        'moderate': 0.5,
        'private': 0.25,
        'very_private': 0.0
    }
    features.append(social_encoding.get(user.get('social_preference', 'moderate'), 0.5))
    
    return features

def _calculate_final_score(scores: Dict[str, float]) -> float:
    """Calculate final weighted score"""
    weights = {
        'embedding_similarity': 0.3,
        'knn_score': 0.2,
        'svd_score': 0.15,
        'logistic_score': 0.2,
        'rule_based_score': 0.15
    }
    
    final_score = 0.0
    total_weight = 0.0
    
    for score_name, weight in weights.items():
        if score_name in scores:
            final_score += scores[score_name] * weight
            total_weight += weight
    
    return final_score / total_weight if total_weight > 0 else 0.0

async def _calculate_detailed_compatibility(user1: Dict[str, Any], user2: Dict[str, Any]) -> Dict[str, float]:
    """Calculate detailed compatibility scores"""
    return await _calculate_match_score(user1, user2)

async def _store_compatibility_score(user1_id: int, user2_id: int, scores: Dict[str, float], db: asyncpg.Connection):
    """Store compatibility score in database"""
    try:
        await db.execute("""
            INSERT INTO compatibility_scores (user1_id, user2_id, knn_score, svd_score, final_score, explanation)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (user1_id, user2_id) 
            DO UPDATE SET 
                knn_score = $3,
                svd_score = $4,
                final_score = $5,
                explanation = $6,
                created_at = CURRENT_TIMESTAMP
        """, user1_id, user2_id, scores.get('knn_score', 0.0), 
             scores.get('svd_score', 0.0), scores.get('final_score', 0.0),
             f"ML-based compatibility score: {scores}")
    except Exception as e:
        logger.error(f"Error storing compatibility score: {e}") 