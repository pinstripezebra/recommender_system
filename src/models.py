from pydantic import BaseModel
from uuid import UUID,uuid4
from typing import Optional
from enum import Enum
from sqlalchemy import Column, String, Float, Integer
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from uuid import UUID

# loading sql model
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Initialize the base class for SQLAlchemy models
Base = declarative_base()

# This is the game model for the database
# we have separate classes for the pydantic model and the SQLAlchemy model
class Game(Base):
    __tablename__ = "optigame_products"  # Table name in the PostgreSQL database

    id = Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    rating = Column(Float, nullable=True)
    sales_volume = Column(String, nullable=True)
    reviews_count = Column(Integer, nullable=True)
    asin = Column(String, unique=True, nullable=False)
    image_link = Column(String, nullable=True)


class GameModel(BaseModel):
    id: Optional[UUID]
    title: str
    description: Optional[str]
    price: float
    rating: Optional[float]
    sales_volume: Optional[str]
    reviews_count: Optional[int]
    asin: str
    image_link: str

    class Config:
        orm_mode = True  # Enable ORM mode to work with SQLAlchemy objects
        from_attributes = True # Enable attribute access for SQLAlchemy objects


# This is the User model for the database
class User(Base):
    __tablename__ = "users"  # Table name in the PostgreSQL database

    id = Column(pg.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False)
    role = Column(String, nullable=False)


class UserModel(BaseModel):
    id: Optional[UUID] = None
    username: str
    password: str
    email: str
    role: str

    class Config:
        orm_mode = True  # Enable ORM mode to work with SQLAlchemy objects
        from_attributes = True # Enable attribute access for SQLAlchemy objects



# This user_id:game_id mapping model
class UserGame(Base):
    __tablename__ = "user_games"  # Table name in the PostgreSQL database

    id = Column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
    asin = Column(String, nullable=False)
    shelf = Column(String, nullable=False)
    rating = Column(Float, nullable=False)
    review = Column(String, nullable=False)


class UserGameModel(BaseModel):
    id: Optional[UUID]  = None
    username: str
    asin: str
    shelf: Optional[str] = None
    rating: Optional[float] = None
    review: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True


# This is the Game Similarity model for the database
class GameSimilarity(Base):
    __tablename__ = "game_similarity"  # Table name in the PostgreSQL database

    id = Column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game1 = Column(String, nullable=False)
    game2 = Column(String, nullable=False)
    similarity = Column(Float, nullable=False)
    
class GameSimilarityModel(BaseModel):
    id: Optional[UUID] = None
    game1: str
    game2: str
    similarity: float

    class Config:
        orm_mode = True  # Enable ORM mode to work with SQLAlchemy objects
        from_attributes = True # Enable attribute access for SQLAlchemy objects



# UserRecommendation model for the database
class UserRecommendation(Base):
    __tablename__ = "user_recommendations"  # Table name in the PostgreSQL database

    id = Column(SA_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
    asin = Column(String, nullable=False)
    similarity = Column(Float, nullable=False)
    
class UserRecommendationModel(BaseModel):
    id: Optional[UUID] = None
    username: str
    asin: str
    similarity: float

    class Config:
        orm_mode = True  # Enable ORM mode to work with SQLAlchemy objects
        from_attributes = True # Enable attribute access for SQLAlchemy objects


# authentication
class Token(BaseModel):
    access_token: str
    token_type: str
