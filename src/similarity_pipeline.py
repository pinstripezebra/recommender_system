from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.utils.db_handler import DatabaseHandler
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import uuid
from dotenv import load_dotenv

source_table_name1 = "optigame_user_games" # contains user_id:asin mapping
source_table_name2 = "optigame_game_tags" # contains asin:game_tags mapping
target_table_name = "user_recommendations"

load_dotenv(dotenv_path=".env2")
URL_database = os.environ.get("DATABASE_URL")
engine = DatabaseHandler(URL_database)


# game: tag data
tag_df = engine.retrieve_all_from_table(source_table_name2)
unique_tags = tag_df['game_tags'].drop_duplicates().sort_values().tolist()
unique_games = tag_df['asin'].drop_duplicates().sort_values().tolist()

# user: game data
user_game_df = engine.retrieve_all_from_table(source_table_name1)
unique_users = user_game_df['username'].drop_duplicates().sort_values().tolist()


def calculate_aggregate_by_user(user_game_df, unique_users, game_vectors, unique_tags):
    """
    Calculate the aggregate game vector for each user based on their played games.
    """
    user_vectors = []
    # iterate through each user
    for user in unique_users:
        user_games = user_game_df[user_game_df['username'] == user]['asin'].tolist()
        # Only keep games that exist in game_vectors
        user_games = [g for g in user_games if g in game_vectors.index]
        played_game_vectors = game_vectors.loc[user_games]
        # Calculate the mean vector for the user's played games
        if not played_game_vectors.empty:
            user_vector = played_game_vectors.mean(axis=0).tolist()
        else:
            user_vector = [0] * len(unique_tags)
    user_vectors.append(user_vector)
        
    return pd.DataFrame(user_vectors, columns=unique_tags, index=unique_users)

def add_game_vector(unique_tags, unique_games, df):
    """
    Create a game vector for each game based on its tags.
    """
    game_vectors = []
    for game in unique_games:
        tags = df[df['asin'] == game]['game_tags'].tolist()
        vector = [1 if tag in tags else 0 for tag in unique_tags]
        game_vectors.append(vector)
    return pd.DataFrame(game_vectors, columns=unique_tags, index=unique_games)

def calculate_similiar_game(user_vector, game_vectors, top_n=20):
    """
    Calculate the cosine similarity between a user's game vector and all game vectors.
    """
    unique_users = user_vector.index.tolist()
    output = []
    # generating (asin) x (user) similarity matrix
    for user in unique_users:
        user_vector_data = user_vector.loc[user].values.reshape(1, -1)
        similarities = cosine_similarity(user_vector_data, game_vectors)
        similarity_df = pd.DataFrame(similarities.T, index=game_vectors.index, columns=[user])
        output.append(similarity_df)
    
    # converting to username, asin, similarity format
    output_df = pd.concat(output, axis=1)
    recommendations = []
    for username in output_df.columns:
        top_games = output_df[username].nlargest(top_n)
        for asin, similarity in top_games.items():
            recommendations.append({
                "username": username,
                "asin": asin,
                "similarity": similarity
            })
    recommendations_df = pd.DataFrame(recommendations, columns=["username", "asin", "similarity"])
    return recommendations_df


# vectorizing game tags
game_vectors = add_game_vector(unique_tags, unique_games, tag_df)

# calculating aggregate game vectors for each user
user_vectors = calculate_aggregate_by_user(user_game_df, unique_users, game_vectors, unique_tags)
print(user_vectors)
print(game_vectors)
# calculating similarity between user vectors and game vectors

user_recommendations = calculate_similiar_game(user_vectors, game_vectors)
print(user_recommendations)


# uploading the similarity matrix to the database
table_creation_query = """CREATE TABLE IF NOT EXISTS user_recommendations (
    id UUID PRIMARY KEY,
    username VARCHAR(255),
    asin VARCHAR(255),
    similarity FLOAT
    )
    """

# delete table if it exists
engine.delete_table(target_table_name)
# creating table
engine.create_table(table_creation_query)

# add 'id' column with unique UUIDs as strings
user_recommendations['id'] = [str(uuid.uuid4()) for _ in range(len(user_recommendations))]

# populating table with similarity data
engine.populate_user_recommendation(user_recommendations)

# checking to ensure data is in table
df = engine.retrieve_all_from_table(target_table_name)
print(df)