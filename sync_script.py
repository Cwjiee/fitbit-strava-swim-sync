import os
import requests
from supabase import create_client
from datetime import datetime, timedelta, timezone

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
    response = requests.post(url, data=data, auth=(FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET))
    
    if not response.ok:
        raise Exception(f"Fitbit API Error ({response.status_code}): {response.text}")
        
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
    
    if not response.ok:
        raise Exception(f"Strava API Error ({response.status_code}): {response.text}")
        
    return response.json()

def get_fitbit_swims(access_token, last_sync_date_str):
    url = "https://api.fitbit.com/1/user/-/activities/list.json"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    if last_sync_date_str:
        after_date = last_sync_date_str.split("T")[0]
    else:
        # Default to yesterday if no sync date exists
        after_date = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
        last_sync_date_str = (datetime.utcnow() - timedelta(days=1)).isoformat()
        
    params = {
        "afterDate": after_date,
        "sort": "asc",
        "limit": 100,
        "offset": 0
    }
    
    response = requests.get(url, headers=headers, params=params)
    if not response.ok:
        print(f"Fitbit Fetch Error: {response.text}")
        return []
        
    data = response.json()
    activities = data.get("activities", [])
    print(activities)
    
    swims_to_sync = []
    for activity in activities:
        # is_swim = activity.get("activityName", "").lower() == "swim" or activity.get("activityTypeId") == 90024
        is_swim = "swim" in activity.get("activityName", "").lower() or activity.get("activityTypeId") == 90024
        if not is_swim:
            continue
            
        start_time_str = activity.get("startTime")
        
        try:
            start_dt = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            last_sync_dt = datetime.fromisoformat(last_sync_date_str.replace("Z", "+00:00"))
            
            if start_dt.tzinfo is None:
                start_dt = start_dt.replace(tzinfo=timezone.utc)
            if last_sync_dt.tzinfo is None:
                last_sync_dt = last_sync_dt.replace(tzinfo=timezone.utc)
                
            if start_dt > last_sync_dt:
                swims_to_sync.append(activity)
        except Exception:
            if start_time_str > last_sync_date_str:
                swims_to_sync.append(activity)

    return swims_to_sync

def is_already_synced(fitbit_log_id):
    res = supabase.table("sync_log").select("id").eq("fitbit_log_id", fitbit_log_id).execute()
    return len(res.data) > 0

def log_sync(fitbit_log_id, strava_activity_id, activity_name, start_time, distance_meters, elapsed_time):
    supabase.table("sync_log").insert({
        "fitbit_log_id": fitbit_log_id,
        "strava_activity_id": strava_activity_id,
        "activity_name": activity_name,
        "start_time": start_time,
        "distance_meters": round(distance_meters, 2),
        "elapsed_seconds": elapsed_time,
    }).execute()

def post_strava_activity(access_token, swim_data):
    url = "https://www.strava.com/api/v3/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    duration_ms = swim_data.get("duration", 0)
    elapsed_time = duration_ms // 1000
    
    distance = swim_data.get("distance", 0)
    distance_unit = swim_data.get("distanceUnit", "Kilometer")
    if distance_unit.lower() in ["kilometer", "kilometers", "km"]:
        distance_meters = distance * 1000
    elif distance_unit.lower() in ["mile", "miles", "mi"]:
        distance_meters = distance * 1609.34
    else:
        distance_meters = distance * 1000

    # midnight-6 am: night 6am - 12pm: morning 12pm-2pm: lunch 2pm - 6pm : afternoon 6pm-midnight: evening 
    # https://www.reddit.com/r/Strava/comments/1dmju1z/what_is_stravas_definition_of_time/

    date_str = swim_data.get("startTime")
    dt = datetime.fromisoformat(date_str)
    hour = dt.hour

    if 0 <= hour < 6:
        time_of_day = "night"
    elif 6 <= hour < 12:
        time_of_day = "morning"
    elif 12 <= hour < 14:
        time_of_day = "lunch"
    elif 14 <= hour < 18:
        time_of_day = "afternoon"
    else:
        time_of_day = "evening"

    activity_name = f"{time_of_day.capitalize()} Swim"

    payload = {
        "name": activity_name,
        "type": "Swim",
        "start_date_local": swim_data.get("startTime"),
        "elapsed_time": elapsed_time,
        "description": "Google Pixel Watch 2",
        "distance": distance_meters
    }
    
    response = requests.post(url, headers=headers, data=payload)
    if not response.ok:
        print(f"Strava Post Error: {response.text}")
        return None
    
    strava_data = response.json()
    return {
        "strava_id": strava_data.get("id"),
        "activity_name": activity_name,
        "distance_meters": distance_meters,
        "elapsed_time": elapsed_time
    }

def main():
    res = supabase.table("auth_tokens").select("*").eq("id", 1).single().execute()
    tokens = res.data

    new_fb = refresh_fitbit(tokens['fitbit_refresh_token'])
    print(new_fb)
    new_st = refresh_strava(tokens['strava_refresh_token'])
    print(new_st)

    last_sync_date = tokens.get('last_sync_date')
    swims = get_fitbit_swims(new_fb['access_token'], last_sync_date)
    
    print(f"Found {len(swims)} new swims to sync.")
    
    latest_sync_date_str = last_sync_date
    for swim in swims:
        fitbit_log_id = str(swim.get('logId'))
        
        if is_already_synced(fitbit_log_id):
            print(f"Skipping swim {fitbit_log_id} from {swim.get('startTime')} — already synced.")
            continue
        
        print(f"Syncing swim from {swim.get('startTime')}...")
        result = post_strava_activity(new_st['access_token'], swim)
        if result:
            print(f"Successfully posted to Strava! (ID: {result['strava_id']})")
            
            log_sync(
                fitbit_log_id=fitbit_log_id,
                strava_activity_id=str(result['strava_id']),
                activity_name=result['activity_name'],
                start_time=swim.get('startTime'),
                distance_meters=result['distance_meters'],
                elapsed_time=result['elapsed_time']
            )
            
            swim_start_str = swim.get('startTime')
            if latest_sync_date_str is None or swim_start_str > latest_sync_date_str:
                latest_sync_date_str = swim_start_str
        else:
            print("Failed to post to Strava.")

    update_data = {
        "fitbit_refresh_token": new_fb['refresh_token'],
        "strava_refresh_token": new_st['refresh_token'],
        "updated_at": "now()"
    }
    if latest_sync_date_str:
        update_data["last_sync_date"] = latest_sync_date_str

    supabase.table("auth_tokens").update(update_data).eq("id", 1).execute()

    print("Tokens and activities synced successfully! 🏊‍♂️")

if __name__ == "__main__":
    main()
