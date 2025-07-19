import pandas as pd
import requests




def get_all_app_id():

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

test_df = get_all_app_id()
print(test_df.head(10))