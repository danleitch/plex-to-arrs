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

RADARR_URL = "https://movies.niftytv.xyz/api/v3"
SONARR_URL = "https://tv.niftytv.xyz/api/v3"
RADARR_ROOT_FOLDER = "/media/Downloads/upload-folder/Movies2"
SONARR_ROOT_FOLDER = "/media/Downloads/upload-folder/TVShows"

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
    print(f"Fetching TMDB ID for {media_type} '{title}'...")
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
    print("Request Payload:")
    print(payload)
    response = requests.post(radarr_add_url, json=payload)
    if response.status_code == 201:
        print(f"Added movie '{title}' to Radarr successfully.")
    else:
        try:
            error_message = response.json()[0]['errorMessage']
            print(f"Failed to add movie '{title}' to Radarr. Error: {error_message}")
        except (KeyError, IndexError):
            print(f"Failed to add movie '{title}' to Radarr. Status Code: {response.status_code}")

def add_to_sonarr(tmdb_id, title):
    print(f"Adding show '{title}' to Sonarr...")
    payload = {
        "title": title,
        "qualityProfileId": int(QUALITY_PROFILE),
        "languageProfileId": int(LANGUAGE_PROFILE),  # Include the language profile ID
        "tvdbId": tmdb_id,
        "rootFolderPath": SONARR_ROOT_FOLDER,
        "monitored": True,
        "addOptions": {
            "searchForMissingEpisodes": True
        }
    }
    sonarr_add_url = f"{SONARR_URL}/series?apikey={SONARR_API_KEY}"
    print("Request Payload:")
    print(payload)
    response = requests.post(sonarr_add_url, json=payload)
    if response.status_code == 201:
        print(f"Added show '{title}' to Sonarr successfully.")
    else:
        try:
            error_message = response.json()[0]['errorMessage']
            print(f"Failed to add show '{title}' to Sonarr. Error: {error_message}")
        except (KeyError, IndexError):
            print(f"Failed to add show '{title}' to Sonarr. Status Code: {response.status_code}")

def main():
    print("Starting script...")
    watchlist = fetch_plex_watchlist()
    print(f"Found {len(watchlist)} items in Plex watchlist")
    print("Processing Plex watchlist...")
    for item in watchlist:
        title = item.get('title')
        media_type = item.get('type')
        # if media_type == "show":
            # tmdb_id = fetch_tmdb_id(title, media_type)
            # if tmdb_id is not None:
            #     add_to_sonarr(tmdb_id, title)
        if media_type == "movie":
            tmdb_id = fetch_tmdb_id(title, media_type)
            if tmdb_id is not None:
                add_to_radarr(tmdb_id, title)
        else:
            print(f"Unknown media type found: {media_type}")

if __name__ == "__main__":
    main()
