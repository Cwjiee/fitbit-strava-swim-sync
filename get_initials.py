import os
import base64
from dotenv import load_dotenv

load_dotenv()

FITBIT_CLIENT_ID = os.environ.get("FITBIT_CLIENT_ID")
STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")

REDIRECT_URI = "http://localhost:8000"

def generate_links():
    fitbit_url = (
        f"https://www.fitbit.com/oauth2/authorize?response_type=code"
        f"&client_id={FITBIT_CLIENT_ID}&redirect_uri={REDIRECT_URI}"
        f"&scope=activity%20heartrate%20location%20profile&expires_in=604800"
    )

    strava_url = (
        f"https://www.strava.com/oauth/authorize?client_id={STRAVA_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&response_type=code&scope=activity:write,activity:read"
    )

    print(f"Click this for Fitbit:\n{fitbit_url}\n")
    print(f"Click this for Strava:\n{strava_url}")

if __name__ == "__main__":
    generate_links()
