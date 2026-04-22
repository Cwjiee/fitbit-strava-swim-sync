import os
import requests
from supabase import create_client

# Load credentials from GitHub Secrets
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_KEY")
FITBIT_CLIENT_ID = os.environ.get("FITBIT_CLIENT_ID")
FITBIT_CLIENT_SECRET = os.environ.get("FITBIT_CLIENT_SECRET")
STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")

supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)

def refresh_fitbit(old_token):
    url = "https://api.fitbit.com/oauth2/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": old_token,
        "client_id": FITBIT_CLIENT_ID
    }
    # Fitbit requires Basic Auth header (Client_ID:Client_Secret in Base64) 
    # or sending them in the body depending on your app type.
    response = requests.post(url, data=data, auth=(FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET))
    return response.json()

def refresh_strava(old_token):
    url = "https://www.strava.com/api/v3/oauth/token"
    data = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": old_token
    }
    response = requests.post(url, data=data)
    return response.json()

def main():
    # 1. Fetch current refresh tokens from Supabase
    res = supabase.table("auth_tokens").select("*").eq("id", 1).single().execute()
    tokens = res.data

    # 2. Get new tokens from Fitbit & Strava
    new_fb = refresh_fitbit(tokens['fitbit_refresh_token'])
    new_st = refresh_strava(tokens['strava_refresh_token'])

    # 3. Update Supabase with the brand new Refresh Tokens
    supabase.table("auth_tokens").update({
        "fitbit_refresh_token": new_fb['refresh_token'],
        "strava_refresh_token": new_st['refresh_token'],
        "updated_at": "now()"
    }).eq("id", 1).execute()

    print("Tokens rotated successfully! 🏊‍♂️")
    
    # 4. NOW use new_fb['access_token'] to fetch your swim data...
    # and use new_st['access_token'] to post it to Strava.

if __name__ == "__main__":
    main()
