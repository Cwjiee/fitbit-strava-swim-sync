from datetime import datetime, timezone

start_time_str = "2026-04-26T12:00:00.000-07:00"
last_sync_date_str = "2026-04-23T00:00:00Z"

start_dt = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
last_sync_dt = datetime.fromisoformat(last_sync_date_str.replace("Z", "+00:00"))

if start_dt.tzinfo is None:
    start_dt = start_dt.replace(tzinfo=timezone.utc)
if last_sync_dt.tzinfo is None:
    last_sync_dt = last_sync_dt.replace(tzinfo=timezone.utc)

print(start_dt > last_sync_dt)
