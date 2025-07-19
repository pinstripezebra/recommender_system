# Steam Game Recommendation System

A Steam game recommendation service built with **FastAPI**, **PostgreSQL**, and deployed on **Render**. This system uses content-based filtering to provide personalized game recommendations based on user preferences and Steam game category tags.

## 🎯 Overview

This project highlights how to deploy a recommender system leveraging FastAPI and steam game data to recommend new games for a user based on games that they've previously expressed intrest in. The system leverages vector embeddings to convert the tags associated with each game into a vector and then uses a cosine similarity score to calculate which games are most like the games that a given user has interacted with. Additionally, FastAPI's background_tasks feature is leveraged to ensure that our recommender_pipeline is rerun whenever a user adds a new game to their library, ensuring the recommendations remain up to date.

## 🏗️ Architecture

### **Tech Stack**
- **Backend**: FastAPI (Python 3.13)
- **Database**: PostgreSQL (hosted on Render)
- **Deployment**: Render (with Docker)
- **CI/CD**: GitHub Actions
- **Containerization**: Docker

### **System Components**
1. **PostgreSQL Database** - Stores user data, Steam game information, genres, categories, and recommendations
2. **FastAPI Application** - REST API for data access and recommendation generation
3. **Background Task Engine** - Asynchronous recommendation processing using Steam game metadata
4. **Docker Container** - Containerized deployment for consistency
5. **CI/CD Pipeline** - Automated builds and deployments

## 🤖 Recommendation Engine

### **Algorithm Workflow**
The recommendation system runs as a FastAPI background task with the following pipeline:

1. **Data Retrieval** - Fetch user's Steam game library from `user_games` table
2. **Vector Creation** - Generate feature vectors for each game based on Steam game tags
3. **User Profiling** - Create user preference vector from owned/liked Steam games
4. **Similarity Calculation** - Compute cosine similarity between user profile and all Steam games
5. **Recommendation Generation** - Select top-N similar Steam games
6. **Database Update** - Replace existing recommendations with new results

### **Key Features**
- **Content-Based Filtering** using Steam game genres, categories, and metadata
- **Real-time Processing** via FastAPI background tasks
- **Steam API Integration** for rich game data
- **Scalable Architecture** with async processing
- **Personalized Results** based on individual Steam gaming preferences

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
   # This is our Database Connection URL from Render
   External_Database_Url=postgresql://username:password@host:port/database
   
   ```

4. **Database Initialization**
   Run the database setup script to create tables and populate initial Steam game data:
   ```bash
   python src/load_database.py
   ```
   
   This script will:
   - Create all necessary database tables
   - Load Steam game data from CSV files (steam_games.csv, steam_game_tags.csv, etc.)
   - Set up user profiles and recommendation tables
   - Verify database connectivity with Steam game schema

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
- `POST /users/{user_id}/recommendations` - Trigger Steam game recommendation generation
- `GET /users/{user_id}/recommendations` - Retrieve user's Steam game recommendations
- `GET /games/{app_id}` - Get detailed Steam game information
- `GET /docs` - Interactive API documentation

### **Database Endpoints**
- User Steam library management and game data access
- Steam game recommendation retrieval and updates
- Steam game metadata queries (genres, categories, developers)
- Health monitoring and diagnostics

## 🗂️ Project Structure

```
recommender_system/
├── src/
│   ├── main.py                 # FastAPI application
│   ├── models.py               # SQLAlchemy & Pydantic models for Steam games
│   ├── similarity_pipeline.py  # Steam game recommendation algorithms
│   ├── load_database.py        # Database initialization with Steam data
│   ├── query_steam_api.py      # Steam API integration utilities
│   └── utils/
│       └── db_handler.py       # Database utilities
├── Data/                       # Steam game CSV data files
│   ├── steam_games.csv         # Steam game catalog
│   ├── steam_game_tags.csv     # Steam game tags and genres
│   ├── steam_users.csv         # User profiles
│   ├── steam_user_games.csv    # User Steam libraries
│   └── user_recommendations.csv # Generated recommendations
├── .github/workflows/          # CI/CD configuration
├── Dockerfile                  # Container configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔧 Configuration

### **Environment Variables**
- `External_Database_Url` - Complete PostgreSQL connection string

### **Database Tables**
- `users` - User account information and Steam profiles
- `games` - Steam game catalog with metadata (appid, name, genres, categories, etc.)
- `game_tags` - Steam game tags, genres, and categories
- `user_games` - User Steam libraries and game ownership
- `user_recommendations` - Generated Steam game recommendations
- `game_similarity` - Precomputed similarity scores between Steam games

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

## 🛠️ Development

### **Running Tests**
```bash
# Run the Steam recommendation system test
python src/similarity_pipeline.py

# Test Steam API integration
python src/query_steam_api.py
```

### **Database Management**
```bash
# Check database connection
python src/check_render_connection.py

# Reload Steam game database
python src/load_database.py
```


## 🆘 Support

For issues and questions:
- Check the [API documentation](http://localhost:8000/docs)
- Review the Steam database connection scripts
- Examine the CI/CD workflow files
- Steam API documentation: [Steam Web API](https://steamcommunity.com/dev)


## 📄 License

---

**Built with FastAPI, PostgreSQL, and Steam Web API
