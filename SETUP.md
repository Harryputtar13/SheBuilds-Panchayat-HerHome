# AI Roommate Matching System - Complete Setup Guide

This guide will help you set up and run the complete AI Roommate Matching System with all features implemented.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- At least 4GB RAM available
- Internet connection for downloading ML models

### 1. Clone and Setup
```bash
git clone <repository-url>
cd SheBuilds-Panchayat-HerHome
```

### 2. Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit .env file with your settings
nano .env
```

### 3. Start the System
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Admin Dashboard**: http://localhost:3000/admin

## 📋 System Architecture

### Backend Services
- **FastAPI Server** (Port 8000): Main API server
- **PostgreSQL Database** (Port 5432): Data storage
- **ML Models**: KNN, SVD, Logistic Regression
- **Embedding Service**: Sentence-BERT for NLP

### Frontend Services
- **React App** (Port 3000): User interface
- **Admin Dashboard**: System management
- **Voice Simulation**: Omnidim.io integration

## 🔧 Initial Setup Steps

### 1. Data Preprocessing
After starting the system, you need to preprocess user data:

1. Go to **Admin Dashboard** → **ML Training**
2. Click **"Preprocess Dataset"** to generate embeddings
3. Wait for completion (check progress bar)

### 2. Train ML Models
Once you have at least 10 users with embeddings:

1. Go to **Admin Dashboard** → **ML Training**
2. Click **"Train ML Models"**
3. Monitor training progress
4. Models will be saved automatically

### 3. Room Allocation
To allocate rooms to users:

1. Go to **Admin Dashboard** → **Room Allocation**
2. Choose allocation strategy:
   - **Compatibility First**: Prioritize user compatibility
   - **Budget First**: Prioritize budget constraints
   - **Location First**: Prioritize location preferences
   - **Balanced**: Consider all factors equally
3. Click **"Allocate Rooms"**

## 🎯 Using the System

### For Users
1. **Take Survey**: Visit `/survey` to complete the roommate preference survey
2. **Voice Input**: Use the voice simulation interface (Omnidim.io compatible)
3. **View Results**: Get matched with compatible roommates
4. **Room Assignment**: Check assigned room details

### For Administrators
1. **Monitor System**: Use the admin dashboard for real-time monitoring
2. **Manage Users**: View all users and their processing status
3. **Manage Rooms**: View room availability and assignments
4. **ML Operations**: Train, load, and monitor ML models
5. **Allocation Management**: Run room allocation algorithms

## 🔍 API Endpoints

### Core Endpoints
- `POST /api/v1/survey-submission/` - Submit user survey
- `GET /api/v1/users/` - Get all users
- `GET /api/v1/rooms/` - Get all rooms

### ML & Preprocessing
- `POST /api/v1/preprocess-dataset/` - Preprocess all user data
- `POST /api/v1/train-models/` - Train ML models
- `GET /api/v1/model-status/` - Check model status
- `POST /api/v1/load-models/` - Load saved models

### Matching & Allocation
- `GET /api/v1/match/{user_id}` - Get roommate matches
- `POST /api/v1/allocate-rooms/` - Allocate rooms
- `GET /api/v1/allocation-status/` - Check allocation status

## 🧠 Machine Learning Features

### Models Implemented
1. **K-Nearest Neighbors (KNN)**: Find similar users
2. **Singular Value Decomposition (SVD)**: Dimensionality reduction
3. **Logistic Regression**: Compatibility prediction
4. **Sentence-BERT**: Text embedding generation

### Compatibility Factors
- Sleep schedule compatibility
- Cleanliness preferences
- Noise tolerance levels
- Social preferences
- Pet and smoking preferences
- Budget constraints
- Location preferences

## 🏠 Room Allocation Strategies

### Available Strategies
1. **Compatibility First**: Groups compatible users together
2. **Budget First**: Matches users to rooms within their budget
3. **Location First**: Prioritizes location preferences
4. **Balanced**: Considers all factors equally

### Allocation Process
1. Analyze user preferences and constraints
2. Calculate compatibility scores
3. Match users to available rooms
4. Update database with assignments
5. Provide detailed allocation reports

## 📊 Monitoring & Analytics

### Admin Dashboard Features
- **System Overview**: Real-time statistics
- **Data Processing**: Embedding generation progress
- **ML Training**: Model status and training requirements
- **Room Allocation**: Assignment rates and occupancy
- **User Management**: User data and processing status
- **Room Management**: Room availability and details

### Key Metrics
- Total users and processing status
- ML model readiness
- Room allocation success rate
- System performance indicators

## 🔧 Troubleshooting

### Common Issues

#### 1. ML Models Not Training
- **Cause**: Insufficient user data
- **Solution**: Add more users (minimum 10 required)
- **Check**: Go to Admin Dashboard → ML Training

#### 2. Embeddings Not Generating
- **Cause**: Sentence-BERT model not loaded
- **Solution**: Check internet connection and restart services
- **Check**: Look for embedding service logs

#### 3. Room Allocation Fails
- **Cause**: No available rooms or users
- **Solution**: Add rooms to database or check user data
- **Check**: Admin Dashboard → Room Allocation

#### 4. Database Connection Issues
- **Cause**: PostgreSQL not starting
- **Solution**: Check Docker logs and restart services
- **Command**: `docker-compose logs postgres`

### Logs and Debugging
```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Restart services
docker-compose restart
```

## 🚀 Production Deployment

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/roommate_matcher

# ML Models
MODEL_CACHE_DIR=/app/models
SENTENCE_TRANSFORMERS_CACHE=/app/models

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

### Scaling Considerations
- **Database**: Use managed PostgreSQL service
- **ML Models**: Implement model serving with Redis cache
- **API**: Use load balancer for multiple instances
- **Frontend**: Use CDN for static assets

## 📈 Performance Optimization

### Database Optimization
- Indexes on frequently queried columns
- Connection pooling for high concurrency
- Regular database maintenance

### ML Model Optimization
- Model caching and persistence
- Batch processing for embeddings
- Async processing for non-blocking operations

### Frontend Optimization
- Code splitting and lazy loading
- Image optimization
- Caching strategies

## 🔒 Security Considerations

### API Security
- Input validation and sanitization
- Rate limiting
- CORS configuration
- Authentication (implement as needed)

### Data Privacy
- User data encryption
- GDPR compliance
- Data retention policies
- Secure data transmission

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

### ML Libraries
- [scikit-learn](https://scikit-learn.org/)
- [Sentence Transformers](https://www.sbert.net/)
- [NumPy](https://numpy.org/)
- [Pandas](https://pandas.pydata.org/)

## 🎉 Success!

Your AI Roommate Matching System is now fully operational! 

**Next Steps:**
1. Add sample users through the survey interface
2. Preprocess the data to generate embeddings
3. Train the ML models
4. Test room allocation with different strategies
5. Monitor system performance through the admin dashboard

**Support:**
- Check the API documentation at `/docs`
- Use the admin dashboard for system monitoring
- Review logs for troubleshooting
- Refer to this guide for common issues

Happy matching! 🏠✨ 