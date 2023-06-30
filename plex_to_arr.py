import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys from environment variables
PLEX_TOKEN = os.getenv("PLEX_TOKEN")
RADARR_API_KEY = os.getenv("RADARR_API_KEY")
SONARR_API_KEY = os.getenv("SONARR_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

RADARR_URL = "http://192.168.1.15:7878/api/v3"
SONARR_URL = "http://192.168.1.15:8989/api/v3"
RADARR_ROOT_FOLDER = "/config"
SONARR_ROOT_FOLDER = "/config"

# Language Profile ID for Sonarr
LANGUAGE_PROFILE = 1  # Adjust this value based on your Sonarr configuration




def get_quality_profile_id():
    quality_profiles_url = f"{RADARR_URL}/qualityProfile?apikey={RADARR_API_KEY}"
    response = requests.get(quality_profiles_url)
    if response.status_code == 200:
        quality_profiles = response.json()
        for profile in quality_profiles:
            if profile["name"] == "HD-1080p":
                return profile["id"]
    else:
        print(f"Failed to retrieve quality profiles. Status Code: {response.status_code}")
    return None

QUALITY_PROFILE = get_quality_profile_id()

def fetch_plex_watchlist():
    print("Fetching Plex watchlist...")
    plex_url = f"https://metadata.provider.plex.tv/library/sections/watchlist/all?X-Plex-Token={PLEX_TOKEN}"
    response = requests.get(plex_url)
    root = ET.fromstring(response.content)
    return root.findall('Directory') + root.findall('Video')

def fetch_tmdb_id(title, media_type):
    if media_type == "show":
        search_url = f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_API_KEY}&query={title}"
    else:
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    response = requests.get(search_url)
    if response.status_code == 200:
        results = response.json().get('results')
        if results:
            # Assuming the first result is the most relevant one
            return results[0]['id']
        else:
            print(f"No TMDB ID found for {media_type} '{title}'")
            return None
    else:
        print(f"Failed to retrieve TMDB ID for {media_type} '{title}'")
        return None

def add_to_radarr(tmdb_id, title):
    print(f"Adding movie '{title}' to Radarr...")
    payload = {
        "title": title,
        "qualityProfileId": int(QUALITY_PROFILE),
        "tmdbId": tmdb_id,
        "rootFolderPath": RADARR_ROOT_FOLDER,
        "monitored": True,
        "addOptions": {
            "searchForMovie": True
        }
    }
    radarr_add_url = f"{RADARR_URL}/movie?apikey={RADARR_API_KEY}"
    response = requests.post(radarr_add_url, json=payload)
    if response.status_code == 201:
        print(f"Added movie '{title}' to Radarr successfully.")
    else:
        try:
            error_message = response.json()[0]['errorMessage']
            print(f"Failed to add movie '{title}' to Radarr. Error: {error_message}")
        except (KeyError, IndexError):
            print(f"Failed to add movie '{title}' to Radarr. Status Code: {response.status_code}")

def search_and_add_series(search_term):
    search_url = f"{SONARR_URL}/series/lookup"
    headers = {"X-Api-Key": SONARR_API_KEY}
    params = {"term": search_term}
    
    response = requests.get(search_url, headers=headers, params=params)
    if response.status_code == 200:
        results = response.json()
        if results:
            series = results[0]  # Assuming the first search result is the desired series
            series_id = series["tvdbId"]
            add_series_url = f"{SONARR_URL}/series"
            payload = {
            "title": search_term,
            "qualityProfileId": int(QUALITY_PROFILE),
            "languageProfileId": int(LANGUAGE_PROFILE),  
            "tvdbId": series_id,
            "rootFolderPath": SONARR_ROOT_FOLDER,
            "monitored": True,
            "addOptions": {
                "searchForMissingEpisodes": True
            }
        }
            
            response = requests.post(add_series_url, headers=headers, json=payload)
            if response.status_code == 201:
                print(f"Added series '{series['title']}' to Sonarr successfully.")
            else:
                print(f"Failed to add series '{series['title']}' to Sonarr. ")
        else:
            print("No series found for the search term.")
    else:
        print("Failed to perform series search.")


def main():
    print("Starting script...")
    watchlist = fetch_plex_watchlist()
    print(f"Found {len(watchlist)} items in Plex watchlist")
    print("Processing Plex watchlist...")
    for item in watchlist:
        title = item.get('title')
        media_type = item.get('type')
        if media_type == "movie":
            tmdb_id = fetch_tmdb_id(title, media_type)
            if tmdb_id is not None:
                add_to_radarr(tmdb_id, title)
        elif media_type == "show":
            tmdb_id = fetch_tmdb_id(title, media_type)
            if tmdb_id is not None:
                search_and_add_series(title)
        else:
            print(f"Unknown media type found: {media_type}")

if __name__ == "__main__":
    main()
