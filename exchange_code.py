import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

FITBIT_CLIENT_ID = os.environ.get("FITBIT_CLIENT_ID")
FITBIT_CLIENT_SECRET = os.environ.get("FITBIT_CLIENT_SECRET")
FITBIT_AUTH_CODE = os.environ.get("FITBIT_AUTH_CODE")

STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
STRAVA_AUTH_CODE = os.environ.get("STRAVA_AUTH_CODE")


REDIRECT_URI = "http://localhost:8000"

def get_fitbit_tokens():
    if not FITBIT_AUTH_CODE:
        return
        
    url = "https://api.fitbit.com/oauth2/token"
    data = {
        "client_id": FITBIT_CLIENT_ID,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": FITBIT_AUTH_CODE,
    }

    print("\n--- Exchanging Fitbit code for tokens... ---")
    response = requests.post(url, data=data, auth=(FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET))
    
    if response.ok:
        print("FITBIT SUCCESS! Here is your payload:\n")
        print(json.dumps(response.json(), indent=2))
        print("\n>>> COPY the 'refresh_token' from above and paste it into the fitbit_refresh_token column in Supabase! <<<")
    else:
        print(f"Fitbit Error ({response.status_code}): {response.text}")

def get_strava_tokens():
    if not STRAVA_AUTH_CODE:
        return
        
    url = "https://www.strava.com/api/v3/oauth/token"
    data = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": STRAVA_AUTH_CODE,
    }

    print("\n--- Exchanging Strava code for tokens... ---")
    response = requests.post(url, data=data)
    
    if response.ok:
        print("STRAVA SUCCESS! Here is your payload:\n")
        print(json.dumps(response.json(), indent=2))
        print("\n>>> COPY the 'refresh_token' from above and paste it into the strava_refresh_token column in Supabase! <<<")
    else:
        print(f"Strava Error ({response.status_code}): {response.text}")

if __name__ == "__main__":
    get_fitbit_tokens()
    get_strava_tokens()
    
    if not FITBIT_AUTH_CODE and not STRAVA_AUTH_CODE:
        print("Please fill in either FITBIT_AUTH_CODE or STRAVA_AUTH_CODE to get your tokens!")

