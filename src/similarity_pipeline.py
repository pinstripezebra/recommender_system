from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from src.models import UserGame, UserRecommendation
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import uuid
from typing import List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRecommendationService:
    def __init__(self, db_session: Session, database_url: str):
        self.db = db_session
        self.database_url = database_url
        self.engine = create_engine(database_url)

    def fetch_user_games(self, username: str) -> pd.DataFrame:
        """Fetch all games for a specific user"""
        query = text("SELECT username, asin FROM user_games WHERE username = :username")
        with self.engine.connect() as conn:
            result = conn.execute(query, {"username": username})
            data = result.fetchall()
            return pd.DataFrame(data, columns=['username', 'asin'])

    def fetch_all_game_tags(self) -> pd.DataFrame:
        """Fetch all game tags"""
        query = text("SELECT asin, game_tags FROM game_tags")
        with self.engine.connect() as conn:
            result = conn.execute(query)
            data = result.fetchall()
            return pd.DataFrame(data, columns=['asin', 'game_tags'])

    def create_game_vectors(self, tag_df: pd.DataFrame) -> tuple[pd.DataFrame, List[str], List[str]]:
        """Create game vectors from tags"""
        unique_tags = tag_df['game_tags'].drop_duplicates().sort_values().tolist()
        unique_games = tag_df['asin'].drop_duplicates().sort_values().tolist()
        
        game_vectors = []
        for game in unique_games:
            tags = tag_df[tag_df['asin'] == game]['game_tags'].tolist()
            vector = [1 if tag in tags else 0 for tag in unique_tags]
            game_vectors.append(vector)
        
        return pd.DataFrame(game_vectors, columns=unique_tags, index=unique_games), unique_tags, unique_games

    def create_user_vector(self, user_games_df: pd.DataFrame, game_vectors: pd.DataFrame, unique_tags: List[str]) -> pd.DataFrame:
        """Create user vector from their played games"""
        if user_games_df.empty:
            return pd.DataFrame([[0] * len(unique_tags)], columns=unique_tags, index=['unknown_user'])
        
        username = user_games_df.iloc[0]['username']
        user_games = user_games_df['asin'].tolist()
        
        # Only keep games that exist in game_vectors
        user_games = [g for g in user_games if g in game_vectors.index]
        
        if not user_games:
            user_vector = [0] * len(unique_tags)
        else:
            played_game_vectors = game_vectors.loc[user_games]
            user_vector = played_game_vectors.mean(axis=0).tolist()
        
        return pd.DataFrame([user_vector], columns=unique_tags, index=[username])

    def calculate_user_recommendations(self, user_vector: pd.DataFrame, game_vectors: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
        """Calculate similarity between user vector and all game vectors"""
        username = user_vector.index[0]
        user_vector_data = user_vector.iloc[0].values.reshape(1, -1)
        
        # Calculate similarities
        similarities = cosine_similarity(user_vector_data, game_vectors)
        similarity_df = pd.DataFrame(similarities.T, index=game_vectors.index, columns=[username])
        
        # Get top N recommendations
        top_games = similarity_df[username].nlargest(top_n)
        
        recommendations = []
        for asin, similarity in top_games.items():
            recommendations.append({
                "username": username,
                "asin": asin,
                "similarity": float(similarity)
            })
        
        return pd.DataFrame(recommendations)

    def delete_existing_recommendations(self, username: str):
        """Delete existing recommendations for a user"""
        self.db.query(UserRecommendation).filter(UserRecommendation.username == username).delete()
        self.db.commit()

    def save_recommendations(self, recommendations_df: pd.DataFrame):
        """Save new recommendations to database"""
        for _, row in recommendations_df.iterrows():
            recommendation = UserRecommendation(
                id=uuid.uuid4(),
                username=row['username'],
                asin=row['asin'],
                similarity=row['similarity']
            )
            self.db.add(recommendation)
        self.db.commit()

    def generate_recommendations_for_user(self, username: str, top_n: int = 20):
        """Main method to generate recommendations for a specific user"""
        try:
            logger.info(f"Starting recommendation generation for user: {username}")
            
            # 1. Fetch user's games
            user_games_df = self.fetch_user_games(username)
            if user_games_df.empty:
                logger.warning(f"No games found for user: {username}")
                return
            
            # 2. Fetch all game tags
            tag_df = self.fetch_all_game_tags()
            if tag_df.empty:
                logger.error("No game tags found in database")
                return
            
            # 3. Create game vectors
            game_vectors, unique_tags, unique_games = self.create_game_vectors(tag_df)
            
            # 4. Create user vector
            user_vector = self.create_user_vector(user_games_df, game_vectors, unique_tags)
            
            # 5. Calculate recommendations
            recommendations_df = self.calculate_user_recommendations(user_vector, game_vectors, top_n)
            
            # 6. Delete existing recommendations
            self.delete_existing_recommendations(username)
            
            # 7. Save new recommendations
            self.save_recommendations(recommendations_df)
            
            logger.info(f"Successfully generated {len(recommendations_df)} recommendations for user: {username}")
            
        except Exception as e:
            logger.error(f"Error generating recommendations for user {username}: {str(e)}")
            self.db.rollback()
            raise