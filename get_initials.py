import base64

# --- FILL THESE IN FROM YOUR DEV CONSOLES ---
FITBIT_CLIENT_ID = "23VF5V"
STRAVA_CLIENT_ID = "224384"
REDIRECT_URI = "http://localhost:8000" # Or whatever you set in their dev portals

def generate_links():
    # Fitbit Link (Needs 'activity' scope for swimming)
    fitbit_url = (
        f"https://www.fitbit.com/oauth2/authorize?response_type=code"
        f"&client_id={FITBIT_CLIENT_ID}&redirect_uri={REDIRECT_URI}"
        f"&scope=activity%20heartrate%20location%20profile&expires_in=604800"
    )

    # Strava Link (Needs 'activity:write' to post your swims)
    strava_url = (
        f"https://www.strava.com/oauth/authorize?client_id={STRAVA_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&response_type=code&scope=activity:write,activity:read"
    )

    print(f"🔗 Click this for Fitbit:\n{fitbit_url}\n")
    print(f"🔗 Click this for Strava:\n{strava_url}")

if __name__ == "__main__":
    generate_links()
