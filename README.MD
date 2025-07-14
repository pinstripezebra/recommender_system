# Board Game Recommendation System

A board game recommendation service built with **FastAPI**, **PostgreSQL**, and deployed on **Render**. This system uses content-based filtering to provide personalized game recommendations based on user preferences and game characteristics captured in tags.

## 🎯 Overview

This project delivers an intelligent board game recommendation engine that analyzes user gaming history and game tags to suggest new games users might enjoy. The system leverages machine learning techniques including cosine similarity and vector embeddings to provide accurate recommendations. Additionally FastAPI's background_tasks feature is leveraged to ensure that our recommender_pipeline is rerun whenever a user adds a new game to their 'liked games' ensuring the recommendations remain up to date.

## 🏗️ Architecture

### **Tech Stack**
- **Backend**: FastAPI (Python 3.13)
- **Database**: PostgreSQL (hosted on Render)
- **Deployment**: Render (with Docker)
- **CI/CD**: GitHub Actions
- **Containerization**: Docker

### **System Components**
1. **PostgreSQL Database** - Stores user data, game information, tags, and recommendations
2. **FastAPI Application** - REST API for data access and recommendation generation
3. **Background Task Engine** - Asynchronous recommendation processing
4. **Docker Container** - Containerized deployment for consistency
5. **CI/CD Pipeline** - Automated builds and deployments

## 🤖 Recommendation Engine

### **Algorithm Workflow**
The recommendation system runs as a FastAPI background task with the following pipeline:

1. **Data Retrieval** - Fetch user's game history from `user_games` table
2. **Tag Processing** - Load all game tags from `game_tags` table
3. **Vector Creation** - Generate feature vectors for each game based on tags
4. **User Profiling** - Create user preference vector from played games
5. **Similarity Calculation** - Compute cosine similarity between user profile and all games
6. **Recommendation Generation** - Select top-N similar games
7. **Database Update** - Replace existing recommendations with new results

### **Key Features**
- **Content-Based Filtering** using game tags and characteristics
- **Real-time Processing** via FastAPI background tasks
- **Scalable Architecture** with async processing
- **Personalized Results** based on individual user preferences

## 🚀 Getting Started

### **Prerequisites**
- Python 3.8+ (recommended: Python 3.13)
- PostgreSQL database (Render PostgreSQL recommended)
- Docker (optional, for containerized deployment)

### **Installation**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/pinstripezebra/recommender_system.git
   cd recommender_system
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Create a `.env` file in the project root:
   ```env
   # Database Configuration
   External_Database_Url= External Database URL retrieved from Render(or alternatively your database URL from another cloud service)
   DB_PORT=5432
   ```

4. **Database Initialization**
   Run the database setup script to create tables and populate initial data:
   ```bash
   python src/load_database.py
   ```
   
   This script will:
   - Create all necessary database tables
   - Load game data from CSV files
   - Set up user and recommendation tables
   - Verify database connectivity

5. **Start the Application**
   ```bash
   uvicorn src.main:app --reload
   ```
   
   Access the API at: `http://localhost:8000`
   API Documentation: `http://localhost:8000/docs`

## 🐳 Docker Deployment

### **Local Docker Build**
```bash
# Build the image
docker build -t recommendersystem .

# Run the container
docker run -p 8000:8000 --env-file .env recommendersystem
```

### **Docker Hub Deployment**
The project includes automated CI/CD via GitHub Actions:

```bash
# Tag for Docker Hub
docker tag recommendersystem seelucas/fastapi_tutorial:fastapi_on_render

# Push to Docker Hub
docker push seelucas/fastapi_tutorial:fastapi_on_render
```

## 📡 API Endpoints

### **Core Endpoints**
- `GET /` - Health check and API status
- `POST /users/{user_id}/recommendations` - Trigger recommendation generation
- `GET /users/{user_id}/recommendations` - Retrieve user recommendations
- `GET /docs` - Interactive API documentation

### **Database Endpoints**
- User management and game data access
- Recommendation retrieval and updates
- Health monitoring and diagnostics

## 🗂️ Project Structure

```
recommender_system/
├── src/
│   ├── main.py                 # FastAPI application
│   ├── models.py               # SQLAlchemy & Pydantic models
│   ├── similarity_pipeline.py  # Recommendation algorithms
│   ├── load_database.py        # Database initialization
│   └── utils/
│       └── db_handler.py       # Database utilities
├── Data/                       # CSV data files
├── .github/workflows/          # CI/CD configuration
├── Dockerfile                  # Container configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔧 Configuration

### **Environment Variables**
- `External_Database_Url` - Complete PostgreSQL connection string
- `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` - Individual DB parameters

### **Database Tables**
- `users` - User account information
- `games` - Board game catalog
- `game_tags` - Game characteristics and tags
- `user_games` - User gaming history
- `user_recommendations` - Generated recommendations
- `game_similarity` - Precomputed similarity scores

## 🚀 Deployment

### **Render Deployment**
1. Connect your GitHub repository to Render
2. Configure environment variables in Render dashboard
3. Deploy using the provided Dockerfile
4. Run database initialization after first deployment

### **CI/CD Pipeline**
- Automatic Docker builds on main branch commits
- Pushes to Docker Hub registry
- Ready for deployment to any Docker-compatible platform


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
