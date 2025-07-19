import pandas as pd
import requests
import time




def get_all_games():

    """Fetch all app IDs and names from Steam API"""

    req = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")
    data = req.json()
    apps_data = data['applist']['apps']
    apps_ids = []
    app_names = []

    for app in apps_data:
        appid = app['appid']
        name = app['name']
        
        # skip apps that have empty name
        if not name:
            continue

        apps_ids.append(appid)
        app_names.append(name)

    return pd.DataFrame({
        'appid': apps_ids,
        'name': app_names
    })

def get_game_data(game_df, n_games=2000):
    """
    Fetch detailed game data from Steam API and return as DataFrame
    
    Args:
        game_df: DataFrame containing appid and name columns
        n_games: Number of games to process (default: 2000)
    
    Returns:
        pd.DataFrame: DataFrame containing detailed game information
    """
    game_data_list = []
    
    # looping through id's of n_games and calling api for each
    for i in range(0, min(n_games, len(game_df))):
        appid = game_df['appid'].iloc[i]
        game_name = game_df['name'].iloc[i]
        
        try:
            appdetails_req = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}")

            # if the game exists should get a response with status code 200
            if appdetails_req.status_code == 200:
                appdetails = appdetails_req.json()
                app_data = appdetails[str(appid)]
                
                # Check if the API call was successful
                if app_data.get('success', False) and 'data' in app_data:
                    game_info = app_data['data']
                    
                    # Extract relevant information and add to list
                    game_record = {
                        'appid': appid,
                        'name': game_info.get('name', game_name),
                        'type': game_info.get('type', ''),
                        'is_free': game_info.get('is_free', False),
                        'short_description': game_info.get('short_description', ''),
                        'detailed_description': game_info.get('detailed_description', ''),
                        'developers': ', '.join(game_info.get('developers', [])),
                        'publishers': ', '.join(game_info.get('publishers', [])),
                        'price': game_info.get('price_overview', {}).get('final_formatted', 'Free') if game_info.get('price_overview') else 'Free',
                        'genres': ', '.join([genre['description'] for genre in game_info.get('genres', [])]),
                        'categories': ', '.join([cat['description'] for cat in game_info.get('categories', [])]),
                        'release_date': game_info.get('release_date', {}).get('date', ''),
                        'platforms': str(game_info.get('platforms', {})),
                        'metacritic_score': game_info.get('metacritic', {}).get('score', None) if game_info.get('metacritic') else None,
                        'recommendations': game_info.get('recommendations', {}).get('total', None) if game_info.get('recommendations') else None
                    }
                    
                    game_data_list.append(game_record)
                    print(f"Successfully processed game {i+1}/{n_games}: {game_info.get('name', game_name)}")
                
                else:
                    print(f"Failed to get data for app {appid}: {game_name}")
                    
            # if we've sent too many requests, we get a 429 or 403 status code - wait 5 minutes
            elif appdetails_req.status_code in [403, 429]:
                print(f'Rate limited (status {appdetails_req.status_code}). App ID {appid}. Sleep for 5 min.')
                time.sleep(5 * 60)
                continue
                
            else:
                print(f"Unexpected status code {appdetails_req.status_code} for app {appid}")
                
        except Exception as e:
            print(f"Error processing app {appid}: {str(e)}")
            continue
        
        # Add a small delay to be respectful to the API
        time.sleep(0.5)
    
    # Convert list to DataFrame
    if game_data_list:
        games_df = pd.DataFrame(game_data_list)
        print(f"\nSuccessfully processed {len(games_df)} games out of {n_games} requested.")
        return games_df
    else:
        print("No game data was successfully retrieved.")
        return pd.DataFrame()
    
def pivot_tags(df):
    """
        Pivot the dataframe so each appid-category pair is a separate row.

        Args:
            df (pd.DataFrame): DataFrame with at least 'appid' and 'categories' columns.
                               The 'categories' column should be a comma-separated string.

        Returns:
            pd.DataFrame: DataFrame with columns 'appid' and 'category', one row per appid-category pair.
    """
    # Ensure categories column is a list (if it's a comma-separated string, split it)
    def parse_categories(categories):
        if isinstance(categories, list):
            return categories
        elif isinstance(categories, str):
            return [c.strip() for c in categories.split(',') if c.strip()]
        else:
            return []

    df = df[['appid', 'categories']].copy()
    df['categories'] = df['categories'].apply(parse_categories)
    pivoted = df.explode('categories').rename(columns={'categories': 'category'})
    pivoted = pivoted.dropna(subset=['category'])
    pivoted = pivoted[pivoted['category'] != '']
    return pivoted.reset_index(drop=True)

# calling methods
game_df = get_all_games()
game_info_df = get_game_data(game_df, n_games = 10)

# writing to csv
game_info_df.to_csv("Data/steam_games.csv", index=False)

# generating tags dataframe
game_tags_df = pivot_tags(game_info_df)
game_tags_df.to_csv("Data/steam_game_tags.csv", index=False)
