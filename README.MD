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