from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from utils.db_handler import DatabaseHandler
import pandas as pd
import uuid
import sys
from sqlalchemy.exc import OperationalError
import psycopg2

# Load environment variables from .env file
load_dotenv(override=True)

# Construct PostgreSQL connection URL for Render
URL_database = os.environ.get("External_Database_Url")

# Initialize DatabaseHandler with the constructed URL
engine = DatabaseHandler(URL_database)

# loading initial user data
users_df = pd.read_csv("Data/steam_users.csv")
games_df = pd.read_csv("Data/steam_games.csv")
user_games_df = pd.read_csv("Data/steam_user_games.csv")
user_recommendations_df = pd.read_csv("Data/user_recommendations.csv")
game_tags_df = pd.read_csv("Data/steam_game_tags.csv")


# Defining queries to create tables
user_table_creation_query = """CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL
    )
    """
game_table_creation_query = """CREATE TABLE IF NOT EXISTS games (
    id UUID PRIMARY KEY,
    appid VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(255),
    is_free BOOLEAN DEFAULT FALSE,
    short_description TEXT,
    detailed_description TEXT,
    developers VARCHAR(255),
    publishers VARCHAR(255),
    price VARCHAR(255),
    genres VARCHAR(255),
    categories VARCHAR(255),
    release_date VARCHAR(255),
    platforms TEXT,
    metacritic_score FLOAT,
    recommendations INTEGER
    )
    """

user_games_query = """CREATE TABLE IF NOT EXISTS user_games (
    id UUID PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    appid VARCHAR(255) NOT NULL,
    shelf VARCHAR(50) DEFAULT 'Wish_List',
    rating FLOAT DEFAULT 0.0,
    review TEXT
    )
    """
recommendation_table_creation_query = """CREATE TABLE IF NOT EXISTS user_recommendations (
    id UUID PRIMARY KEY,
    username VARCHAR(255),
    appid VARCHAR(255),
    similarity FLOAT
    )
    """

game_tags_creation_query = """CREATE TABLE IF NOT EXISTS game_tags (
    id UUID PRIMARY KEY,
    appid VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL
    )
    """



# Running queries to create tables
engine.delete_table('user_recommendations')
engine.delete_table('user_games')
engine.delete_table('game_tags')
engine.delete_table('games')
engine.delete_table('users')

# Create tables
engine.create_table(user_table_creation_query)
engine.create_table(game_table_creation_query)
engine.create_table(user_games_query)
engine.create_table(recommendation_table_creation_query)
engine.create_table(game_tags_creation_query)

# Ensuring each row of each dataframe has a unique ID
if 'id' not in users_df.columns:
    users_df['id'] = [str(uuid.uuid4()) for _ in range(len(users_df))]
if 'id' not in games_df.columns:
    games_df['id'] = [str(uuid.uuid4()) for _ in range(len(games_df))]
if 'id' not in user_games_df.columns:
    user_games_df['id'] = [str(uuid.uuid4()) for _ in range(len(user_games_df))]
if 'id' not in user_recommendations_df.columns:
    user_recommendations_df['id'] = [str(uuid.uuid4()) for _ in range(len(user_recommendations_df))]
if 'id' not in game_tags_df.columns:
    game_tags_df['id'] = [str(uuid.uuid4()) for _ in range(len(game_tags_df))]

# Populates the 4 tables with data from the dataframes
engine.populate_table_dynamic(users_df, 'users')
engine.populate_table_dynamic(games_df, 'games')
engine.populate_table_dynamic(user_games_df, 'user_games')
engine.populate_table_dynamic(user_recommendations_df, 'user_recommendations')
engine.populate_table_dynamic(game_tags_df, 'game_tags')

# Testing if the tables were created and populated correctly
print(engine.test_table('users'))
print(engine.test_table('games'))
print(engine.test_table('user_games'))
print(engine.test_table('user_recommendations'))
print(engine.test_table('game_tags'))