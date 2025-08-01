import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Users, Star, Home, Heart, AlertTriangle, Loader2, ArrowLeft } from 'lucide-react';
import axios from 'axios';

const ResultsPage = () => {
  const { userId } = useParams();
  const [matches, setMatches] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchUserAndMatches();
  }, [userId]);

  const fetchUserAndMatches = async () => {
    try {
      setLoading(true);
      
      // Fetch user data
      const userResponse = await axios.get(`/api/v1/users/${userId}`);
      setUser(userResponse.data);
      
      // Fetch matches (placeholder for now - will be implemented in Stage 4)
      // For now, we'll create mock data
      const mockMatches = [
        {
          user_id: 2,
          name: "Alex Chen",
          age: 23,
          occupation: "Software Engineer",
          compatibility_score: 0.92,
          knn_score: 0.89,
          svd_score: 0.94,
          explanation: "Excellent compatibility! You both share similar sleep schedules, cleanliness preferences, and have complementary hobbies. Alex's love for hiking matches your outdoor interests perfectly.",
          common_interests: ["Hiking", "Reading", "Quiet environments"],
          potential_conflicts: ["Different study schedules"],
          room_recommendation: {
            room_number: "201",
            floor: 2,
            monthly_rent: 900,
            amenities: ["WiFi", "Kitchen", "Bathroom", "Study Desk"]
          }
        },
        {
          user_id: 3,
          name: "Maria Rodriguez",
          age: 21,
          occupation: "Psychology Student",
          compatibility_score: 0.87,
          knn_score: 0.85,
          svd_score: 0.89,
          explanation: "Great match! Maria shares your cleanliness standards and social preferences. Her interest in music complements your guitar playing.",
          common_interests: ["Music", "Clean living", "Moderate socializing"],
          potential_conflicts: ["Different noise tolerance levels"],
          room_recommendation: {
            room_number: "102",
            floor: 1,
            monthly_rent: 850,
            amenities: ["WiFi", "Kitchen", "Bathroom", "Balcony"]
          }
        },
        {
          user_id: 4,
          name: "Jordan Taylor",
          age: 24,
          occupation: "Graduate Student",
          compatibility_score: 0.83,
          knn_score: 0.81,
          svd_score: 0.85,
          explanation: "Good compatibility with Jordan. You share similar academic focus and lifestyle preferences. Jordan's pet-friendly attitude aligns with your preferences.",
          common_interests: ["Academic focus", "Pet-friendly", "Similar budget"],
          potential_conflicts: ["Different sleep schedules"],
          room_recommendation: {
            room_number: "301",
            floor: 3,
            monthly_rent: 1000,
            amenities: ["WiFi", "Kitchen", "Bathroom", "Study Desk", "Air Conditioning"]
          }
        },
        {
          user_id: 5,
          name: "Sam Johnson",
          age: 22,
          occupation: "Business Student",
          compatibility_score: 0.78,
          knn_score: 0.76,
          svd_score: 0.80,
          explanation: "Decent match with Sam. You have some overlapping interests and similar cleanliness standards, though there are some lifestyle differences.",
          common_interests: ["Similar age", "Clean living", "Campus proximity"],
          potential_conflicts: ["Different social preferences", "Budget differences"],
          room_recommendation: {
            room_number: "202",
            floor: 2,
            monthly_rent: 950,
            amenities: ["WiFi", "Kitchen", "Bathroom", "Balcony", "Study Desk"]
          }
        },
        {
          user_id: 6,
          name: "Casey Williams",
          age: 20,
          occupation: "Art Student",
          compatibility_score: 0.72,
          knn_score: 0.70,
          svd_score: 0.74,
          explanation: "Moderate compatibility with Casey. While you share some interests, there are notable differences in lifestyle preferences that may require compromise.",
          common_interests: ["Creative interests", "Similar age group"],
          potential_conflicts: ["Different noise tolerance", "Different cleanliness standards"],
          room_recommendation: {
            room_number: "101",
            floor: 1,
            monthly_rent: 800,
            amenities: ["WiFi", "Kitchen", "Bathroom"]
          }
        }
      ];
      
      setMatches(mockMatches);
      
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to load results. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getCompatibilityColor = (score) => {
    if (score >= 0.9) return 'text-green-600 bg-green-100';
    if (score >= 0.8) return 'text-blue-600 bg-blue-100';
    if (score >= 0.7) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getCompatibilityText = (score) => {
    if (score >= 0.9) return 'Excellent Match';
    if (score >= 0.8) return 'Great Match';
    if (score >= 0.7) return 'Good Match';
    return 'Fair Match';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-600 animate-spin mx-auto mb-4" />
          <p className="text-xl text-gray-600">Finding your perfect roommate...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-600 mx-auto mb-4" />
          <p className="text-xl text-gray-600 mb-4">{error}</p>
          <Link
            to="/survey"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            Try Again
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <Link
            to="/survey"
            className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-6"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Survey
          </Link>
          
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Your Perfect Roommate Matches
          </h1>
          <p className="text-xl text-gray-600 mb-6">
            AI-powered recommendations based on your preferences
          </p>
          
          {user && (
            <div className="bg-white rounded-xl p-6 shadow-lg inline-block">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                Welcome, {user.name}!
              </h2>
              <p className="text-gray-600">
                {user.age} years old • {user.occupation}
              </p>
            </div>
          )}
        </motion.div>

        {/* Matches Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {matches.map((match, index) => (
            <motion.div
              key={match.user_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="match-card p-6"
            >
              {/* Match Header */}
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">{match.name}</h3>
                  <p className="text-gray-600">{match.age} years old • {match.occupation}</p>
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${getCompatibilityColor(match.compatibility_score)}`}>
                  {getCompatibilityText(match.compatibility_score)}
                </div>
              </div>

              {/* Compatibility Score */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Compatibility Score</span>
                  <span className="text-lg font-bold text-blue-600">
                    {Math.round(match.compatibility_score * 100)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <motion.div
                    className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${match.compatibility_score * 100}%` }}
                    transition={{ duration: 1, delay: index * 0.1 }}
                  />
                </div>
              </div>

              {/* Explanation */}
              <div className="mb-4">
                <p className="text-gray-700 text-sm leading-relaxed">
                  {match.explanation}
                </p>
              </div>

              {/* Common Interests */}
              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
                  <Heart className="w-4 h-4 mr-1 text-green-600" />
                  Common Interests
                </h4>
                <div className="flex flex-wrap gap-1">
                  {match.common_interests.map((interest, i) => (
                    <span
                      key={i}
                      className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full"
                    >
                      {interest}
                    </span>
                  ))}
                </div>
              </div>

              {/* Potential Conflicts */}
              {match.potential_conflicts.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
                    <AlertTriangle className="w-4 h-4 mr-1 text-yellow-600" />
                    Potential Conflicts
                  </h4>
                  <div className="flex flex-wrap gap-1">
                    {match.potential_conflicts.map((conflict, i) => (
                      <span
                        key={i}
                        className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full"
                      >
                        {conflict}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Room Recommendation */}
              {match.room_recommendation && (
                <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                  <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
                    <Home className="w-4 h-4 mr-1 text-blue-600" />
                    Recommended Room
                  </h4>
                  <div className="text-sm text-gray-700">
                    <p><strong>Room {match.room_recommendation.room_number}</strong> (Floor {match.room_recommendation.floor})</p>
                    <p className="text-blue-600 font-medium">${match.room_recommendation.monthly_rent}/month</p>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {match.room_recommendation.amenities.map((amenity, i) => (
                        <span
                          key={i}
                          className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                        >
                          {amenity}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-2">
                <button className="flex-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white py-2 px-4 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300 text-sm font-medium">
                  Contact {match.name}
                </button>
                <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all duration-300">
                  <Star className="w-4 h-4" />
                </button>
              </div>
            </motion.div>
          ))}
        </div>

        {/* AI Model Information */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-12 bg-white rounded-xl p-6 shadow-lg"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Users className="w-5 h-5 mr-2 text-blue-600" />
            How Our AI Matching Works
          </h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">K-Nearest Neighbors (KNN)</h4>
              <p className="text-sm text-gray-600">
                Finds users with similar preferences and characteristics based on categorical data.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Singular Value Decomposition (SVD)</h4>
              <p className="text-sm text-gray-600">
                Analyzes user compatibility patterns and preferences using collaborative filtering.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Sentence-BERT Embeddings</h4>
              <p className="text-sm text-gray-600">
                Converts hobbies and interests into numerical vectors for semantic similarity matching.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ResultsPage; 