# Fitbit to Strava Swim Sync (swsync)

## Why this project exists

If you track your workouts with a Fitbit device (like the Google Pixel Watch 2) and use Strava to log your fitness journey, you've likely encountered a frustrating limitation: **Fitbit's native integration with Strava does not sync swimming activities.**

While runs and bike rides sync over to Strava seamlessly, swims tracked on your watch remain trapped in the Fitbit ecosystem. This project bridges that gap by acting as a fully automated, background synchronization service specifically for swimming.

## Features

- **Automated Syncing:** Designed to run automatically on a schedule via GitHub Actions, meaning you don't have to lift a finger once it's set up.
- **Smart Naming:** Automatically names your Strava activities based on the time of day (e.g., "Morning Pool Swim", "Evening Pool Swim") to match Strava's natural conventions.
- **Proper Formatting:** Converts Fitbit's duration and distance formats into Strava's expected metrics.
- **Device Attribution:** Tags the activities as originating from the "Google Pixel Watch 2" in the Strava description.
- **State Management:** Uses Supabase as a lightweight database to securely store OAuth refresh tokens and keep track of the `last_sync_date`, ensuring no duplicate swims are uploaded.
- **Sync Audit Log:** Every successful sync is recorded in a `sync_log` table (Fitbit log ID → Strava activity ID), providing a full history and preventing duplicate uploads even if the script runs multiple times.

## How it works

1. **Authentication:** The script uses OAuth 2.0 to authenticate with both the Fitbit API and the Strava API.
2. **Fetch:** It queries the Fitbit API for any new activities logged since the last successful sync.
3. **Filter:** It isolates activities that are specifically categorized as swimming.
4. **Transform & Push:** It formats the swim data (distance, elapsed time, start time) into a payload and sends a `POST` request to Strava to create the new activity.
5. **Update State:** It saves the new refresh tokens and updates the `last_sync_date` in Supabase for the next run.

## Project Structure

- `sync_script.py`: The core automation script that performs the fetching, transforming, and pushing of data.
- `exchange_code.py`: A helper script used during initial setup to exchange OAuth authorization codes for long-lived access and refresh tokens.
- `get_initials.py`: A helper script used to generate the initial OAuth authorization URLs for both Fitbit and Strava.
- `.github/workflows/sync_swims.yaml`: The GitHub Actions workflow file that runs the script on a schedule.

## Setup & Configuration

This project requires a few external dependencies to function:
1. A **Fitbit Developer Application** (to get a Client ID and Secret).
2. A **Strava Developer Application** (to get a Client ID and Secret).
3. A **Supabase Project** (with a single table `auth_tokens` to store your `last_sync_date` and `refresh_token`s).
4. Environment variables managed either via a `.env` file locally or GitHub Secrets for the automated pipeline.
