### Overview

This project leverages FastAPI and render to deploy a board game recommendation service, using a content based recommender to identify games similar to those liked by a given user.


### Components
1. Data Stored on PostgreSQL database hosted on render
2. Data Access and updates is managed through a FastAPI project also deployed onr ender
3. Recommendations are generated when a user updates the user_games table, leveraging a FastApi Background Task to update the relevant recommendation table


### Recommendations Workflow
The recommendations workflow is ran as a FastAPI background task triggering elements in the following order
1. Fetch user's games from optigame_user_games
2. Fetch all game tags from optigame_game_tags  
3. Create game vectors from tags
4. Create user vector from played games
5. Calculate cosine similarity
6. Delete existing recommendations for user
7. Insert new top-N recommendations

# Initializing Database
To initialize the database, follow these steps:

1. **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/recommender_system.git
    cd recommender_system
    ```

2. **Install Dependencies**
    Make sure you have Python 3.8+ installed. Then, install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure Environment Variables**
    Set up your environment variables (such as database connection strings) as needed. You can create a `.env` file in the project root:
    ```
    DATABASE_URL=your_postgres_connection_string
    ```

4. **Run the Database Loader**
    Execute the following command to run the initial database setup:
    ```bash
    python src/load_database.py
    ```

This will populate your PostgreSQL database with the necessary tables and initial data.