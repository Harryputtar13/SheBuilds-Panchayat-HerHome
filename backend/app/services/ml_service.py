import asyncio
import logging
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import TruncatedSVD
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class RoommateMatchingML:
    """
    Machine Learning service for roommate matching using multiple algorithms
    """
    
    def __init__(self):
        self.knn_model = None
        self.svd_model = None
        self.logistic_model = None
        self.scaler = StandardScaler()
        self.models_trained = False
        self.model_path = "models/"
        
        # Ensure models directory exists
        os.makedirs(self.model_path, exist_ok=True)
    
    async def train_models(self, db_connection) -> Dict[str, Any]:
        """
        Train all ML models using user data from database
        """
        try:
            logger.info("Starting ML model training...")
            
            # Fetch user data with embeddings
            users_data = await self._fetch_training_data(db_connection)
            
            if len(users_data) < 10:
                logger.warning(f"Insufficient data for training. Found {len(users_data)} users, need at least 10")
                return {
                    "status": "insufficient_data",
                    "message": f"Need at least 10 users, found {len(users_data)}",
                    "users_count": len(users_data)
                }
            
            # Prepare training data
            X, y = await self._prepare_training_data(users_data)
            
            # Train models
            knn_results = await self._train_knn_model(X, y)
            svd_results = await self._train_svd_model(X, y)
            logistic_results = await self._train_logistic_model(X, y)
            
            # Save models
            await self._save_models()
            
            self.models_trained = True
            
            return {
                "status": "success",
                "message": "All models trained successfully",
                "users_count": len(users_data),
                "models": {
                    "knn": knn_results,
                    "svd": svd_results,
                    "logistic": logistic_results
                }
            }
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _fetch_training_data(self, db_connection) -> List[Dict[str, Any]]:
        """
        Fetch user data with embeddings for training
        """
        users = await db_connection.fetch("""
            SELECT id, name, age, gender, occupation, sleep_schedule,
                   cleanliness_level, noise_tolerance, social_preference,
                   hobbies, dietary_restrictions, pet_preference,
                   smoking_preference, budget_range, location_preference,
                   embedding_vector
            FROM users 
            WHERE embedding_vector IS NOT NULL
        """)
        
        return [dict(user) for user in users]
    
    async def _prepare_training_data(self, users_data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data for ML models
        """
        # Extract features
        features = []
        labels = []
        
        for user in users_data:
            # Use embedding vector as primary features
            if user['embedding_vector']:
                embedding = np.array(user['embedding_vector'])
                
                # Add additional numerical features
                additional_features = []
                
                # Age (normalized)
                if user['age']:
                    additional_features.append(user['age'] / 100.0)  # Normalize age
                else:
                    additional_features.append(0.5)  # Default age
                
                # Categorical features (one-hot encoded)
                categorical_features = self._encode_categorical_features(user)
                additional_features.extend(categorical_features)
                
                # Combine embedding with additional features
                combined_features = np.concatenate([embedding, additional_features])
                features.append(combined_features)
                
                # Create compatibility label (simplified for training)
                # In a real scenario, this would be based on actual compatibility data
                compatibility_score = self._calculate_compatibility_score(user)
                labels.append(1 if compatibility_score > 0.7 else 0)
        
        return np.array(features), np.array(labels)
    
    def _encode_categorical_features(self, user: Dict[str, Any]) -> List[float]:
        """
        Encode categorical features as numerical values
        """
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
    
    def _calculate_compatibility_score(self, user: Dict[str, Any]) -> float:
        """
        Calculate a compatibility score for training purposes
        This is a simplified heuristic - in production, this would be based on actual data
        """
        score = 0.5  # Base score
        
        # Adjust based on preferences
        if user.get('cleanliness_level') == 'clean':
            score += 0.1
        if user.get('noise_tolerance') == 'moderate':
            score += 0.1
        if user.get('social_preference') == 'moderate':
            score += 0.1
        
        return min(score, 1.0)
    
    async def _train_knn_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Train K-Nearest Neighbors model
        """
        try:
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train KNN model
            self.knn_model = NearestNeighbors(n_neighbors=5, algorithm='auto', metric='cosine')
            self.knn_model.fit(X_scaled)
            
            return {
                "algorithm": "K-Nearest Neighbors",
                "n_neighbors": 5,
                "metric": "cosine",
                "status": "trained"
            }
            
        except Exception as e:
            logger.error(f"Error training KNN model: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _train_svd_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Train Singular Value Decomposition model for dimensionality reduction
        """
        try:
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train SVD model
            n_components = min(50, X_scaled.shape[1] - 1)  # Reduce to 50 components or less
            self.svd_model = TruncatedSVD(n_components=n_components, random_state=42)
            X_reduced = self.svd_model.fit_transform(X_scaled)
            
            return {
                "algorithm": "Singular Value Decomposition",
                "n_components": n_components,
                "explained_variance_ratio": float(np.sum(self.svd_model.explained_variance_ratio_)),
                "status": "trained"
            }
            
        except Exception as e:
            logger.error(f"Error training SVD model: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _train_logistic_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Train Logistic Regression model for compatibility prediction
        """
        try:
            # Split data for training and validation
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train Logistic Regression model
            self.logistic_model = LogisticRegression(random_state=42, max_iter=1000)
            self.logistic_model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.logistic_model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            return {
                "algorithm": "Logistic Regression",
                "accuracy": round(accuracy, 4),
                "test_samples": len(X_test),
                "status": "trained"
            }
            
        except Exception as e:
            logger.error(f"Error training Logistic Regression model: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _save_models(self):
        """
        Save trained models to disk
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if self.knn_model:
                with open(f"{self.model_path}knn_model_{timestamp}.pkl", 'wb') as f:
                    pickle.dump(self.knn_model, f)
            
            if self.svd_model:
                with open(f"{self.model_path}svd_model_{timestamp}.pkl", 'wb') as f:
                    pickle.dump(self.svd_model, f)
            
            if self.logistic_model:
                with open(f"{self.model_path}logistic_model_{timestamp}.pkl", 'wb') as f:
                    pickle.dump(self.logistic_model, f)
            
            # Save scaler
            with open(f"{self.model_path}scaler_{timestamp}.pkl", 'wb') as f:
                pickle.dump(self.scaler, f)
            
            logger.info("Models saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    async def load_models(self) -> bool:
        """
        Load the most recent trained models from disk
        """
        try:
            # Find the most recent model files
            model_files = [f for f in os.listdir(self.model_path) if f.endswith('.pkl')]
            
            if not model_files:
                logger.warning("No saved models found")
                return False
            
            # Get the most recent timestamp
            timestamps = set()
            for file in model_files:
                if '_' in file:
                    timestamp = file.split('_')[-1].replace('.pkl', '')
                    timestamps.add(timestamp)
            
            if not timestamps:
                return False
            
            latest_timestamp = max(timestamps)
            
            # Load models
            knn_file = f"{self.model_path}knn_model_{latest_timestamp}.pkl"
            svd_file = f"{self.model_path}svd_model_{latest_timestamp}.pkl"
            logistic_file = f"{self.model_path}logistic_model_{latest_timestamp}.pkl"
            scaler_file = f"{self.model_path}scaler_{latest_timestamp}.pkl"
            
            if os.path.exists(knn_file):
                with open(knn_file, 'rb') as f:
                    self.knn_model = pickle.load(f)
            
            if os.path.exists(svd_file):
                with open(svd_file, 'rb') as f:
                    self.svd_model = pickle.load(f)
            
            if os.path.exists(logistic_file):
                with open(logistic_file, 'rb') as f:
                    self.logistic_model = pickle.load(f)
            
            if os.path.exists(scaler_file):
                with open(scaler_file, 'rb') as f:
                    self.scaler = pickle.load(f)
            
            self.models_trained = True
            logger.info("Models loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False
    
    def get_model_status(self) -> Dict[str, Any]:
        """
        Get the current status of all models
        """
        return {
            "models_trained": self.models_trained,
            "knn_model": self.knn_model is not None,
            "svd_model": self.svd_model is not None,
            "logistic_model": self.logistic_model is not None,
            "scaler": self.scaler is not None
        }

# Global ML service instance
ml_service = RoommateMatchingML() 