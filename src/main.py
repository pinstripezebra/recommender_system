from fastapi import FastAPI, Depends, HTTPException, status
from uuid import uuid4, UUID
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import dotenv_values
from datetime import datetime, timedelta

# security imports
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# custom imports
from src.models import User, Game, GameModel, UserModel,  UserGameModel, UserGame, GameSimilarity,GameSimilarityModel, UserRecommendation, UserRecommendationModel


config = dotenv_values(".env")

# Load the database connection string from the environment variable
DATABASE_URL = config["DATABASE_URL"]
USER_TABLE = config["USER_TABLE"]


# Initialize the database connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create the database tables (if they don't already exist)
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize the FastAPI app
app = FastAPI(title="Game Store API", version="1.0.0")

# secure the API with OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Add CORS middleware to allow requests 
origins = ["http://localhost:8000", 
           "http://localhost:5174", 
           "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



#-------------------------------------------------#
# ----------PART 1: GET METHODS-------------------#
#-------------------------------------------------#




@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/api/v1/games/")
async def fetch_products(asin: str = None, db: Session = Depends(get_db)):
    # Query the database using the SQLAlchemy Game model
    if asin:
        products = db.query(Game).filter(Game.asin == asin).all()
    else:
        products = db.query(Game).all()
    return [GameModel.from_orm(product) for product in products]

@app.get("/api/v1/users/")
async def fetch_users(username: str, db: Session = Depends(get_db)):
    users = db.query(User).filter(User.username == username).all()
    return [UserModel.from_orm(user) for user in users]

@app.get("/api/v1/similar_games/")
async def fetch_similar_games(asin: str, db: Session = Depends(get_db)):
    # Query the database and return result
    similar_games = db.query(GameSimilarity).filter(GameSimilarity.game1 == asin).all()
    return [GameSimilarityModel.from_orm(game) for game in similar_games]


@app.get("/api/v1/user_recommended_game/")
async def fetch_recommended_game(username: str, db: Session = Depends(get_db)):
    user_recommendations = db.query(UserRecommendation).filter(UserRecommendation.username == username)
    return [UserRecommendationModel.from_orm(recommendation) for recommendation in user_recommendations]

@app.get("/api/v1/user_game/")
async def fetch_user_recommendation(username: str, db: Session = Depends(get_db)):
    # Query the database using the SQLAlchemyfor user_games
    user_games = db.query(UserGame).filter(UserGame.username == username)
    return [UserGameModel.from_orm(user_game) for user_game in user_games]

#-------------------------------------------------#
# ----------PART 2: POST METHODS------------------#
#-------------------------------------------------#


@app.post("/api/v1/user_game/")
async def create_user_game(user_game: UserGameModel, db: Session = Depends(get_db)):
    # Check if the entry already exists
    existing = db.query(UserGame).filter_by(username=user_game.username, asin=user_game.asin).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already has this game.")

    # Prepare data with defaults
    user_game_data = {
        "username": user_game.username,
        "asin": user_game.asin,
        "shelf": user_game.shelf if user_game.shelf is not None else "Wish_List",
        "rating": user_game.rating if user_game.rating is not None else 0.0,
        "review": user_game.review if user_game.review is not None else ""
    }
    if user_game.id is not None:
        user_game_data["id"] = UUID(str(user_game.id))

    db_user_game = UserGame(**user_game_data)
    db.add(db_user_game)
    db.commit()
    db.refresh(db_user_game)
    return db_user_game

#-------------------------------------------------#
# ----------PART 3: DELETE METHODS----------------#
#-------------------------------------------------#


@app.delete("/api/v1/user_game/")
async def delete_user_game(username: str, asin: str, db: Session = Depends(get_db)):
    user_game = db.query(UserGame).filter_by(username=username, asin=asin).first()
    if not user_game:
        raise HTTPException(status_code=404, detail="User game not found.")
    db.delete(user_game)
    db.commit()
    return {"detail": "User game deleted successfully."}

