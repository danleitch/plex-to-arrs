import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys from environment variables
PLEX_TOKEN = os.getenv("PLEX_TOKEN")
RADARR_API_KEY = os.getenv("RADARR_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


RADARR_URL = "https://movies.niftytv.xyz/api/v3"
RADARR_ROOT_FOLDER = "/media/Downloads/upload-folder/Movies2"


def get_quality_profile_id():
    radarr_url = "https://movies.niftytv.xyz/api/v3"
    quality_profiles_url = f"{radarr_url}/qualityProfile?apikey={RADARR_API_KEY}"
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
    return root.findall('Video')


def fetch_tmdb_id(title):
    print("Fetching TMDB ID...")
    TMDB_SEARCH_URL = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    response = requests.get(TMDB_SEARCH_URL)
    if response.status_code == 200:
        results = response.json().get('results')
        if results:
            # Assuming the first result is the most relevant one
            return results[0]['id']
        else:
            print(f"No TMDB id found for {title}")
            return None
    else:
        print(f"Failed to retrieve TMDB ID for {title}")
        return None


def add_to_radarr(tmdb_id, title):
    print(f"Adding {title} to Radarr...")
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
        print(f"Added {title} to Radarr successfully.")
    else:
        try:
            error_message = response.json()[0]['errorMessage']
            print(f"Failed to add {title} to Radarr. Error: {error_message}")
        except (KeyError, IndexError):
            print(f"Failed to add {title} to Radarr. Status Code: {response.status_code}")
    print("Response Content:")
    print(response.content.decode())




def main():
    print("Starting script...")
    watchlist = fetch_plex_watchlist()
    print(f"Found {len(watchlist)} items in Plex watchlist")
    print("Processing Plex watchlist...")
    for video in watchlist:
        title = video.get('title')
        publicPagesURL = video.get('publicPagesURL')
        if publicPagesURL:
            tmdb_id = fetch_tmdb_id(title)
            if tmdb_id is not None:
                add_to_radarr(tmdb_id, title)
        else:
            print(f"No 'publicPagesURL' found for {title}")


if __name__ == "__main__":
    main()
