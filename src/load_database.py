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

# Load environment variables from .env file (override=True reloads changed values)
load_dotenv(override=True)

# Debug: Print loaded environment variables
print("=== Environment Variables ===")
print(f"db_instance_identifier: {os.environ.get('db_instance_identifier')}")
print(f"master_username: {os.environ.get('master_username')}")
print(f"password: {'*' * len(os.environ.get('password', '')) if os.environ.get('password') else 'NOT SET'}")
print(f"RDS_ENDPOINT: {os.environ.get('RDS_ENDPOINT')}")
print(f"RDS_PORT: {os.environ.get('RDS_PORT', '5432')}")
print(f"RDS_DATABASE: {os.environ.get('RDS_DATABASE', 'postgres')}")
print("============================")

# Get AWS RDS connection details from environment variables
db_identifier = os.environ.get("db_instance_identifier")
master_username = os.environ.get("master_username")
password = os.environ.get("password")
rds_endpoint = os.environ.get("RDS_ENDPOINT")
rds_port = os.environ.get("RDS_PORT", "5432")
rds_database = os.environ.get("RDS_DATABASE", "postgres")

# Construct PostgreSQL connection URL for RDS
URL_database = f"postgresql://{master_username}:{password}@{rds_endpoint}:{rds_port}/{rds_database}"

# Initialize DatabaseHandler with the constructed URL
engine = DatabaseHandler(URL_database)

# loading initial user data
users_df = pd.read_csv("Data/users.csv")
games_df = pd.read_csv("Data/games.csv")
user_games_df = pd.read_csv("Data/user_games.csv")
user_recommendations_df = pd.read_csv("Data/user_recommendations.csv")
game_tags_df = pd.read_csv("Data/game_tags.csv")


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
    title VARCHAR(255) NOT NULL,
    description TEXT,
    price FLOAT NOT NULL,
    rating FLOAT,
    sales_volume VARCHAR(255),
    reviews_count INTEGER,
    asin VARCHAR(255) UNIQUE NOT NULL,
    image_link VARCHAR(255)
    )
    """

user_games_query = """CREATE TABLE IF NOT EXISTS user_games (
    id UUID PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    asin VARCHAR(255) NOT NULL,
    shelf VARCHAR(50) DEFAULT 'Wish_List',
    rating FLOAT DEFAULT 0.0,
    review TEXT,
    FOREIGN KEY (username) REFERENCES users(username),
    FOREIGN KEY (asin) REFERENCES games(asin)
    )
    """
recommendation_table_creation_query = """CREATE TABLE IF NOT EXISTS user_recommendations (
    id UUID PRIMARY KEY,
    username VARCHAR(255),
    asin VARCHAR(255),
    similarity FLOAT
    )
    """

game_tags_creation_query = """CREATE TABLE IF NOT EXISTS game_tags (
    id UUID PRIMARY KEY,
    tag VARCHAR(255) NOT NULL
    )
    """



# Running queries to create tables
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
engine.populate_table_dynamic(users_df, 'optigame_users')
engine.populate_table_dynamic(games_df, 'optigame_products')
engine.populate_table_dynamic(user_games_df, 'optigame_user_games')
engine.populate_table_dynamic(user_recommendations_df, 'user_recommendations')
engine.populate_table_dynamic(game_tags_df, 'game_tags')

# Testing if the tables were created and populated correctly
print(engine.test_table('optigame_users'))
print(engine.test_table('optigame_products'))
print(engine.test_table('optigame_user_games'))
print(engine.test_table('user_recommendations'))
print(engine.test_table('game_tags'))