import os
import requests
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
GENIUS_ACCESS_TOKEN = os.getenv("GENIUS_ACCESS_TOKEN")

BASE_URL = "https://api.genius.com"

# Function to search for an artist and return their ID
def get_artist_id(artist_name):
    headers = {"Authorization": f"Bearer {GENIUS_ACCESS_TOKEN}"}
    search_url = f"{BASE_URL}/search"
    params = {"q": artist_name}
    response = requests.get(search_url, headers=headers, params=params)

    if response.status_code != 200:
        print("❌ Error fetching artist information")
        return None

    results = response.json().get("response", {}).get("hits", [])
    for result in results:
        if result["result"]["primary_artist"]["name"].lower() == artist_name.lower():
            return result["result"]["primary_artist"]["id"]

    print("❌ Artist not found")
    return None

# Fetch Creed's artist ID
creed_id = get_artist_id("Creed")
print(f"Creed's Artist ID: {creed_id}")
