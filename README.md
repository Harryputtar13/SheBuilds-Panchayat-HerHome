# AI Roommate Matching System

An intelligent roommate matching system powered by AI and machine learning algorithms.

## Features

- **AI-Powered Matching**: Uses Sentence-BERT, KNN, SVD, and Logistic Regression for optimal roommate matching
- **Voice Assistant Integration**: Compatible with Omnidim.io Voice Assistant for seamless data collection
- **Real-time Recommendations**: Get instant roommate matches with compatibility scores
- **Modern UI**: Beautiful React frontend with Tailwind CSS

## Tech Stack

- **Backend**: Python with FastAPI
- **Database**: PostgreSQL
- **ML Models**: Sentence-BERT, K-Nearest Neighbors, SVD, Logistic Regression
- **Frontend**: React with Tailwind CSS, shadcn/ui
- **Libraries**: scikit-learn, Surprise, pandas, sentence-transformers

## Project Structure

```
roommate-matcher/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── database/         # Database migrations and setup
└── docker-compose.yml
```

## Quick Start

### Option 1: Local PostgreSQL
1. Clone the repository
2. Run `docker-compose up` to start all services
3. Access the frontend at `http://localhost:3000`
4. API documentation available at `http://localhost:8000/docs`

### Option 2: Neon DB (Recommended)
1. Clone the repository
2. Follow the [Neon DB Integration Guide](NEON_INTEGRATION.md)
3. Run `docker-compose -f docker-compose.neon.yml up` to start services
4. Access the frontend at `http://localhost:3000`
5. API documentation available at `http://localhost:8000/docs`

## Development Roadmap

- ✅ Stage 1: Backend Foundation & Data Ingestion
- ✅ Stage 2: Data Preprocessing & NLP Model
- ✅ Stage 3: Machine Learning Model Training
- ✅ Stage 4: Matching & Recommendation Service
- ✅ Stage 5: Frontend Development
- ✅ Stage 6: Room Allocation Logic

## Current Status

**All Stages Complete!** 🎉🚀

The AI Roommate Matching System is now fully implemented with:

### Backend Features
- ✅ Complete FastAPI backend with Omnidim.io voice assistant integration
- ✅ PostgreSQL database with comprehensive schema
- ✅ Sentence-BERT embedding service for NLP processing
- ✅ Machine Learning models (KNN, SVD, Logistic Regression)
- ✅ Intelligent room allocation algorithms
- ✅ Real-time compatibility scoring and matching

### Frontend Features
- ✅ Beautiful React frontend with Tailwind CSS
- ✅ Voice simulation interface for Omnidim.io integration
- ✅ Comprehensive admin dashboard for system management
- ✅ Real-time progress tracking and statistics
- ✅ Responsive design with modern UI/UX

### ML & AI Features
- ✅ Data preprocessing pipeline with text embeddings
- ✅ Multi-algorithm matching system
- ✅ Compatibility scoring using multiple factors
- ✅ Room allocation with different strategies
- ✅ Model training and management interface

### System Features
- ✅ Docker containerization for easy deployment
- ✅ Comprehensive API documentation
- ✅ Real-time monitoring and status tracking
- ✅ Scalable architecture for production use

**The system is now production-ready!** 🎯  