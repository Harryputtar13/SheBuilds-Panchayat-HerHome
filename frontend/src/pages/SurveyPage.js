import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mic, MicOff, Send, Loader2, CheckCircle } from 'lucide-react';
import axios from 'axios';

const SurveyPage = () => {
  const navigate = useNavigate();
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [surveyData, setSurveyData] = useState({});
  const [voiceTranscript, setVoiceTranscript] = useState('');

  const surveySteps = [
    {
      id: 'name',
      question: "What's your full name?",
      type: 'text',
      field: 'name'
    },
    {
      id: 'age',
      question: "How old are you?",
      type: 'number',
      field: 'age'
    },
    {
      id: 'gender',
      question: "What's your gender?",
      type: 'select',
      options: ['male', 'female', 'other', 'prefer_not_to_say'],
      field: 'gender'
    },
    {
      id: 'occupation',
      question: "What do you do? (student, job, etc.)",
      type: 'text',
      field: 'occupation'
    },
    {
      id: 'sleep_schedule',
      question: "What's your sleep schedule?",
      type: 'select',
      options: ['early_bird', 'night_owl', 'flexible', 'regular'],
      field: 'sleep_schedule'
    },
    {
      id: 'cleanliness_level',
      question: "How would you describe your cleanliness level?",
      type: 'select',
      options: ['very_clean', 'clean', 'moderate', 'relaxed'],
      field: 'cleanliness_level'
    },
    {
      id: 'noise_tolerance',
      question: "What's your noise tolerance?",
      type: 'select',
      options: ['very_quiet', 'quiet', 'moderate', 'noisy'],
      field: 'noise_tolerance'
    },
    {
      id: 'social_preference',
      question: "How social are you?",
      type: 'select',
      options: ['very_social', 'social', 'moderate', 'introvert'],
      field: 'social_preference'
    },
    {
      id: 'hobbies',
      question: "What are your hobbies and interests?",
      type: 'text',
      field: 'hobbies'
    },
    {
      id: 'dietary_restrictions',
      question: "Any dietary restrictions?",
      type: 'text',
      field: 'dietary_restrictions'
    },
    {
      id: 'pet_preference',
      question: "What's your pet preference?",
      type: 'select',
      options: ['love_pets', 'ok_with_pets', 'no_pets', 'have_pets'],
      field: 'pet_preference'
    },
    {
      id: 'smoking_preference',
      question: "What's your smoking preference?",
      type: 'select',
      options: ['smoker', 'non_smoker', 'ok_with_smoking'],
      field: 'smoking_preference'
    },
    {
      id: 'budget_range',
      question: "What's your monthly budget for rent?",
      type: 'text',
      field: 'budget_range'
    },
    {
      id: 'location_preference',
      question: "Any location preferences?",
      type: 'text',
      field: 'location_preference'
    }
  ];

  const startVoiceRecording = () => {
    setIsRecording(true);
    setVoiceTranscript('');
    
    // Simulate voice recording and transcription
    setTimeout(() => {
      const mockTranscripts = [
        "My name is Sarah Johnson",
        "I'm 22 years old",
        "I'm female",
        "I'm a computer science student",
        "I'm a night owl",
        "I'm very clean",
        "I prefer quiet environments",
        "I'm moderately social",
        "I love reading, hiking, and playing guitar",
        "I'm vegetarian",
        "I love pets",
        "I'm a non-smoker",
        "My budget is around $800 per month",
        "I prefer to be near campus"
      ];
      
      if (currentStep < mockTranscripts.length) {
        setVoiceTranscript(mockTranscripts[currentStep]);
      }
    }, 2000);
  };

  const stopVoiceRecording = () => {
    setIsRecording(false);
    // Process the voice transcript
    if (voiceTranscript) {
      processVoiceInput(voiceTranscript);
    }
  };

  const processVoiceInput = (transcript) => {
    const currentStepData = surveySteps[currentStep];
    let value = transcript;

    // Simple processing logic (in real implementation, this would use NLP)
    if (currentStepData.type === 'number') {
      const numbers = transcript.match(/\d+/);
      value = numbers ? parseInt(numbers[0]) : '';
    } else if (currentStepData.type === 'select') {
      // Try to match the transcript to one of the options
      const lowerTranscript = transcript.toLowerCase();
      const matchedOption = currentStepData.options.find(option => 
        lowerTranscript.includes(option.replace('_', ' '))
      );
      value = matchedOption || currentStepData.options[0];
    }

    setSurveyData(prev => ({
      ...prev,
      [currentStepData.field]: value
    }));
  };

  const handleNext = () => {
    if (currentStep < surveySteps.length - 1) {
      setCurrentStep(currentStep + 1);
      setVoiceTranscript('');
    } else {
      submitSurvey();
    }
  };

  const handleManualInput = (value) => {
    const currentStepData = surveySteps[currentStep];
    setSurveyData(prev => ({
      ...prev,
      [currentStepData.field]: value
    }));
  };

  const submitSurvey = async () => {
    setIsProcessing(true);
    
    try {
      // Prepare the survey data for Omnidim.io format
      const omnidimData = {
        session_id: `session_${Date.now()}`,
        user_id: null,
        voice_data: {
          confidence_score: 0.95,
          language: "en"
        },
        ...surveyData,
        timestamp: new Date().toISOString()
      };

      // Submit to backend
      const response = await axios.post('/api/v1/survey-submission/', omnidimData);
      
      // Navigate to results page
      navigate(`/results/${response.data.id}`);
      
    } catch (error) {
      console.error('Error submitting survey:', error);
      alert('Error submitting survey. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const currentStepData = surveySteps[currentStep];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Roommate Preferences Survey
          </h1>
          <p className="text-xl text-gray-600">
            Powered by Omnidim.io Voice Assistant
          </p>
          
          {/* Progress Bar */}
          <div className="mt-8">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Step {currentStep + 1} of {surveySteps.length}</span>
              <span>{Math.round(((currentStep + 1) / surveySteps.length) * 100)}% Complete</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <motion.div
                className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${((currentStep + 1) / surveySteps.length) * 100}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
        </motion.div>

        {/* Survey Question */}
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white rounded-2xl shadow-xl p-8 mb-8"
        >
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            {currentStepData.question}
          </h2>

          {/* Voice Recording Section */}
          <div className="mb-6">
            <div className="flex items-center justify-center mb-4">
              <button
                onClick={isRecording ? stopVoiceRecording : startVoiceRecording}
                disabled={isProcessing}
                className={`w-20 h-20 rounded-full flex items-center justify-center text-white font-semibold transition-all duration-300 ${
                  isRecording 
                    ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                    : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700'
                }`}
              >
                {isRecording ? <MicOff className="w-8 h-8" /> : <Mic className="w-8 h-8" />}
              </button>
            </div>
            
            <p className="text-center text-gray-600 mb-4">
              {isRecording ? 'Listening... Speak now!' : 'Click the microphone to start voice input'}
            </p>

            {voiceTranscript && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <p className="text-blue-800 font-medium">Voice Input:</p>
                <p className="text-blue-700">{voiceTranscript}</p>
              </div>
            )}
          </div>

          {/* Manual Input Section */}
          <div className="mb-6">
            <p className="text-gray-600 mb-3">Or type your answer:</p>
            
            {currentStepData.type === 'select' ? (
              <select
                value={surveyData[currentStepData.field] || ''}
                onChange={(e) => handleManualInput(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select an option...</option>
                {currentStepData.options.map(option => (
                  <option key={option} value={option}>
                    {option.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type={currentStepData.type}
                value={surveyData[currentStepData.field] || ''}
                onChange={(e) => handleManualInput(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder={`Enter your ${currentStepData.field.replace('_', ' ')}...`}
              />
            )}
          </div>

          {/* Navigation Buttons */}
          <div className="flex justify-between">
            <button
              onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
              disabled={currentStep === 0 || isProcessing}
              className="px-6 py-3 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            <button
              onClick={handleNext}
              disabled={!surveyData[currentStepData.field] || isProcessing}
              className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Processing...
                </>
              ) : currentStep === surveySteps.length - 1 ? (
                <>
                  <Send className="w-5 h-5 mr-2" />
                  Submit Survey
                </>
              ) : (
                'Next'
              )}
            </button>
          </div>
        </motion.div>

        {/* Omnidim.io Integration Info */}
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-xl p-6">
          <div className="flex items-center mb-3">
            <Mic className="w-6 h-6 text-purple-600 mr-2" />
            <h3 className="text-lg font-semibold text-purple-800">Omnidim.io Voice Assistant</h3>
          </div>
          <p className="text-purple-700">
            This survey is designed to work seamlessly with Omnidim.io voice assistant. 
            In a real implementation, the voice assistant would handle the conversation 
            flow and send structured data to this application.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SurveyPage; 